"""
(SQx) mixer dashboard screen application.

Behavior:
 - MIDI: quarter-frame MTC decoding — sets timecode and framerate from MTC (unchanged).
 - OSC: accepts timecode inputs but does NOT set framerate. OSC-to-frame conversion uses
        MIDI framerate if available else OSC_FRAMERATE_FALLBACK. Short single-frame blips
        like 00.00.00.00 -> 00.00.01.00 are suppressed briefly to avoid visible flashes.
 - Device row: up to 2 EW-DX EM2 wireless-mic channels (extensible to 4) and up to
        4 IEM G4 channels, shown as WSM/Wireless-Workbench-style channel strips
        between the timecode display and the companion web view. See
        device_network.py for the (best-effort / simulate-by-default) network layer.
"""

import signal
import sys
import threading
import time
import re
import os
import configparser

import mido

# from PySide6.QtCore import Qt
from PySide6.QtCore import QTime, QTimer, QUrl, Slot, Signal, QObject
from PySide6.QtCore import QCommandLineOption, QCommandLineParser, QSysInfo
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow

# from PySide6.QtWebEngineWidgets import QWebEngineView

from pythonosc import dispatcher as osc_dispatcher
from pythonosc import osc_server

from assets.mainwindow import Ui_MainWindow
from preferences import PreferencesPanel
from device_widgets import DeviceRow

signal.signal(signal.SIGINT, signal.SIG_DFL)

APP_VERSION = "0.13"
has_fullscreen_option = False

# Vertical geometry for the dynamic groupDevices / webView split. groupDevices
# always starts right after the Timecode box; its height (and therefore
# webView's y/height) is recomputed whenever the device grid gains or loses a
# row -- see MainWindow._apply_device_row_geometry().
GROUP_DEVICES_Y = 285
WEBVIEW_GAP = 5            # gap between groupDevices and the web view
WEBVIEW_BOTTOM_MARGIN = 5  # gap between the web view and the window's bottom edge
WINDOW_HEIGHT = 1480

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.ini")


class SettingsManager:
    """
    Minimal settings manager backed by settings.ini.

    Settings are organized by section. Legacy files may still have keys in the older [settings]
    section; these are migrated automatically.
    """
    def __init__(self, path=SETTINGS_FILE):
        self.path = path
        self.cfg = configparser.ConfigParser()
        self.cfg.optionxform = str                                                  # type: ignore
        self.defaults = {
            "timecode": {
                "TIMECODE_SOURCE": "midi",
                "MIDI_PORT_NAME": "",
                "OSC_LISTEN_HOST": "0.0.0.0",
                "OSC_LISTEN_PORT": "9001",
                "OSC_ADDRESS": "/timecode",
                "OSC_FRAMERATE_FALLBACK": "30",
                "TIMECODE_MIN_UPDATE_MS": "40",
                "TIMECODE_SUPPRESSION_MS": "300",
            },
            "companion": {
                "COMPANION_URL": "http://localhost:8080",
            },
            "network": {
                # Master switch for the whole IEM/Mic feature -- when false, no
                # clients are started regardless of individual slot enables, and
                # the group collapses to a one-line "disabled" message.
                "DEVICES_ENABLED": "true",
                # No real Sennheiser hardware is assumed present by default; flip this
                # off once IPs below point at real EW-DX EM2 / IEM G4 units. See
                # device_network.py for protocol notes/caveats.
                "SIMULATE_DEVICES": "true",
                "POLL_INTERVAL_MS": "1000",
            },
            # 4 IEM G4 slots (all enabled by default; disable unused ones in Preferences)
            "iem": {
                # Section-level (applies to every IEM slot), not per-slot:
                # Preferences -> IEM -> "Show AF level".
                "IEM_AF_ENABLED": "true",
                # No per-slot CHANNEL here -- an SR IEM G4 has no
                # channel-select concept (one physical unit is one channel),
                # unlike the mic side's EM2 (see [wireless_mics] below).
                "IEM1_ENABLED": "true",  "IEM1_NAME": "IEM 1", "IEM1_IP": "", "IEM1_PORT": "53212",
                "IEM2_ENABLED": "true",  "IEM2_NAME": "IEM 2", "IEM2_IP": "", "IEM2_PORT": "53212",
                "IEM3_ENABLED": "true",  "IEM3_NAME": "IEM 3", "IEM3_IP": "", "IEM3_PORT": "53212",
                "IEM4_ENABLED": "true",  "IEM4_NAME": "IEM 4", "IEM4_IP": "", "IEM4_PORT": "53212",
            },
            # 4 wireless-mic slots = up to 2x EW-DX EM2 (2 channels per unit).
            # Slots 1-2 (unit #1) enabled today; 3-4 (unit #2) ready for "the future".
            "wireless_mics": {
                "MIC1_ENABLED": "true",  "MIC1_NAME": "Mic 1", "MIC1_IP": "", "MIC1_PORT": "45", "MIC1_CHANNEL": "1",
                "MIC2_ENABLED": "true",  "MIC2_NAME": "Mic 2", "MIC2_IP": "", "MIC2_PORT": "45", "MIC2_CHANNEL": "2",
                "MIC3_ENABLED": "false", "MIC3_NAME": "Mic 3", "MIC3_IP": "", "MIC3_PORT": "45", "MIC3_CHANNEL": "1",
                "MIC4_ENABLED": "false", "MIC4_NAME": "Mic 4", "MIC4_IP": "", "MIC4_PORT": "45", "MIC4_CHANNEL": "2",
            },
        }
        self._ensure_loaded()

    def _ensure_loaded(self):
        if os.path.exists(self.path):
            self.cfg.read(self.path)

        for section in self.defaults.keys():
            if section not in self.cfg:
                self.cfg[section] = {}

        # legacy single-section config: [settings] -> [companion]
        if "settings" in self.cfg and "companion" in self.cfg:
            for key, value in self.cfg["settings"].items():
                if key.upper() == "COMPANION_URL" and "COMPANION_URL" not in self.cfg["companion"]:
                    self.cfg["companion"]["COMPANION_URL"] = value
        if "settings" in self.cfg:
            legacy_settings = self.cfg["settings"]
            if "COMPANION_URL" in legacy_settings and "COMPANION_URL" not in self.cfg["companion"]:
                self.cfg["companion"]["COMPANION_URL"] = legacy_settings["COMPANION_URL"]
            if "companion_url" in legacy_settings and "COMPANION_URL" not in self.cfg["companion"]:
                self.cfg["companion"]["COMPANION_URL"] = legacy_settings["companion_url"]
            if "COMPANION_URL" not in legacy_settings and "companion_url" not in legacy_settings:
                # no direct url; leave legacy section in place until rewritten explicitly
                pass

        # normalize keys for each section and populate defaults
        for section, section_defaults in self.defaults.items():
            sec = self.cfg[section]
            for key in list(sec.keys()):
                canonical = key.upper()
                if canonical != key:
                    if canonical not in sec:
                        sec[canonical] = sec[key]
                    del sec[key]
            for k, v in section_defaults.items():
                if k not in sec:
                    sec[k] = v

        # migrate old settings section out of the way
        if "settings" in self.cfg and not self.cfg["settings"]:
            del self.cfg["settings"]

    def get(self, key, default=None, cast=None, section="timecode"):
        section_name = section.lower()
        if section_name not in self.cfg:
            self.cfg[section_name] = {}
        val = self.cfg[section_name].get(key, self.defaults.get(section_name, {}).get(key, default))
        if val is None:
            return default
        if cast:
            try:
                return cast(val)
            except Exception:
                return default
        return val

    def set(self, key, value, section="timecode"):
        section_name = section.lower()
        if section_name not in self.cfg:
            self.cfg[section_name] = {}
        self.cfg[section_name][key] = str(value)

    def save(self):
        if "settings" in self.cfg:
            self.cfg.remove_section("settings")
        with open(self.path, "w") as fp:
            self.cfg.write(fp)


class TimecodeReader(QObject):
    timecode_changed = Signal(str)
    framerate_changed = Signal(str)

    def __init__(self, settings: SettingsManager):
        super().__init__()

        self.settings = settings

        # MTC nibble state
        self.nibbles = [0] * 8

        # time values
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.frames = 0

        # framerate state (string). MIDI will set this when receiving MTC.
        self.framerate = "?"  # "24","25","29.97","30","23.976", or "?"

        # runtime attributes for midi/osc
        self._midi_port = None  # mido input port object if open
        self._osc_server = None
        self._osc_thread = None

        # suppression config to avoid single-frame blips at zero (ms)
        self._suppression_timeout_ms = self.settings.get("TIMECODE_SUPPRESSION_MS", cast=int)
        self._suppress_pending = None  # dict with keys: 'tc','timer','ts'

        # debounce last emitted timecode
        self._last_tc = None
        self._last_emit_ts = 0.0

        # UI debounce
        self.min_update_ms = self.settings.get("TIMECODE_MIN_UPDATE_MS", cast=int)

        # Start based on settings
        self._apply_source_from_settings(initial=True)

    # ---------------- Settings reload / apply ----------------
    def reload_settings(self):
        # reload file then re-apply config values and restart/stop inputs as necessary
        self.settings._ensure_loaded()
        self._suppression_timeout_ms = self.settings.get("TIMECODE_SUPPRESSION_MS", cast=int)
        self.min_update_ms = self.settings.get("TIMECODE_MIN_UPDATE_MS", cast=int)
        self._apply_source_from_settings(initial=False)

    def _apply_source_from_settings(self, initial=False):
        source = (self.settings.get("TIMECODE_SOURCE") or "midi").lower()
        # Stop whatever is not requested; start what's requested
        if source == 'midi':
            if self._midi_port is None:
                try:
                    self.start_midi()
                except Exception as e:
                    print("MIDI: failed to start:", e)
        else:
            if self._midi_port is not None:
                self.stop_midi()

        if source == 'osc':
            if self._osc_server is None:
                try:
                    self.start_osc()
                except Exception as e:
                    print("OSC: failed to start:", e)
        else:
            if self._osc_server is not None:
                self.stop_osc()

        # update cached other settings
        try:
            self.osc_framerate_fallback = float(self.settings.get(                  # type: ignore
                "OSC_FRAMERATE_FALLBACK",
                cast=float))
        except Exception:
            self.osc_framerate_fallback = 30.0

    # ---------------- MIDI (MTC quarter-frame) ----------------
    def start_midi(self):
        input_names = mido.get_input_names()                                        # type: ignore
        if not input_names:
            print("MIDI: no input ports found")
            return

        midi_port_name_cfg = self.settings.get("MIDI_PORT_NAME", default="")
        port_name = None
        if midi_port_name_cfg:
            for ipn in input_names:
                if midi_port_name_cfg in ipn:
                    port_name = ipn
                    break
            if port_name is None:
                print(f"MIDI: port containing '{midi_port_name_cfg}' not found; using first port.")

        if port_name is None:
            port_name = input_names[0]

        print(f"MIDI: opening input {port_name}")
        # use mido callback style, it spawns a background thread inside python-rtmidi/portmidi
        # backend
        try:
            self._midi_port = mido.open_input(port_name,                            # type: ignore
                                              callback=self._midi_callback)
        except Exception as e:
            print("MIDI: input error:", e)
            self._midi_port = None

    def stop_midi(self):
        if self._midi_port is not None:
            try:
                self._midi_port.close()
            except Exception:
                pass
            self._midi_port = None
            print("MIDI: stopped")

    def _midi_callback(self, msg):
        try:
            if msg.type == "quarter_frame":
                frame_type = msg.frame_type
                frame_value = msg.frame_value
                if 0 <= frame_type < 8:
                    self.nibbles[frame_type] = frame_value
                    self._decode_timecode_from_nibbles()
        except Exception as e:
            print("MIDI: callback error:", e)

    def _decode_timecode_from_nibbles(self):
        frames = (self.nibbles[0] | (self.nibbles[1] << 4))
        seconds = (self.nibbles[2] | (self.nibbles[3] << 4))
        minutes = (self.nibbles[4] | (self.nibbles[5] << 4))
        hours = (self.nibbles[6] | ((self.nibbles[7] & 0x1) << 4))

        # SMPTE framerate decode from nibble 7 (authoritative)
        rate_bits = (self.nibbles[7] >> 1) & 0x3
        fr_map = {0: "24", 1: "25", 2: "29.97", 3: "30"}
        fr = fr_map.get(rate_bits, "?")
        if fr != self.framerate:
            self.framerate = fr
            self.framerate_changed.emit(fr)

        self._emit_timecode(hours, minutes, seconds, frames)

    # ---------------- OSC ----------------
    def start_osc(self):
        disp = osc_dispatcher.Dispatcher()
        disp.map(self.settings.get("OSC_ADDRESS", default="/timecode"),             # type: ignore
                 self._osc_message)
        disp.map("/*", self._osc_message)

        host = self.settings.get("OSC_LISTEN_HOST", default="0.0.0.0")
        port = int(self.settings.get("OSC_LISTEN_PORT", default="9001"))            # type: ignore
        try:
            self._osc_server = osc_server.ThreadingOSCUDPServer((host, port),       # type: ignore
                                                                disp)
        except Exception as e:
            print(f"OSC: failed to start on {host}:{port} -> {e}")
            self._osc_server = None
            return

        print(f"OSC: listening on {self._osc_server.server_address}, "
              f"address={self.settings.get('OSC_ADDRESS')}")
        self._osc_thread = threading.Thread(target=self._osc_server.serve_forever, daemon=True)
        self._osc_thread.start()

    def stop_osc(self):
        if self._osc_server:
            try:
                self._osc_server.shutdown()
            except Exception:
                pass
            try:
                self._osc_server.server_close()
            except Exception:
                pass
            self._osc_server = None
            print("OSC: stopped")

    def _osc_message(self, address, *args):
        """
        Accepts:
         - single string "HH:MM:SS:FF" or "HH.MM.SS.FF"
         - four numeric args: H M S F
         - single numeric arg: seconds (float) [we WILL NOT accept frames-per-second from OSC]
        NOTE: OSC-provided framerate values (if any) are ignored.
        """
        try:
            if not args:
                return

            # string form
            if len(args) == 1 and isinstance(args[0], str):
                s = args[0].strip()
                parts = re.split(r"[:\.]", s)
                if len(parts) == 4 and all(p.isdigit() for p in parts):
                    h, m, sec, f = [int(p) for p in parts]
                    self._osc_emit_timecode_with_suppression(h, m, sec, f)
                    return
                match = re.search(r"(\d{1,2})[:\.](\d{1,2})[:\.](\d{1,2})[:\.]?(\d{1,2})?", s)
                if match:
                    h = int(match.group(1))
                    m = int(match.group(2))
                    sec = int(match.group(3))
                    f = int(match.group(4) or 0)
                    self._osc_emit_timecode_with_suppression(h, m, sec, f)
                return

            # numeric args
            numeric_args = []
            for a in args:
                if isinstance(a, (int, float)):
                    numeric_args.append(a)
                else:
                    try:
                        numeric_args.append(float(a))
                    except Exception:
                        pass

            # h m s f
            if len(numeric_args) >= 4:
                h = int(numeric_args[0]) % 24
                m = int(numeric_args[1]) % 60
                sec = int(numeric_args[2]) % 60
                f = int(round(numeric_args[3]))
                # ignore any further numeric args (do not accept framerate)
                self._osc_emit_timecode_with_suppression(h, m, sec, f)
                return

            # single numeric -> seconds (float)
            if len(numeric_args) == 1:
                secs = float(numeric_args[0])
                # Use MIDI framerate if known (set by MTC). Otherwise use configured fallback.
                try:
                    fps = float(self.framerate) if self.framerate != "?" else float(
                        self.settings.get("OSC_FRAMERATE_FALLBACK", cast=float))    # type: ignore
                except Exception:
                    fps = float(self.settings.get("OSC_FRAMERATE_FALLBACK",         # type: ignore
                                                  default=30,
                                                  cast=float))
                total_seconds_int = int(secs)
                fractional = secs - total_seconds_int
                h = total_seconds_int // 3600
                m = (total_seconds_int % 3600) // 60
                sec = total_seconds_int % 60
                # floor/truncate AND clamp to avoid f==fps
                f = int(fractional * fps)
                if f >= fps:
                    f = int(fps) - 1 if fps >= 1 else 0
                self._osc_emit_timecode_with_suppression(h, m, sec, f)
                return

        except Exception as e:
            print("OSC: parsing error:", e)

    # ---------------- suppression helpers ----------------
    def _osc_emit_timecode_with_suppression(self, h, m, s, f):
        """
        Emits timecode for OSC input but applies suppression for the specific blip pattern:
        previous == 00.00.00.00 and new == 00.00.01.00 and emission would be within suppression
        window.
        """
        tc = f"{int(h):02d}.{int(m):02d}.{int(s):02d}.{int(f):02d}"
        now_ms = time.time() * 1000.0

        # If we have a pending suppress timer and a different (non-pending) message arrives,
        # cancel the pending suppressed emission and proceed to emit the new message (we prefer
        # latest).
        if self._suppress_pending:
            pending_timer = self._suppress_pending.get("timer")
            # cancel timer if pending exists because we will emit new now
            if pending_timer:
                try:
                    pending_timer.cancel()
                except Exception:
                    pass
            self._suppress_pending = None

        # Detect the specific blip: previous 00.00.00.00 -> new 00.00.01.00 shortly after
        if self._last_tc == "00.00.00.00" and tc == "00.00.01.00":
            # if last emission was recent, suppress briefly and wait for confirmation
            if (now_ms - self._last_emit_ts) < self._suppression_timeout_ms:        # type: ignore
                # schedule delayed emission of this tc unless another message cancels it
                timer = threading.Timer(self._suppression_timeout_ms / 1000.0,      # type: ignore
                                        self._release_suppressed, args=(tc,))
                self._suppress_pending = {"tc": tc, "timer": timer, "ts": now_ms}
                timer.daemon = True
                timer.start()
                return  # do not emit now

        # Otherwise, normal emit
        self._do_emit_timecode(tc, now_ms)

    def _release_suppressed(self, tc):
        """
        Called by timer if suppressed blip wasn't cancelled. Emit only if last_tc didn't change
        since suppression was scheduled (prevents reintroducing flashes).
        """
        now_ms = time.time() * 1000.0
        # if someone else already changed last_tc, skip emitting
        if self._last_tc != "00.00.00.00":
            self._suppress_pending = None
            return
        # emit the suppressed tc
        self._do_emit_timecode(tc, now_ms)
        self._suppress_pending = None

    def _do_emit_timecode(self, tc, now_ms=None):
        if now_ms is None:
            now_ms = time.time() * 1000.0
        if tc != self._last_tc:
            if (self.min_update_ms <= 0 or                                          # type: ignore
                    (now_ms - self._last_emit_ts) >= self.min_update_ms):           # type: ignore
                self._last_tc = tc
                self._last_emit_ts = now_ms
                self.timecode_changed.emit(tc)

    # ---------------- emit helpers ----------------
    def _emit_timecode(self, h, m, s, f):
        # Normalize using current framerate (MIDI if known) or fallback for seconds->frames only
        try:
            fr_numeric = float(self.framerate) if self.framerate != "?" else float(
                self.settings.get("OSC_FRAMERATE_FALLBACK", cast=float))            # type: ignore
        except Exception:
            fr_numeric = float(self.settings.get("OSC_FRAMERATE_FALLBACK",          # type: ignore
                                                 default=30,
                                                 cast=float))

        h = int(h) % 24
        m = int(m) % 60
        s = int(s) % 60
        f = int(f)
        if fr_numeric <= 0:
            fr_numeric = max(1.0, float(self.settings.get(                          # type: ignore
                "OSC_FRAMERATE_FALLBACK", default=30, cast=float)))

        # handle rollover if frame >= framerate (safety)
        if f >= fr_numeric:
            s += int(f // fr_numeric)
            f = int(f % fr_numeric)
        if s >= 60:
            m += s // 60
            s = s % 60
        if m >= 60:
            h += m // 60
            m = m % 60
        h = h % 24

        self.hours, self.minutes, self.seconds, self.frames = h, m, s, f
        tc = f"{h:02d}.{m:02d}.{s:02d}.{f:02d}"

        now_ms = time.time() * 1000.0
        # Use same suppression logic for direct emit path
        source = (self.settings.get("TIMECODE_SOURCE") or "midi").lower()
        if source in ("osc"):
            self._osc_emit_timecode_with_suppression(h, m, s, f)
        else:
            self._do_emit_timecode(tc, now_ms)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_time)
        self.timer.start(500)

        clock_palette = self._ui.lcdClock.palette()
        clock_palette.setColor(clock_palette.ColorRole.WindowText, QColor(0, 255, 160))
        self._ui.lcdClock.setPalette(clock_palette)
        timecode_palette = self._ui.lcdTimecode.palette()
        timecode_palette.setColor(timecode_palette.ColorRole.WindowText, QColor(255, 0, 0))
        self._ui.lcdTimecode.setPalette(timecode_palette)

        self.show_time()

        self._ui.lcdTimecode.display("00.00.00.00")

        # Settings manager
        self.settings = SettingsManager()

        # Timecode reader
        self.mtc_reader = TimecodeReader(self.settings)
        self.mtc_reader.timecode_changed.connect(self.update_timecode)
        self.mtc_reader.framerate_changed.connect(self.update_framerate)

        # IEM / wireless-mic device row (populates self._ui.deviceRowLayout).
        # Fills IEM 1-4 first, then Mic 1-4, into a 4-col x up-to-2-row grid.
        self.device_row = DeviceRow(self.settings, self._ui.deviceRowLayout, self._ui.deviceRowContents)
        self.device_row.layout_changed.connect(self._apply_device_row_geometry)
        # Apply sizing for the initial build (rebuild_from_settings() already
        # ran once inside DeviceRow.__init__, before the signal above was
        # connected, so size explicitly for that first pass here).
        self._apply_device_row_geometry(self.device_row.group_height)

        # WebView
        self._ui.webView.setUrl(QUrl(self.settings.get(                             # type: ignore
            "COMPANION_URL",
            default="http://localhost:8080",
            section="companion",
        )))

        # Embedded preferences panel for kiosk/touch operation
        self.preferences_panel = PreferencesPanel(self.settings, self._ui.centralwidget)
        self.preferences_panel.resize(300, 902)
        self.preferences_panel.move(10, 200)
        self.preferences_panel.hide()
        self.preferences_panel.settingsApplied.connect(self.on_settings_applied)

        # Preferences button
        try:
            self._ui.btnPreferences.clicked.connect(self.open_preferences)
        except Exception:
            pass  # in case UI not updated

        # fullscreen option parsed from command line
        if has_fullscreen_option:
            self.showFullScreen()

    @Slot()
    def show_time(self):
        t = QTime.currentTime()
        text = t.toString("hh:mm:ss")
        if t.msec() >= 500:
            text = text.replace(":", " ")
        self._ui.lcdClock.display(text)

    @Slot(str)
    def update_timecode(self, tc):
        self._ui.lcdTimecode.display(tc)

    @Slot(str)
    def update_framerate(self, fr):
        # reset styles
        self._ui.frate_24.setStyleSheet("""
            QLabel { background-color: #444; color: rgb(135, 135, 135); }
        """)
        self._ui.frate_25.setStyleSheet("""
            QLabel { background-color: #444; color: rgb(135, 135, 135); }
        """)
        self._ui.frate_29.setStyleSheet("""
            QLabel { background-color: #444; color: rgb(135, 135, 135); }
        """)
        self._ui.frate_30.setStyleSheet("""
            QLabel { background-color: #444; color: rgb(135, 135, 135); }
        """)
        # highlight
        if fr.startswith("29"):
            self._ui.frate_29.setStyleSheet("color: white;")
        elif fr == "24" or fr.startswith("24"):
            self._ui.frate_24.setStyleSheet("color: white;")
        elif fr == "25" or fr.startswith("25"):
            self._ui.frate_25.setStyleSheet("color: white;")
        elif fr == "30" or fr.startswith("30"):
            self._ui.frate_30.setStyleSheet("color: white;")

    def open_preferences(self):
        if self.preferences_panel.isVisible():
            self.preferences_panel.hide()
            return
        self.preferences_panel.raise_()
        self.preferences_panel.show()
        self.preferences_panel.activateWindow()

    @Slot()
    def on_settings_applied(self):
        """Preferences OK was pressed: re-apply timecode source + rebuild device row."""
        self.mtc_reader.reload_settings()
        self.device_row.rebuild_from_settings()
        # (device_row.rebuild_from_settings() emits layout_changed, which
        # _apply_device_row_geometry() below is connected to, so the
        # groupDevices/webView resize happens automatically.)

    @Slot(int)
    def _apply_device_row_geometry(self, group_h: int):
        """
        Grow/shrink groupDevices to `group_h` px (computed by DeviceRow from
        the actual per-row content heights -- rows aren't assumed uniform,
        since an IEM row can be shorter than a Mic row when IEM's AF display
        is switched off), and slide the web view down/up to start right
        below it, shrinking it by exactly the amount groupDevices grew (and
        vice versa).
        """
        self._ui.groupDevices.setGeometry(0, GROUP_DEVICES_Y, 320, group_h)

        scroll_h = group_h - 20  # 20px reserved for the QGroupBox title, per the .ui
        self._ui.scrollDevices.setGeometry(0, 20, 320, scroll_h)
        self._ui.deviceRowContents.resize(320, scroll_h)

        webview_y = GROUP_DEVICES_Y + group_h + WEBVIEW_GAP
        webview_h = max(100, WINDOW_HEIGHT - webview_y - WEBVIEW_BOTTOM_MARGIN)
        self._ui.webView.setGeometry(0, webview_y, 321, webview_h)


def parse(app):
    parser = QCommandLineParser()
    parser.addHelpOption()
    parser.addVersionOption()
    fullscreen_option = QCommandLineOption(["fullscreen"],
                                           "Start application fullscreen on startup.")
    parser.addOption(fullscreen_option)
    parser.process(app)

    global has_fullscreen_option
    has_fullscreen_option = parser.isSet(fullscreen_option)


if __name__ == "__main__":
    kernel = QSysInfo().kernelVersion()
    app = QApplication(sys.argv)
    app.setApplicationName("Mixer Dashboard")
    app.setApplicationVersion(APP_VERSION)
    # app.setOverrideCursor(Qt.BlankCursor)                                           # type: ignore
    parse(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
