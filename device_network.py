"""
device_network.py

Network layer for the Sennheiser device row: SR IEM G4 transmitters (our
"iem" slots) speak Sennheiser's Media Control Protocol (TI 1254 v1.0) over
UDP/53212; EW-DX EM 2 receivers (our "mic" slots) speak SSC (legacy,
unauthenticated) over UDP/45. Both client implementations below come
directly from a verified reference implementation rather than being
reverse-engineered here.

Two adapter classes (`G4IemChannelClient`, `SscMicChannelClient`) translate
each protocol's native data object into the `DeviceReading` shape
device_widgets.py already knows how to draw, so the widgets themselves
didn't need to change for this swap from the earlier placeholder TCP/JSON
client to these real UDP protocols.

EW-DX EM2 SSC paths used here -- confirmed against Sennheiser's official
"Sound Control Protocol, Developer's guide for EW-DX" (EW-DX EM 2 firmware
1.1.3), Publ. 03/2023, section 8 "SSC Method List (EW-DX EM 2)":

  /rx{1,2}/name                    8.62, 8.87
  /rx{1,2}/frequency                8.66, 8.91  (kHz)
  /rx{1,2}/mute                     8.63, 8.88
  /rx{1,2}/warnings                 8.61, 8.86  -- ["Aes256Error","LowSignal","NoLink","RfPeak"]
  /m/rx{1,2}/rssi                   8.96, 8.100 -- RF level, -107.0..0.0 dBm
  /m/rx{1,2}/rsqi                   8.97, 8.101 -- link quality, 0..100 %
  /m/rx{1,2}/divi                   8.98, 8.102 -- diversity antenna: 0=none, 1=A, 2=B
  /m/rx{1,2}/af                     8.99, 8.103 -- audio level, -138.5..0.0 dBFS
  /mates/tx{1,2}/battery/gauge      8.106, 8.122 -- charge, 0..100 %
  /mates/tx{1,2}/warnings           8.107, 8.123 -- ["AfPeak","LowBattery"]

(The document's own section 8.103 heading misprints its path as "/m/rx1/af"
-- a duplicate of 8.99 -- but its body text and the surrounding numbering
make clear it describes /m/rx2/af; used that way here.)

diversity and AF level *are* in the protocol, same as WSM shows them --
they just needed the right paths, which weren't in the excerpt this client
was first built from. RF (dBm), LQI (%), diversity (A/B) and AF (dBFS,
mapped to a 0-100% bar via AF_DBFS_FLOOR/CEILING below) are all now read
from confirmed, documented paths, as is the paired transmitter's battery
gauge. `rx{N}/warnings` and `mates/tx{N}/warnings` are also read and folded
into `DeviceReading.rf_warning` / `.battery_warning` / `.warnings`.

One physical EM2 answers for two channels (rx1/rx2) on one UDP socket, so
`DeviceRegistry` shares a single `SSCEM2Device` across every configured mic
slot that points at the same IP, rather than opening one socket per slot.
An SR IEM G4 is one channel per unit/IP, so no sharing is needed there.
"""

from __future__ import annotations

import json
import os
import random
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtNetwork import QHostAddress, QUdpSocket

# Set SQX_G4_DEBUG=1 (or SQX_NET_DEBUG=1 for both protocols) to print every
# raw line/message received from real hardware -- the fastest way to see
# exactly what a device is (or isn't) sending, e.g. to confirm whether a
# cyclic attribute like AF is arriving at all vs. arriving but not parsing.
# Error responses and Push/subscribe acknowledgments print regardless of
# this flag, since those are rare and high-value to see either way.
G4_DEBUG = os.environ.get("SQX_G4_DEBUG", os.environ.get("SQX_NET_DEBUG", "")).lower() in ("1", "true", "yes")
SSC_DEBUG = os.environ.get("SQX_SSC_DEBUG", os.environ.get("SQX_NET_DEBUG", "")).lower() in ("1", "true", "yes")

G4_PORT = 53212   # SR IEM G4 / EM 300-500 G4 Media Control Protocol (TI 1254 v1.0)
SSC_PORT = 45     # EW-DX EM 2, legacy unauthenticated SSC

# /m/rxN/af needs an active SSC *subscription*, not a plain polled get
# -----------------------------------------------------------------------
# Confirmed against real EW-DX EM2 hardware: name/frequency/mute, rssi
# (RF), rsqi (LQI), divi (diversity) and the paired-tx battery gauge all
# come back correctly from the plain `null`-get polling _poll() does below
# -- but /m/rxN/af never did, even though it's requested in the exact same
# batched message as rssi/rsqi/divi. AF is a fast, audio-rate metering
# value, and the SSC spec's documented mechanism for that kind of data is
# /osc/state/subscribe (section 5 of the developer's guide) rather than a
# one-shot get -- some servers likely only start actually computing/
# reporting a metering value once something is subscribed to it, to avoid
# doing that work for nobody. _subscribe_af() below requests exactly that,
# purely additively (nothing about the working polled fields changes).
SSC_SUBSCRIBE_LIFETIME_S = 30     # requested subscription lifetime
SSC_SUBSCRIBE_RENEW_MS = 20_000   # renew comfortably before it expires
SSC_SUBSCRIBE_MIN_MS = 50         # throttle: at most ~20 notifications/sec/address
SSC_SUBSCRIBE_COUNT = 20_000      # generous vs. renewal cadence above

# /m/rxN/af (SSC) reports audio level in dBFS (-138.5..0.0, per the protocol
# spec), but DeviceReading.af_peak is a 0-100% bar value like the simulator
# and the IEM side produce. This is the *display* mapping window (a practical
# "useful signal" range), not a protocol limit -- adjust to taste.
AF_DBFS_FLOOR = -42.0
AF_DBFS_CEILING = 0.0

# /m/rxN/rssi's protocol-documented range is the full -107.0..0.0 dBm; that's
# used to clamp incoming values. RF_DBM_FLOOR/CEILING in device_widgets.py is
# a separate, narrower *display* window for the bar -- see that file.
RSSI_DBM_MIN = -107.0
RSSI_DBM_MAX = 0.0


# ---------------------------------------------------------------------------
# Reading shape shared with device_widgets.py (unchanged by this rewrite)
# ---------------------------------------------------------------------------

@dataclass
class DeviceReading:
    """
    A snapshot of everything a channel strip widget wants to show. Not every
    field applies to every device kind -- widgets only read the ones that
    matter for their type:

      IEM G4 (SR transmitter):
        frequency_mhz, af_l, af_r, muted, warnings
      EW-DX EM2 (SSC receiver channel):
        rf_dbm, lqi, diversity_active, af_peak, battery_percent,
        battery_warning, rf_warning, muted, warnings
        -- all read from confirmed SSC paths, see module docstring.
    """
    connected: bool = False
    simulated: bool = False
    name: str = ""
    frequency_mhz: Optional[float] = None
    warnings: str = ""

    # -- EW-DX EM2 (mic) fields --
    rf_dbm: Optional[float] = None          # RF signal strength, dBm (m/rxN/rssi)
    lqi: Optional[int] = None               # link quality indicator, 0-100 (m/rxN/rsqi)
    diversity_active: Optional[str] = None  # "A" | "B" | None (m/rxN/divi)
    af_peak: Optional[int] = None           # mono AF level, 0-100 (mapped from m/rxN/af, dBFS)
    af_dbfs: Optional[float] = None         # the raw dBFS value af_peak was mapped from, for display
    battery_percent: Optional[int] = None   # mates/txN/battery/gauge
    battery_warning: bool = False           # driven by mates/txN/warnings ("LowBattery")
    rf_warning: bool = False                # driven by rxN/warnings ("LowSignal"/"NoLink")

    # -- IEM G4 fields --
    af_l: Optional[int] = None              # stereo AF, left, 0-100 (from the SR's "AF" cyclic push)
    af_r: Optional[int] = None              # stereo AF, right, 0-100

    muted: bool = False
    extra: dict = field(default_factory=dict)


class DeviceClientBase(QObject):
    """Common interface used by device_widgets.ChannelStripWidget."""

    reading_changed = Signal(object)     # DeviceReading
    connection_changed = Signal(bool)

    def __init__(self, kind: str, name: str, ip: str, port: int, channel: int,
                 poll_interval_ms: int = 1000, parent=None):
        super().__init__(parent)
        self.kind = kind              # "iem" or "mic"
        self.name = name or kind
        self.ip = (ip or "").strip()
        self.port = port
        self.channel = channel or 1
        self.poll_interval_ms = max(50, poll_interval_ms)
        self.reading = DeviceReading(name=self.name)

    def start(self):  # pragma: no cover - overridden
        raise NotImplementedError

    def stop(self):  # pragma: no cover - overridden
        raise NotImplementedError

    def _emit(self, reading: DeviceReading):
        self.reading = reading
        self.reading_changed.emit(reading)


# ---------------------------------------------------------------------------
# Simulation (unchanged: no network I/O, used when SIMULATE_DEVICES is on or
# a slot has no IP configured)
# ---------------------------------------------------------------------------

def _af_pct_to_dbfs(pct: int) -> float:
    """Inverse of the af dBFS->0-100% mapping below, for the simulator only."""
    span = AF_DBFS_CEILING - AF_DBFS_FLOOR
    return AF_DBFS_FLOOR + (pct / 100.0) * span


class SimulatedDeviceClient(DeviceClientBase):
    """Generates believable-looking telemetry with no network I/O at all."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._battery = random.uniform(35, 100)
        self._rf_base = random.uniform(55, 95)     # 0-100 "quality" used to derive dBm/LQI
        self._diversity = random.choice(["A", "B"])

    def start(self):
        self.connection_changed.emit(True)
        self._tick()
        self._timer.start(self.poll_interval_ms)

    def stop(self):
        self._timer.stop()

    def _random_af(self):
        return int(max(0, min(100, 30 + random.uniform(-5, 50) if random.random() > 0.15 else 0)))

    def _tick(self):
        if self.kind == "mic":
            self._battery = max(0.0, self._battery - random.uniform(0, 0.05))
            self._rf_base = max(0.0, min(100.0, self._rf_base + random.uniform(-3, 3)))
            rf_dbm = round(-95.0 + (self._rf_base / 100.0) * 70.0 + random.uniform(-2, 2), 1)
            lqi = int(max(0, min(100, self._rf_base + random.uniform(-5, 5))))
            if random.random() < 0.06:
                self._diversity = "B" if self._diversity == "A" else "A"
            af_pct = self._random_af()
            reading = DeviceReading(
                connected=True,
                simulated=True,
                name=self.name,
                rf_dbm=rf_dbm,
                lqi=lqi,
                diversity_active=self._diversity,
                af_peak=af_pct,
                af_dbfs=_af_pct_to_dbfs(af_pct),
                battery_percent=int(self._battery),
                battery_warning=self._battery < 15,
                rf_warning=rf_dbm < -80 or lqi < 20,
                muted=False,
            )
        else:  # iem
            af_enabled = getattr(self, "af_enabled", True)
            reading = DeviceReading(
                connected=True,
                simulated=True,
                name=self.name,
                frequency_mhz=round(520.000 + (hash(self.ip or self.name) % 4000) / 100.0, 3),
                af_l=self._random_af() if af_enabled else None,
                af_r=self._random_af() if af_enabled else None,
                muted=False,
            )
        self._emit(reading)


# ---------------------------------------------------------------------------
# G4 Media Control Protocol (TI 1254 v1.0) -- SR IEM G4 / EM 300-500 G4
# ---------------------------------------------------------------------------

_G4_ERROR_RE = re.compile(r"^\d{4}:")


@dataclass
class G4ChannelData:
    name: str = ""
    firmware: str = ""
    frequency_khz: Optional[int] = None
    bank: Optional[int] = None
    channel: Optional[int] = None
    mute: Optional[bool] = None
    warnings: str = ""

    # EM (receiver) only -- kept for completeness; not used by our IEM slots
    battery_pct: Optional[int] = None
    rf_level_pct: Optional[int] = None
    antenna_active: Optional[int] = None
    pilot_detected: Optional[bool] = None
    af_peak_pct: Optional[int] = None
    af_peak_hold_pct: Optional[int] = None

    # SR (transmitter) only -- this is what our IEM slots read. Per TI 1254
    # v1.0 section "Cyclic attributes valid for SR only", the 4 values are,
    # in order: Af-Peak1, Af-Peak2, Af-PeakHold1, Af-PeakHold2 (0..100%,
    # >100% possible) -- i.e. instantaneous L/R followed by their peak-hold.
    # We only use the first two (instantaneous) for the live meter.
    sr_af_levels: List[int] = field(default_factory=list)
    mode_stereo: Optional[bool] = None
    sensitivity_db: Optional[int] = None


class G4Device(QObject):
    """
    One ew G4 stationary device (one audio channel), talking the ASCII
    "Command param1 ... paramN\\r" protocol over UDP/53212 described in
    Sennheiser's "Media control protocol description" (TI 1254 v1.0),
    covering ew 300-500 G4 and ew IEM G4 stationary devices. Subscribes to
    cyclic attribute pushes via `Push` and renews that subscription before
    it expires; a watchdog flags the device offline if pushes stop arriving.

    Real-hardware finding, confirmed: an SR's cyclic attributes (AF among
    them) weren't updating even though frequency/mute/connection all worked
    fine. Debug logging showed the device rejecting our subscription
    outright -- "1020: Value out of range [ Push 60 1000 7 ]" -- which
    `_send_push()` now explains and fixes: the flags=7 we were sending sets
    a bit ("on change of pilot signal or battery status") that TI 1254
    v1.0's own flag table marks "(EM only)"; an SR has neither to report
    that way, so the device apparently doesn't accept it as a legal value
    at all. SR now gets flags=3 (the two device-agnostic bits only).

    (Earlier, before that error was actually visible, a case mismatch in
    the spec's own AF example -- "Af" vs. the header's "AF" -- looked like
    the likely cause and `_handle_line()` was made case-insensitive to
    cover it. That's harmless and stays, but the flags value was the actual
    fix.)
    """

    data_changed = Signal()
    connection_changed = Signal(bool)

    PUSH_TIMEOUT_S = 60       # ask the device to keep pushing for this long
    PUSH_RENEW_MS = 25_000    # renew comfortably before the timeout expires

    def __init__(self, name: str, ip: str, kind: str, port: int = G4_PORT,
                 push_cycle_ms: int = 200, parent=None):
        super().__init__(parent)
        if kind not in ("G4_SR", "G4_EM"):
            raise ValueError(f"Unsupported G4 kind: {kind}")
        self.name = name
        self.ip = ip
        self.port = port
        self.kind = kind
        self.push_cycle_ms = max(20, push_cycle_ms)  # device-side cyclic-update interval
        self.data = G4ChannelData()
        self.online = False
        self._last_rx_ms = 0.0
        self._stale_after_ms = self.PUSH_TIMEOUT_S * 1000 + 8000

        self.socket = QUdpSocket(self)
        self.socket.bind(QHostAddress.AnyIPv4, 0)
        self.socket.readyRead.connect(self._on_ready_read)

        self._renew_timer = QTimer(self)
        self._renew_timer.timeout.connect(self._send_push)
        self._renew_timer.start(self.PUSH_RENEW_MS)

        self._watchdog = QTimer(self)
        self._watchdog.timeout.connect(self._check_alive)
        self._watchdog.start(2000)

        self._bootstrap()

    # -- outgoing -----------------------------------------------------
    def _send(self, line: str) -> None:
        payload = (line + "\r").encode("ascii", errors="ignore")
        self.socket.writeDatagram(payload, QHostAddress(self.ip), self.port)

    def _bootstrap(self) -> None:
        self._send_push()
        self._send("Name")
        self._send("FirmwareRevision")
        self._send("Frequency")
        self._send("Mute")
        if self.kind == "G4_SR":
            self._send("Mode")
            self._send("Sensitivity")

    def _send_push(self) -> None:
        # 3rd parameter is a 3-bit field: +1 config-on-change, +2 cyclic-on-
        # warning-change, +4 cyclic-on-pilot/battery-change. That +4 bit is
        # explicitly documented as "(EM only)" in TI 1254 v1.0's flag table.
        # Real hardware (an SR/IEM G4) rejected "Push 60 1000 7" outright
        # with error 1020 ("value out of range") -- consistent with +4
        # simply not being a legal value for a device with no pilot signal
        # or battery of its own to report that way. SR gets flags=3 (the
        # two device-agnostic bits only); EM keeps the full flags=7.
        flags = 3 if self.kind == "G4_SR" else 7
        self._send(f"Push {self.PUSH_TIMEOUT_S} {self.push_cycle_ms} {flags}")

    def set_mute(self, mute: bool) -> None:
        self._send(f"Mute {1 if mute else 0}")

    def set_name(self, name: str) -> None:
        self._send(f"Name {name}")

    def request_refresh(self) -> None:
        self._bootstrap()

    # -- incoming -------------------------------------------------------
    def _check_alive(self) -> None:
        now = time.monotonic() * 1000
        alive = bool(self._last_rx_ms) and (now - self._last_rx_ms) < self._stale_after_ms
        if alive != self.online:
            self.online = alive
            self.connection_changed.emit(alive)

    def _on_ready_read(self) -> None:
        while self.socket.hasPendingDatagrams():
            size = self.socket.pendingDatagramSize()
            datagram, _host, _port = self.socket.readDatagram(size)
            self._last_rx_ms = time.monotonic() * 1000
            if not self.online:
                self.online = True
                self.connection_changed.emit(True)
            text = bytes(datagram).decode("ascii", errors="ignore")
            for line in text.split("\r"):
                line = line.strip()
                if line:
                    if G4_DEBUG:
                        print(f"G4 [{self.name or self.ip}] <- {line!r}")
                    self._handle_line(line)
        self.data_changed.emit()

    def _handle_line(self, line: str) -> None:
        if _G4_ERROR_RE.match(line):
            # Previously silently dropped -- these were invisible even when
            # e.g. our own Push command was being rejected by the device,
            # which would explain "cyclic attributes never arrive" while
            # one-shot commands (Name/Frequency/Mute) keep working fine.
            print(f"G4 [{self.name or self.ip}]: device reported an error: {line}")
            return

        parts = line.split(" ")
        # Case-insensitive on purpose: the protocol doc's own "Response of
        # cyclic attributes" example writes the SR's audio-level line as
        # "Af ..." while that same attribute's formal header (and the EM
        # side's own example) is "AF" -- an inconsistency inside the spec
        # itself. Real firmware may emit either; comparing case-folded means
        # it doesn't matter which one actually shows up on the wire. No two
        # command keywords in this protocol differ only by case, so this
        # can't introduce an ambiguity.
        cmd, args = parts[0].upper(), parts[1:]
        d = self.data
        try:
            if cmd == "NAME":
                d.name = " ".join(args)
            elif cmd == "FIRMWAREREVISION":
                d.firmware = args[0] if args else ""
            elif cmd == "FREQUENCY":
                d.frequency_khz = int(args[0])
                d.bank = int(args[1]) if len(args) > 1 else None
                d.channel = int(args[2]) if len(args) > 2 else None
            elif cmd == "MUTE":
                d.mute = bool(int(args[0]))
            elif cmd == "MSG":
                d.warnings = " ".join(args) if args else "OK"
            elif cmd == "MODE":
                d.mode_stereo = bool(int(args[0]))
            elif cmd == "SENSITIVITY":
                d.sensitivity_db = int(args[0])
            elif cmd == "BAT":
                d.battery_pct = None if args[0] == "?" else int(args[0])
            elif cmd == "RF1":
                d.rf_level_pct = max(d.rf_level_pct or 0, int(args[1]))
            elif cmd == "RF2":
                d.rf_level_pct = max(d.rf_level_pct or 0, int(args[1]))
            elif cmd == "RF" and self.kind == "G4_EM":
                d.rf_level_pct = int(args[0])
                d.antenna_active = int(args[1])
                d.pilot_detected = bool(int(args[2]))
            elif cmd == "AF" and self.kind == "G4_EM":
                d.af_peak_pct = int(args[0])
                d.af_peak_hold_pct = int(args[1])
            elif cmd == "AF" and self.kind == "G4_SR":
                try:
                    d.sr_af_levels = [int(a) for a in args]
                except ValueError:
                    # Isolated from the broad except below on purpose: if
                    # one value in this line fails to parse, we want to know
                    # about it (and see the raw args) rather than have it
                    # silently vanish along with everything else this line
                    # might have updated.
                    print(f"G4 [{self.name or self.ip}]: AF line didn't parse as "
                          f"integers: {args!r}")
            elif cmd == "PUSH":
                # Acknowledgment of our Push subscription request -- printed
                # so a rejected/adjusted subscription is visible instead of
                # silently doing nothing. A healthy ack echoes back
                # "PUSH <timeout> <cycle> <flags>" matching what we sent.
                print(f"G4 [{self.name or self.ip}]: Push acknowledged: {line}")
            elif cmd in ("STATES", "CONFIG", "BANKLIST", "RFCONFIG", "SQUELCH", "EQUALIZER"):
                pass  # received/acknowledged but not surfaced in the UI
        except (ValueError, IndexError):
            pass  # malformed/unexpected line - ignore rather than crash

    def close(self) -> None:
        try:
            self._send("Push 0 0 0")
        except Exception:
            pass
        self.socket.close()


class G4IemChannelClient(DeviceClientBase):
    """
    Adapter: wraps one G4Device(kind="G4_SR") -- one physical SR IEM G4 unit
    is one audio channel, so unlike the mic side there's no `channel` concept
    to select here; the base class's `channel` field is accepted for
    interface symmetry but never read.
    """

    def __init__(self, *args, af_enabled: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self._device: Optional[G4Device] = None
        # Preferences -> IEM "Show AF level" switch. False means we don't
        # even do the (cheap, but non-zero) work of pulling L/R out of the
        # cyclic AF line -- the widget won't show a meter for it either way.
        self.af_enabled = af_enabled

    def start(self):
        if not self.ip:
            self.connection_changed.emit(False)
            return
        self._device = G4Device(
            name=self.name, ip=self.ip, kind="G4_SR", port=self.port or G4_PORT,
            push_cycle_ms=self.poll_interval_ms, parent=self,
        )
        self._device.data_changed.connect(self._on_data_changed)
        self._device.connection_changed.connect(self.connection_changed)

    def stop(self):
        if self._device is not None:
            self._device.close()
            self._device = None

    def _on_data_changed(self):
        d = self._device.data
        af_l = af_r = None
        if self.af_enabled:
            af = d.sr_af_levels
            af_l = af[0] if len(af) >= 1 else None
            af_r = af[1] if len(af) >= 2 else (af[0] if len(af) == 1 else None)
        reading = DeviceReading(
            connected=self._device.online,
            simulated=False,
            name=d.name,   # the device's own reported name -- not our configured one
            frequency_mhz=(d.frequency_khz / 1000.0) if d.frequency_khz is not None else None,
            warnings=d.warnings,
            af_l=af_l,
            af_r=af_r,
            muted=bool(d.mute),
        )
        self._emit(reading)


# ---------------------------------------------------------------------------
# SSC (Sennheiser Sound Control) -- EW-DX EM 2
# ---------------------------------------------------------------------------

@dataclass
class SSCChannelData:
    name: str = ""
    frequency_khz: Optional[int] = None
    mute: Optional[bool] = None
    rsqi_pct: Optional[int] = None       # link quality, 0..100 % -- /m/rxN/rsqi
    rssi_dbm: Optional[float] = None     # RF level, -107..0 dBm -- /m/rxN/rssi
    divi: Optional[int] = None           # diversity antenna, raw: 0=none, 1=A, 2=B -- /m/rxN/divi
    af_dbfs: Optional[float] = None      # audio level, -138.5..0 dBFS -- /m/rxN/af
    battery_pct: Optional[int] = None    # -- /mates/txN/battery/gauge
    rx_warnings: List[str] = field(default_factory=list)   # /rxN/warnings
    tx_warnings: List[str] = field(default_factory=list)   # /mates/txN/warnings


class SSCEM2Device(QObject):
    """
    One EW-DX EM 2 (produces two channels: rx1 and rx2), talking legacy
    SSCv1 (unauthenticated JSON-over-UDP, port 45) -- the device's "Legacy"
    3rd Party Access mode. If the unit has been claimed with SSCv2
    (encrypted, HTTPS + basic auth) this client cannot talk to it: switch
    the device back to "Legacy" 3rd party access, or this class would need
    extending to speak SSCv2 over HTTPS instead.
    """

    data_changed = Signal()
    connection_changed = Signal(bool)

    STALE_AFTER_MS = 4000

    def __init__(self, name: str, ip: str, port: int = SSC_PORT,
                 poll_ms: int = 1000, parent=None):
        super().__init__(parent)
        self.name = name
        self.ip = ip
        self.port = port
        self.poll_ms = max(100, poll_ms)
        self.rx1 = SSCChannelData()
        self.rx2 = SSCChannelData()
        self.online = False
        self._last_rx_ms = 0.0

        self.socket = QUdpSocket(self)
        self.socket.bind(QHostAddress.AnyIPv4, 0)
        self.socket.readyRead.connect(self._on_ready_read)

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll)
        self._poll_timer.start(self.poll_ms)

        self._subscribe_timer = QTimer(self)
        self._subscribe_timer.timeout.connect(self._subscribe_af)
        self._subscribe_timer.start(SSC_SUBSCRIBE_RENEW_MS)

        self._watchdog = QTimer(self)
        self._watchdog.timeout.connect(self._check_alive)
        self._watchdog.start(1000)

        self._poll()
        self._subscribe_af()

    # -- outgoing ---------------------------------------------------------
    def _send(self, obj: dict) -> None:
        try:
            payload = json.dumps(obj, separators=(",", ":")).encode("utf-8")
            self.socket.writeDatagram(payload, QHostAddress(self.ip), self.port)
        except (TypeError, OSError):
            pass

    def _poll(self) -> None:
        self._send({"rx1": {"name": None, "frequency": None, "mute": None, "warnings": None}})
        self._send({"rx2": {"name": None, "frequency": None, "mute": None, "warnings": None}})
        self._send({"m": {"rx1": {"rsqi": None, "rssi": None, "divi": None, "af": None}}})
        self._send({"m": {"rx2": {"rsqi": None, "rssi": None, "divi": None, "af": None}}})
        self._send({"mates": {"tx1": {"battery": {"gauge": None}, "warnings": None}}})
        self._send({"mates": {"tx2": {"battery": {"gauge": None}, "warnings": None}}})

    def _subscribe_af(self) -> None:
        """
        Explicitly subscribe to /m/rx1/af and /m/rx2/af (SSC dev guide
        section 5, /osc/state/subscribe) -- see the SSC_SUBSCRIBE_* comment
        near the top of this file for why. Subscriptions expire (we ask for
        SSC_SUBSCRIBE_LIFETIME_S), so this is called again on a timer, well
        before that. The device's push notifications for the subscribed
        addresses arrive as ordinary {"m":{"rx1":{"af": <value>}}} messages,
        which _on_ready_read()/_apply()/_set_value() already handle exactly
        like a get() reply -- no separate receive-side handling needed.
        """
        params = {"min": SSC_SUBSCRIBE_MIN_MS, "max": 0,
                  "count": SSC_SUBSCRIBE_COUNT, "lifetime": SSC_SUBSCRIBE_LIFETIME_S}
        self._send({"osc": {"state": {"subscribe": [
            {"#": params, "m": {"rx1": {"af": None}}},
            {"#": params, "m": {"rx2": {"af": None}}},
        ]}}})

    def set_mute(self, channel: int, mute: bool) -> None:
        key = "rx1" if channel == 1 else "rx2"
        self._send({key: {"mute": mute}})

    def request_refresh(self) -> None:
        self._poll()

    # -- incoming -----------------------------------------------------
    def _check_alive(self) -> None:
        now = time.monotonic() * 1000
        alive = bool(self._last_rx_ms) and (now - self._last_rx_ms) < self.STALE_AFTER_MS
        if alive != self.online:
            self.online = alive
            self.connection_changed.emit(alive)

    def _on_ready_read(self) -> None:
        while self.socket.hasPendingDatagrams():
            size = self.socket.pendingDatagramSize()
            datagram, _host, _port = self.socket.readDatagram(size)
            self._last_rx_ms = time.monotonic() * 1000
            if not self.online:
                self.online = True
                self.connection_changed.emit(True)
            try:
                msg = json.loads(bytes(datagram).decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if SSC_DEBUG:
                print(f"SSC [{self.name or self.ip}] <- {msg!r}")
            if isinstance(msg, dict):
                self._apply(msg, ())
        self.data_changed.emit()

    def _apply(self, obj: Dict[str, Any], path: Tuple[str, ...]) -> None:
        for key, value in obj.items():
            p = path + (key,)
            if isinstance(value, dict):
                self._apply(value, p)
            else:
                self._set_value(p, value)

    def _set_value(self, path: Tuple[str, ...], value: Any) -> None:
        if not path:
            return
        chan: Optional[SSCChannelData] = None

        if path[0] in ("rx1", "rx2"):
            chan = self.rx1 if path[0] == "rx1" else self.rx2
            leaf_path = path[1:]
        elif path[0] == "m" and len(path) > 1 and path[1] in ("rx1", "rx2"):
            chan = self.rx1 if path[1] == "rx1" else self.rx2
            leaf_path = path[2:]
        elif path[0] == "mates" and len(path) > 1 and path[1] in ("tx1", "tx2"):
            chan = self.rx1 if path[1] == "tx1" else self.rx2
            leaf_path = path[2:]
        else:
            return

        if chan is None or not leaf_path:
            return
        leaf = leaf_path[-1]

        if leaf == "name" and isinstance(value, str):
            chan.name = value
        elif leaf == "frequency" and isinstance(value, (int, float)):
            chan.frequency_khz = int(value)
        elif leaf == "mute" and isinstance(value, bool):
            chan.mute = value
        elif leaf == "rsqi" and isinstance(value, (int, float)):
            chan.rsqi_pct = int(value)
        elif leaf == "rssi" and isinstance(value, (int, float)):
            chan.rssi_dbm = float(value)
        elif leaf == "divi" and isinstance(value, (int, float)):
            chan.divi = int(value)
        elif leaf == "af" and isinstance(value, (int, float)):
            chan.af_dbfs = float(value)
        elif leaf == "gauge" and isinstance(value, (int, float)):
            chan.battery_pct = int(value)
        elif leaf == "warnings" and isinstance(value, list):
            # "warnings" is ambiguous between /rxN/warnings and
            # /mates/txN/warnings -- path[0] disambiguates which list it is.
            warning_list = [str(w) for w in value]
            if path[0] in ("rx1", "rx2"):
                chan.rx_warnings = warning_list
            elif path[0] == "mates":
                chan.tx_warnings = warning_list

    def close(self) -> None:
        self._poll_timer.stop()
        self._subscribe_timer.stop()
        self._watchdog.stop()
        self.socket.close()


class SscMicChannelClient(DeviceClientBase):
    """
    Adapter: reads one channel (rx1/rx2, per `channel`) off a *shared*
    SSCEM2Device -- see DeviceRegistry. RF (dBm), LQI (%), diversity (A/B),
    AF level (mapped from dBFS to 0-100%) and battery are all read from
    confirmed SSC paths -- see module docstring.
    """

    def __init__(self, registry: "DeviceRegistry", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registry = registry
        self._device: Optional[SSCEM2Device] = None

    def start(self):
        if not self.ip:
            self.connection_changed.emit(False)
            return
        self._device = self._registry.get_em2(self.ip, port=self.port or SSC_PORT,
                                               poll_ms=self.poll_interval_ms)
        self._device.data_changed.connect(self._on_data_changed)
        self._device.connection_changed.connect(self.connection_changed)
        self.connection_changed.emit(self._device.online)
        self._on_data_changed()

    def stop(self):
        if self._device is not None:
            try:
                self._device.data_changed.disconnect(self._on_data_changed)
                self._device.connection_changed.disconnect(self.connection_changed)
            except (TypeError, RuntimeError):
                pass
            self._device = None
        # NOTE: the shared SSCEM2Device itself is owned/closed by the
        # DeviceRegistry, not by this per-slot adapter -- another slot may
        # still be using the other rx channel on the same unit.

    def _on_data_changed(self):
        if self._device is None:
            return
        chan = self._device.rx1 if self.channel == 1 else self._device.rx2

        # /m/rxN/divi: 0=none, 1=antenna A, 2=antenna B (SSC dev guide 8.98/8.102).
        diversity_active = {1: "A", 2: "B"}.get(chan.divi)

        # /m/rxN/af is dBFS (-138.5..0); map onto the widget's 0-100% bar.
        af_peak = None
        if chan.af_dbfs is not None:
            span = AF_DBFS_CEILING - AF_DBFS_FLOOR
            af_peak = int(max(0.0, min(100.0, (chan.af_dbfs - AF_DBFS_FLOOR) / span * 100.0)))

        warning_text = ", ".join(chan.rx_warnings + chan.tx_warnings)

        reading = DeviceReading(
            connected=self._device.online,
            simulated=False,
            name=chan.name,   # the device's own reported name -- not our configured one
            frequency_mhz=(chan.frequency_khz / 1000.0) if chan.frequency_khz is not None else None,
            warnings=warning_text,
            rf_dbm=chan.rssi_dbm,
            lqi=chan.rsqi_pct,
            diversity_active=diversity_active,
            af_peak=af_peak,
            af_dbfs=chan.af_dbfs,
            battery_percent=chan.battery_pct,
            # "LowSignal"/"NoLink" (rx side) and "LowBattery" (tx side) are the
            # protocol's own warning flags (SSC dev guide 8.61/8.107); OR'd
            # with a threshold check as a belt-and-suspenders fallback in case
            # a warning hasn't been polled yet.
            battery_warning=("LowBattery" in chan.tx_warnings
                              or (chan.battery_pct is not None and chan.battery_pct < 15)),
            rf_warning=(any(w in ("LowSignal", "NoLink") for w in chan.rx_warnings)
                        or (chan.rssi_dbm is not None and chan.rssi_dbm < -80)
                        or (chan.rsqi_pct is not None and chan.rsqi_pct < 20)),
            muted=bool(chan.mute),
        )
        self._emit(reading)


class DeviceRegistry:
    """
    Shares one SSCEM2Device per unique IP across a DeviceRow's lifetime,
    since one physical EM2 answers for two channels (rx1/rx2) on one UDP
    socket -- e.g. Mic slots 1 & 2 pointed at the same EM2's IP end up
    reading rx1/rx2 of a single shared device instead of opening two
    redundant sockets to the same unit.

    Owned by DeviceRow; call close_all() on rebuild/teardown.
    """

    def __init__(self):
        self._em2_by_ip: Dict[str, SSCEM2Device] = {}

    def get_em2(self, ip: str, port: int = SSC_PORT, poll_ms: int = 1000) -> SSCEM2Device:
        device = self._em2_by_ip.get(ip)
        if device is None:
            device = SSCEM2Device(name=ip, ip=ip, port=port, poll_ms=poll_ms)
            self._em2_by_ip[ip] = device
        return device

    def close_all(self):
        for device in self._em2_by_ip.values():
            device.close()
        self._em2_by_ip.clear()


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def make_client(kind: str, name: str, ip: str, port: int, channel: int,
                 poll_interval_ms: int, simulate: bool,
                 registry: "DeviceRegistry", af_enabled: bool = True,
                 parent=None) -> DeviceClientBase:
    """
    Factory: returns a simulated or real (protocol-appropriate) client.
    `af_enabled` only applies to `kind == "iem"` (Preferences -> IEM ->
    "Show AF level"); ignored for mic.
    """
    if simulate or not ip:
        client = SimulatedDeviceClient(kind, name, ip, port, channel, poll_interval_ms, parent=parent)
        if kind == "iem":
            client.af_enabled = af_enabled
        return client
    if kind == "iem":
        return G4IemChannelClient(kind, name, ip, port or G4_PORT, channel,
                                   poll_interval_ms, af_enabled=af_enabled, parent=parent)
    return SscMicChannelClient(registry, kind, name, ip, port or SSC_PORT, channel,
                                poll_interval_ms, parent=parent)
