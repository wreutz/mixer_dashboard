"""
device_widgets.py

Channel-strip widgets for the EW-DX EM2 (wireless mic receiver) and IEM G4
devices, styled after Sennheiser WSM / Shure Wireless Workbench channel
strips, laid out in a fixed 4-column x up-to-2-row grid so they fit a
320px-wide portrait screen.

Per-type parameters (see also device_network.DeviceReading):

  IEM G4 (transmitter -- no RF/battery telemetry available to us):
    - frequency
    - AF level, stereo (L / R)
    - no battery, no RF meter

  EW-DX EM2 (receiver channel):
    - RF level (dBm)
    - LQI -- link quality indicator (0-100%)
    - AF level (mono)
    - battery
    - diversity A/B, shown as two small squares above the RF meter

These widgets are pure Qt/Python (no .ui dependency) and are instantiated at
runtime by device_widgets.DeviceRow, which is built from settings.ini and
placed inside the QScrollArea ("scrollDevices") defined in
assets/mainwindow.ui.
"""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFrame, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
)

from device_network import DeviceReading, DeviceRegistry, G4_PORT, SSC_PORT, make_client

# ---------------------------------------------------------------------------
# Grid / geometry constants
# ---------------------------------------------------------------------------

# Fixed 4-column grid, up to 2 rows (max 4 IEM + max 4 mic channels).
GRID_COLUMNS = 4
GRID_MAX_ROWS = 2

STRIP_WIDTH = 74
# Sized so the AF meter's bar never drops below SegmentBar's own declared
# 44px minimum once its value-label is showing (needed to fix AF being
# blank on real hardware -- see the AF readout addition in
# WirelessMicChannelWidget). At 234, the mic strip (the tighter of the two
# layouts) leaves ~55px/~7.5px-per-segment for the AF bar and ~66px/~9.3px
# for RF and LQI; verified by simulating the actual QVBoxLayout/QHBoxLayout
# item stack rather than guessed.
STRIP_HEIGHT = 234

# RF is reported in dBm, but the bar needs a 0-100% fill. This is the display
# window only -- it does not clamp or alter the dBm value shown in the readout.
# Widen/narrow it if your EM2s sit in a different part of the range in practice.
RF_DBM_FLOOR = -95.0     # bar empty at or below this
RF_DBM_CEILING = -25.0   # bar full at or above this

# Geometry knobs shared with MainWindow's dynamic resize calculation (kept
# here, next to STRIP_HEIGHT, so the two stay in sync).
GRID_ROW_SPACING = 4
GRID_MARGIN_TOP = 2
GRID_MARGIN_BOTTOM = 2
GROUPBOX_TITLE_OFFSET = 20   # vertical space a QGroupBox title reserves above its content
GROUP_BOTTOM_PADDING = 6     # a little breathing room / scrollbar allowance
EMPTY_MESSAGE_HEIGHT = 40    # collapsed height: just enough for the 2-line "nothing enabled" msg


def group_devices_height(rows: int) -> int:
    """
    Height (px) the IEM/Mic QGroupBox needs. `rows` is 1 or 2 for an actual
    grid of channel strips; MainWindow uses this to grow/shrink groupDevices
    and push the web view down/up to match. `rows == 0` is the collapsed
    state -- no channels enabled, or the whole feature switched off via
    DEVICES_ENABLED -- which needs only enough room for a short message, not
    a full row of channel strips.
    """
    if rows <= 0:
        return GROUPBOX_TITLE_OFFSET + EMPTY_MESSAGE_HEIGHT + GROUP_BOTTOM_PADDING
    rows = min(GRID_MAX_ROWS, rows)
    content_h = (rows * STRIP_HEIGHT
                 + max(0, rows - 1) * GRID_ROW_SPACING
                 + GRID_MARGIN_TOP + GRID_MARGIN_BOTTOM)
    return GROUPBOX_TITLE_OFFSET + content_h + GROUP_BOTTOM_PADDING


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

COLOR_BG = QColor("#2c2c2c")
COLOR_BG_DISABLED = QColor("#202020")
COLOR_BORDER = QColor("#111111")
COLOR_TEXT = QColor(220, 220, 220)
COLOR_TEXT_DIM = QColor(140, 140, 140)
COLOR_CAPTION = QColor(150, 150, 155)
COLOR_OK = QColor(70, 220, 110)
COLOR_WARN = QColor(240, 190, 60)
COLOR_BAD = QColor(230, 70, 70)
COLOR_OFF = QColor(70, 70, 70)
COLOR_SIM = QColor(235, 140, 40)   # status dot for simulated channels (instead of red/green)


def _segment_color(lit_index: int, lit_count: int, total: int, kind: str) -> QColor:
    """Color for one lit segment. 'af' peaks red at the top; 'level' (RF/LQI
    quality meters) go red when few segments are lit at all."""
    if kind == "af":
        if lit_index >= total - 1:
            return COLOR_BAD
        if lit_index >= total - 3:
            return COLOR_WARN
        return COLOR_OK
    # "level" (RF / LQI): fewer lit segments = weaker/worse
    if lit_count <= 1:
        return COLOR_BAD
    if lit_count <= 3:
        return COLOR_WARN
    return COLOR_OK


# ---------------------------------------------------------------------------
# Small building-block widgets
# ---------------------------------------------------------------------------

class SegmentBar(QWidget):
    """A small vertical segmented level meter (used for RF, LQI, AF)."""

    def __init__(self, kind: str, segments: int = 6, parent=None):
        super().__init__(parent)
        self.kind = kind  # "level" (RF/LQI) or "af"
        self.segments = segments
        self._value = 0  # 0-100, None-safe via set_value
        self._enabled_state = True
        self.setMinimumSize(10, 44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_value(self, value):
        v = 0 if value is None else max(0, min(100, int(value)))
        if v != self._value:
            self._value = v
            self.update()

    def set_enabled_state(self, enabled: bool):
        self._enabled_state = enabled
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w = self.width()
        h = self.height()
        gap = 2
        seg_h = (h - gap * (self.segments - 1)) / self.segments
        lit_count = round((self._value / 100.0) * self.segments)
        for i in range(self.segments):
            # index 0 = bottom segment
            y = h - (i + 1) * seg_h - i * gap
            rect = QRectF(0, y, w, seg_h)
            lit = i < lit_count
            if not self._enabled_state:
                color = COLOR_OFF
            elif lit:
                color = _segment_color(i, lit_count, self.segments, self.kind)
            else:
                color = COLOR_OFF
            painter.fillRect(rect, color)
        painter.end()


def _caption_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"color: {COLOR_CAPTION.name()}; font-size: 8px; font-weight: bold;")
    lbl.setFixedHeight(10)
    return lbl


def _value_label() -> QLabel:
    lbl = QLabel("--")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"color: {COLOR_TEXT_DIM.name()}; font-size: 8px;")
    lbl.setFixedHeight(10)
    return lbl


def _has_warning_text(warnings: str) -> bool:
    """
    True for a non-empty warning string that isn't just "OK" (the G4
    protocol's own "no warning" `Msg` value). Both IEM (G4 `Msg`) and mic
    (SSC `rxN/warnings` + `mates/txN/warnings`) readings populate this.
    """
    return bool(warnings) and warnings.strip().upper() != "OK"


def _readout_label() -> QLabel:
    """
    A full-width numeric readout line under the bar row (e.g. "RF  -58dBm",
    "LQI  87%", "520.125 MHz"). Kept separate from the bars so the bars
    themselves can stay side-by-side and tall.
    """
    lbl = QLabel("--")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"color: {COLOR_TEXT.name()}; font-size: 8px;")
    lbl.setFixedHeight(11)
    return lbl


class MeterBlock(QWidget):
    """Caption label + segmented bar + (optional) numeric value readout, stacked vertically."""

    def __init__(self, caption: str, kind: str, show_value: bool = True, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(_caption_label(caption))
        self.bar = SegmentBar(kind)
        layout.addWidget(self.bar, stretch=1)
        self.value_label = _value_label() if show_value else None
        if self.value_label is not None:
            layout.addWidget(self.value_label)

    def set_value(self, value, text: str = None):                                   # type: ignore
        self.bar.set_value(value)
        if self.value_label is not None:
            self.value_label.setText(text if text is not None else "--")

    def set_enabled_state(self, enabled: bool):
        self.bar.set_enabled_state(enabled)


class DiversitySquares(QWidget):
    """Two small squares labelled A / B; the currently-active diversity antenna lights up."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addStretch(1)
        self.sq_a = self._make_square("A")
        layout.addWidget(self.sq_a)
        self.sq_b = self._make_square("B")
        layout.addWidget(self.sq_b)
        layout.addStretch(1)
        self._set_square_style(self.sq_a, active=False, enabled=True)
        self._set_square_style(self.sq_b, active=False, enabled=True)

    @staticmethod
    def _make_square(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFixedSize(16, 14)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl

    @staticmethod
    def _set_square_style(label: QLabel, active: bool, enabled: bool):
        if not enabled:
            bg, fg = COLOR_OFF, COLOR_TEXT_DIM
        elif active:
            bg, fg = COLOR_OK, QColor("#0a0a0a")
        else:
            bg, fg = QColor("#3a3a3a"), COLOR_TEXT_DIM
        label.setStyleSheet(
            f"background-color: {bg.name()}; color: {fg.name()}; "
            f"font-size: 8px; font-weight: bold; border-radius: 2px;"
        )

    def set_active(self, active: str, enabled: bool = True):
        """`active` is 'A', 'B', or None (unknown / not receiving)."""
        self._set_square_style(self.sq_a, active == "A", enabled)
        self._set_square_style(self.sq_b, active == "B", enabled)


class BatteryGauge(QWidget):
    """Small horizontal battery icon with a fill percentage."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = None
        self._warning = False
        self.setFixedHeight(14)
        self.setMinimumWidth(STRIP_WIDTH - 12)

    def set_value(self, value, warning: bool = False):
        self._value = value
        self._warning = warning
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w = self.width() - 3  # leave room for the "nub"
        h = self.height()
        body = QRectF(0, 0, w, h)
        painter.setPen(COLOR_BORDER)
        painter.setBrush(QColor("#111111"))
        painter.drawRoundedRect(body, 2, 2)
        nub = QRectF(w, h * 0.28, 3, h * 0.44)
        painter.fillRect(nub, COLOR_BORDER)

        if self._value is not None:
            pct = max(0, min(100, self._value))
            fill_w = max(0.0, (w - 4) * (pct / 100.0))
            if self._warning or pct < 15:
                color = COLOR_BAD
            elif pct < 40:
                color = COLOR_WARN
            else:
                color = COLOR_OK
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(2, 2, fill_w, h - 4), 1, 1)
        painter.end()


class BatteryBlock(QWidget):
    """Caption + battery gauge + numeric percentage readout, stacked vertically."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(_caption_label("BATT"))
        self.gauge = BatteryGauge()
        layout.addWidget(self.gauge)
        self.value_label = _value_label()
        layout.addWidget(self.value_label)

    def set_value(self, value, warning: bool = False):
        self.gauge.set_value(value, warning)
        self.value_label.setText(f"{value}%" if value is not None else "--")


# ---------------------------------------------------------------------------
# Channel strips
# ---------------------------------------------------------------------------

class ChannelStripWidget(QFrame):
    """
    Shared skeleton for a channel strip: status dot + header, name label,
    and a type-specific content area (built by subclasses via
    `_build_content()`, which is expected to end with its own bottom readout
    line -- e.g. frequency -- rather than a separate generic footer row).
    Subclasses implement `_build_content()` and `apply_reading()`.
    """

    def __init__(self, header: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(STRIP_WIDTH, STRIP_HEIGHT)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._enabled_state = True
        self._connected = False
        self._simulated = False
        self._meter_blocks = []   # populated by subclasses, used by set_enabled_state

        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(4, 4, 4, 4)
        self._outer.setSpacing(3)

        top_row = QHBoxLayout()
        top_row.setSpacing(2)
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(8, 8)
        top_row.addWidget(self.status_dot)
        self.header_label = QLabel(header)
        self.header_label.setStyleSheet(f"color: {COLOR_TEXT_DIM.name()}; font-size: 9px;")
        top_row.addWidget(self.header_label)
        top_row.addStretch(1)
        self._outer.addLayout(top_row)

        self.name_label = QLabel("--")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet(f"color: {COLOR_TEXT.name()}; font-size: 10px; "
                                      "font-weight: bold;")
        self.name_label.setFixedHeight(20)
        self._outer.addWidget(self.name_label)

        self._build_content(self._outer)

        self._apply_frame_style()

    def _build_content(self, outer: QVBoxLayout):  # pragma: no cover - overridden
        raise NotImplementedError

    def _apply_frame_style(self):
        bg = COLOR_BG if self._enabled_state else COLOR_BG_DISABLED
        self.setStyleSheet(
            f"QFrame {{ background-color: {bg.name()}; border: 1px solid {COLOR_BORDER.name()}; "
            f"border-radius: 3px; }}"
        )

    def set_enabled_state(self, enabled: bool):
        self._enabled_state = enabled
        for block in self._meter_blocks:
            block.set_enabled_state(enabled)
        self.setVisible(enabled)
        self._apply_frame_style()

    def set_connected(self, connected: bool, simulated: bool = None):               # type: ignore
        """
        Status dot: green = connected, red = disconnected, orange = this
        channel is simulated (regardless of `connected`, since a simulated
        client always reports itself connected -- orange is the signal that
        distinguishes "real, live data" from "made up for testing").

        `simulated` is sticky: apply_reading() passes it explicitly each
        time; the direct connection_changed→set_connected wiring (used so a
        real device dropping offline updates the dot even without a fresh
        reading) only passes `connected`, and simply reuses whatever
        simulated-ness was last set.
        """
        self._connected = connected
        if simulated is not None:
            self._simulated = simulated
        if self._simulated:
            color = COLOR_SIM
        else:
            color = COLOR_OK if connected else COLOR_BAD
        self.status_dot.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")

    def _set_warning_style(self, warning: bool):
        color = COLOR_WARN if warning else COLOR_TEXT
        self.name_label.setStyleSheet(f"color: {color.name()}; font-size: 10px; font-weight: bold;")

    def apply_reading(self, reading: DeviceReading):  # pragma: no cover - overridden
        raise NotImplementedError


class WirelessMicChannelWidget(ChannelStripWidget):
    """
    EW-DX EM2 receiver channel: diversity A/B squares, RF level (dBm), LQI
    (0-100%), AF level, and battery.
    """

    def __init__(self, channel_label: str, parent=None):
        super().__init__(header=channel_label, parent=parent)

    def _build_content(self, outer: QVBoxLayout):
        # [A][B] diversity squares sit directly above the RF meter
        self.diversity = DiversitySquares()
        outer.addWidget(self.diversity)

        # RF / LQI / AF bars side by side (WSM / Wireless Workbench style), each
        # captioned. Numeric values go in the readout lines below, so the bars
        # themselves stay tall enough to actually read at a glance.
        meter_row = QHBoxLayout()
        meter_row.setSpacing(4)
        self.rf_meter = MeterBlock("RF", "level", show_value=False)
        meter_row.addWidget(self.rf_meter)
        self.lqi_meter = MeterBlock("LQI", "level", show_value=False)
        meter_row.addWidget(self.lqi_meter)
        self.af_meter = MeterBlock("AF", "af", show_value=True)
        meter_row.addWidget(self.af_meter)
        outer.addLayout(meter_row, stretch=1)

        self.rf_readout = _readout_label()
        outer.addWidget(self.rf_readout)
        self.lqi_readout = _readout_label()
        outer.addWidget(self.lqi_readout)

        # extra breathing room above the battery gauge, per request
        outer.addSpacing(10)

        self.battery = BatteryBlock()
        outer.addWidget(self.battery)

        # Frequency, at the bottom -- same spot/pattern as the IEM strip.
        self.freq_readout = _readout_label()
        outer.addWidget(self.freq_readout)

        self._meter_blocks = [self.rf_meter, self.lqi_meter, self.af_meter]

    def apply_reading(self, reading: DeviceReading):
        self.set_connected(reading.connected, reading.simulated)
        self.name_label.setText(reading.name or "--")

        self.diversity.set_active(reading.diversity_active,                     # type: ignore
                                  enabled=self._enabled_state)

        # RF is reported in dBm; map onto the bar's 0-100% fill for the visual
        # meter only (RF_DBM_FLOOR..RF_DBM_CEILING -> empty..full).
        rf_pct = None
        if reading.rf_dbm is not None:
            span = RF_DBM_CEILING - RF_DBM_FLOOR
            rf_pct = max(0.0, min(100.0, (reading.rf_dbm - RF_DBM_FLOOR) / span * 100.0))
        self.rf_meter.set_value(rf_pct)
        self.rf_readout.setText(
            f"RF {reading.rf_dbm:.0f} dBm" if reading.rf_dbm is not None else "RF --")

        self.lqi_meter.set_value(reading.lqi)
        self.lqi_readout.setText(
            f"LQI {reading.lqi}%" if reading.lqi is not None else "LQI --")

        af_text = f"{reading.af_dbfs:.0f}" if reading.af_dbfs is not None else "--"
        self.af_meter.set_value(reading.af_peak, af_text)

        self.battery.set_value(reading.battery_percent, reading.battery_warning)

        # Bottom line: MUTE takes priority (most urgent); otherwise the
        # channel's tuned frequency, same convention as the IEM strip.
        if reading.muted:
            self.freq_readout.setText("MUTE")
        elif reading.frequency_mhz:
            self.freq_readout.setText(f"{reading.frequency_mhz:.3f} MHz")
        else:
            self.freq_readout.setText("-- MHz")

        self._set_warning_style(reading.rf_warning or reading.battery_warning
                                or _has_warning_text(reading.warnings))


class IemChannelWidget(ChannelStripWidget):
    """
    IEM G4 channel: transmitter-side, so no RF meter or battery -- just
    frequency and stereo AF level (L / R).
    """

    def __init__(self, channel_label: str, parent=None):
        super().__init__(header=channel_label, parent=parent)

    def _build_content(self, outer: QVBoxLayout):
        # Stereo AF only -- captioned L / R bars side by side. No RF meter and
        # no battery gauge: an IEM G4 transmitter has neither to report.
        af_row = QHBoxLayout()
        af_row.setSpacing(6)
        self.af_l_meter = MeterBlock("L", "af", show_value=False)
        af_row.addWidget(self.af_l_meter)
        self.af_r_meter = MeterBlock("R", "af", show_value=False)
        af_row.addWidget(self.af_r_meter)
        outer.addLayout(af_row, stretch=1)

        self.freq_readout = _readout_label()
        outer.addWidget(self.freq_readout)

        self._meter_blocks = [self.af_l_meter, self.af_r_meter]

    def apply_reading(self, reading: DeviceReading):
        self.set_connected(reading.connected, reading.simulated)
        self.name_label.setText(reading.name or "--")

        self.af_l_meter.set_value(reading.af_l)
        self.af_r_meter.set_value(reading.af_r)

        # MUTE takes priority (most urgent); otherwise the tuned frequency.
        if reading.muted:
            self.freq_readout.setText("MUTE")
        elif reading.frequency_mhz:
            self.freq_readout.setText(f"{reading.frequency_mhz:.3f} MHz")
        else:
            self.freq_readout.setText("-- MHz")

        self._set_warning_style(_has_warning_text(reading.warnings))


# ---------------------------------------------------------------------------
# Device row: builds/owns the grid of channel strips + their network clients
# ---------------------------------------------------------------------------

class DeviceRow(QWidget):
    """
    Builds and owns the full set of channel strips plus their network
    clients, laid out in a fixed 4-column grid (`deviceRowLayout`, a
    QGridLayout) that is the contents widget of a QScrollArea.

    Fill order: enabled IEM G4 channels first, then enabled EW-DX EM2 mic
    channels, filling left-to-right / top-to-bottom -- so with all 4 IEM
    slots and mic slots 1-2 enabled you get:

        row 0:  IEM1  IEM2  IEM3  IEM4
        row 1:  Mic1  Mic2   --    --

    `rows_used` (1 or 2) reflects how many grid rows are actually occupied,
    and `layout_changed(rows)` fires on every rebuild so MainWindow can
    grow/shrink the surrounding QGroupBox (and push the web view down/up)
    to match.
    """

    layout_changed = Signal(int)   # rows_used, after a rebuild

    def __init__(self, settings, layout: QGridLayout, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.layout: QGridLayout = layout
        self._widgets = []   # list[ChannelStripWidget] (or the placeholder QLabel)
        self._clients = []   # list[DeviceClientBase]
        # Shares one SSCEM2Device per IP across mic slots (rx1/rx2 of the same
        # physical EM2) -- see device_network.DeviceRegistry. Recreated on
        # every rebuild since IPs may have changed in Preferences.
        self._registry = DeviceRegistry()
        self.rows_used = 1
        self.rebuild_from_settings()

    def rebuild_from_settings(self):
        self._teardown()

        devices_enabled = str(self.settings.get("DEVICES_ENABLED", default="true",
                                                section="network")).lower() in ("1", "true", "yes",
                                                                                "on")
        poll_ms = self.settings.get("POLL_INTERVAL_MS", default=1000, cast=int, section="network")
        simulate = str(self.settings.get("SIMULATE_DEVICES", default="true",
                                         section="network")).lower() in ("1", "true", "yes", "on")

        # Build the ordered list of enabled channels first: IEM G4 (1-4),
        # then EW-DX EM2 mic channels (1-4). Fill order = this list order.
        # Skipped entirely if the whole feature is switched off.
        enabled_devices = []
        if devices_enabled:
            for i in range(1, 5):
                if str(self.settings.get(f"IEM{i}_ENABLED", default="false",
                                         section="iem")).lower() in ("1", "true", "yes", "on"):
                    enabled_devices.append(("iem", i, f"IEM {i}"))
            for i in range(1, 5):
                if str(self.settings.get(f"MIC{i}_ENABLED", default="false",
                                         section="wireless_mics")).lower() in ("1", "true", "yes",
                                                                               "on"):
                    enabled_devices.append(("mic", i, f"EM2 {i}"))

        for index, (kind, slot, header_label) in enumerate(enabled_devices):
            row, col = divmod(index, GRID_COLUMNS)
            section = "iem" if kind == "iem" else "wireless_mics"
            prefix = "IEM" if kind == "iem" else "MIC"
            default_port = G4_PORT if kind == "iem" else SSC_PORT
            name = self.settings.get(f"{prefix}{slot}_NAME",
                                     default=header_label,
                                     section=section)
            ip = self.settings.get(f"{prefix}{slot}_IP",
                                   default="", section=section)
            port = self.settings.get(f"{prefix}{slot}_PORT",
                                     default=default_port,
                                     cast=int,
                                     section=section)
            channel = self.settings.get(f"{prefix}{slot}_CHANNEL",
                                        default=1,
                                        cast=int,
                                        section=section)
            self._add_device(kind, header_label, name, ip, port, channel, poll_ms, simulate, row,
                             col)

        if enabled_devices:
            self.rows_used = min(GRID_MAX_ROWS, math.ceil(len(enabled_devices) / GRID_COLUMNS))
        else:
            # Collapsed state: no channel strips at all, just a short message
            # -- and group_devices_height(0) shrinks the surrounding group
            # (and grows the web view into the freed space) to match.
            self.rows_used = 0
            if not devices_enabled:
                message = "Sennheiser IEM / Wireless Mics disabled\n(Preferences \u2192 General)"
            else:
                message = "No IEM / mic channels enabled\n(Preferences \u2192 IEM / Wireless Mics)"
            placeholder = QLabel(message)
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet(f"color: {COLOR_TEXT_DIM.name()}; font-size: 10px;")
            self.layout.addWidget(placeholder, 0, 0, 1, GRID_COLUMNS)
            self._widgets.append(placeholder)

        self.layout_changed.emit(self.rows_used)

    def _add_device(self, kind, header_label, name, ip, port, channel, poll_ms, simulate, row, col):
        if kind == "mic":
            widget = WirelessMicChannelWidget(header_label)
        else:
            widget = IemChannelWidget(header_label)
        self.layout.addWidget(widget, row, col)
        self._widgets.append(widget)

        client = make_client(kind, name, ip, port, channel, poll_ms, simulate,
                             registry=self._registry, parent=self)
        client.reading_changed.connect(widget.apply_reading)
        client.connection_changed.connect(widget.set_connected)
        client.start()
        self._clients.append(client)

    def _teardown(self):
        for client in self._clients:
            try:
                client.stop()
            except Exception:
                pass
            client.deleteLater()
        self._clients = []
        for widget in self._widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
        self._widgets = []
        # belt-and-suspenders: drop anything else left in the grid layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget() is not None:                                           # type: ignore
                item.widget().deleteLater()                                         # type: ignore
        # Close every shared SSCEM2Device socket and start fresh -- IPs may
        # have changed in Preferences since the last build.
        self._registry.close_all()
        self._registry = DeviceRegistry()
