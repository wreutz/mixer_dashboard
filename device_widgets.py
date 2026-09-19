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

# Height for an IEM strip with AF display disabled (name + frequency only,
# no meters at all) -- computed the same way as STRIP_HEIGHT, by simulating
# the actual QVBoxLayout item stack rather than guessed.
IEM_STRIP_HEIGHT_COMPACT = 63

# RF is reported in dBm, but the bar needs a 0-100% fill. This is the display
# window only -- it does not clamp or alter the dBm value shown in the readout.
# Widen/narrow it if your EM2s sit in a different part of the range in practice.
RF_DBM_FLOOR = -95.0     # bar empty at or below this
RF_DBM_CEILING = -25.0   # bar full at or above this

# G4 reports IEM AF level as 0-100% ("at 0 dB", per TI 1254 v1.0), not dBFS.
# We convert to an approximate dB scale via 20*log10(pct/100) -- 100% -> 0dB,
# halving amplitude -> -6dB, etc. -- since Sennheiser doesn't publish the
# exact curve WSM itself uses internally.
#
# IEM_AF_DB_FLOOR (-135) is the absolute clamp for the *readout number* --
# avoids -infinity at 0%, and legitimately shows near-silence as a very low
# number. IEM_AF_BAR_DB_FLOOR/CEILING is a SEPARATE, much narrower window
# for the *bar fill* -- comparing against real WSM side by side, its meter's
# visible tick marks (-10/-20/-30dB) imply a scale only tens of dB wide, not
# 135dB wide. Mapping the bar through -135..0 made it read almost empty for
# perfectly normal signal levels; a receiver at -10dB would only reach ~7%
# up a -135-tall bar. -40..0 is an estimate from where WSM's ticks stop
# being visible in that comparison, not a documented value -- adjust it if
# it's still off, and note that RF_DBM_FLOOR/CEILING above is the same
# pattern (a narrow *display* window, independent of the raw value/readout).
IEM_AF_DB_FLOOR = -135.0
IEM_AF_BAR_DB_FLOOR = -40.0
IEM_AF_BAR_DB_CEILING = 0.0


def _af_pct_to_db(pct):
    """Raw 0-100% (linear amplitude, per TI 1254) -> dB, floored at
    IEM_AF_DB_FLOOR. None in, None out."""
    if pct is None:
        return None
    if pct <= 0:
        return IEM_AF_DB_FLOOR
    return max(IEM_AF_DB_FLOOR, 20.0 * math.log10(pct / 100.0))


def _af_db_to_text(db) -> str:
    return "--" if db is None else f"{db:.0f}"


def _af_db_to_bar_pct(db):
    """
    Maps dB onto the bar's 0-100% fill using IEM_AF_BAR_DB_FLOOR/CEILING --
    a log-scaled bar, matching the log-scaled number underneath it (and
    matching what a real dB meter, WSM included, actually looks like) --
    rather than the raw linear percentage, which doesn't correspond to
    "how loud something looks on a meter" at all.
    """
    if db is None:
        return None
    span = IEM_AF_BAR_DB_CEILING - IEM_AF_BAR_DB_FLOOR
    return max(0.0, min(100.0, (db - IEM_AF_BAR_DB_FLOOR) / span * 100.0))

# Geometry knobs shared with MainWindow's dynamic resize calculation (kept
# here, next to STRIP_HEIGHT, so the two stay in sync).
GRID_ROW_SPACING = 4
GRID_MARGIN_TOP = 2
GRID_MARGIN_BOTTOM = 2
GROUPBOX_TITLE_OFFSET = 20   # vertical space a QGroupBox title reserves above its content
GROUP_BOTTOM_PADDING = 6     # a little breathing room / scrollbar allowance
EMPTY_MESSAGE_HEIGHT = 40    # collapsed height: just enough for the 2-line "nothing enabled" message


def group_devices_height_for_rows(row_heights) -> int:
    """
    Height (px) the IEM/Mic QGroupBox needs to show rows whose *actual*
    content heights are given in `row_heights` (one entry per occupied grid
    row, tallest widget in that row). Rows aren't assumed uniform anymore:
    an IEM row can be shorter than a Mic row when IEM's AF display is
    disabled (IEM_STRIP_HEIGHT_COMPACT instead of STRIP_HEIGHT), so
    MainWindow needs the real per-row heights, not just a row count, to
    grow/shrink groupDevices (and push the web view down/up) correctly.

    An empty list is the collapsed state -- no channels enabled, or the
    whole feature switched off via DEVICES_ENABLED -- which needs only
    enough room for a short message, not a full row of channel strips.
    """
    if not row_heights:
        return GROUPBOX_TITLE_OFFSET + EMPTY_MESSAGE_HEIGHT + GROUP_BOTTOM_PADDING
    content_h = (sum(row_heights)
                 + max(0, len(row_heights) - 1) * GRID_ROW_SPACING
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
    """
    A small vertical segmented level meter (used for RF, LQI, AF).

    `dense=True` (used for AF meters) computes the segment count from the
    bar's actual available height at paint time instead of using a fixed
    count, aiming for ~3px segments with a 1px gap -- a much finer,
    closer-to-continuous look (WSM's own meters read this way) than the
    fixed 6-segment bar RF/LQI still use, which was fine for a coarse
    signal-quality indicator but far too coarse for an audio level meter.
    """

    DENSE_TARGET_SEGMENT_PX = 3.0
    DENSE_GAP_PX = 1
    DENSE_MIN_SEGMENTS = 10
    DENSE_MAX_SEGMENTS = 60

    def __init__(self, kind: str, segments: int = 6, dense: bool = False, parent=None):
        super().__init__(parent)
        self.kind = kind  # "level" (RF/LQI) or "af"
        self.segments = segments   # used only when dense=False
        self.dense = dense
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

    def _segment_count(self, height: float) -> int:
        if not self.dense:
            return self.segments
        raw = int(height // (self.DENSE_TARGET_SEGMENT_PX + self.DENSE_GAP_PX))
        return max(self.DENSE_MIN_SEGMENTS, min(self.DENSE_MAX_SEGMENTS, raw))

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w = self.width()
        h = self.height()
        gap = self.DENSE_GAP_PX if self.dense else 2
        segments = self._segment_count(h)
        seg_h = (h - gap * (segments - 1)) / segments
        lit_count = round((self._value / 100.0) * segments)
        for i in range(segments):
            # index 0 = bottom segment
            y = h - (i + 1) * seg_h - i * gap
            rect = QRectF(0, y, w, seg_h)
            lit = i < lit_count
            if not self._enabled_state:
                color = COLOR_OFF
            elif lit:
                color = _segment_color(i, lit_count, segments, self.kind)
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

    def __init__(self, caption: str, kind: str, show_value: bool = True, dense: bool = False, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(_caption_label(caption))
        self.bar = SegmentBar(kind, dense=dense)
        layout.addWidget(self.bar, stretch=1)
        self.value_label = _value_label() if show_value else None
        if self.value_label is not None:
            layout.addWidget(self.value_label)

    def set_value(self, value, text: str = None):
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
        self.name_label.setStyleSheet(f"color: {COLOR_TEXT.name()}; font-size: 10px; font-weight: bold;")
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

    def set_connected(self, connected: bool, simulated: bool = None):
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
        self.af_meter = MeterBlock("AF", "af", show_value=False, dense=True)
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

        self.diversity.set_active(reading.diversity_active, enabled=self._enabled_state)

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

        self.af_meter.set_value(reading.af_peak)

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
    frequency and stereo AF level (L / R). `af_enabled=False` (the
    Preferences -> IEM "Show AF level" switch) drops the AF section
    entirely and shrinks the strip to IEM_STRIP_HEIGHT_COMPACT, showing
    only the name and frequency.
    """

    def __init__(self, channel_label: str, af_enabled: bool = True, parent=None):
        # Set before super().__init__() -- _build_content() (called from
        # within it) needs to know which layout to build.
        self._af_enabled = af_enabled
        super().__init__(header=channel_label, parent=parent)

    def _build_content(self, outer: QVBoxLayout):
        if not self._af_enabled:
            self.af_l_meter = None
            self.af_r_meter = None
            self.freq_readout = _readout_label()
            outer.addWidget(self.freq_readout)
            outer.addStretch(1)
            self._meter_blocks = []
            # Overrides the STRIP_HEIGHT the base class already applied.
            self.setFixedSize(STRIP_WIDTH, IEM_STRIP_HEIGHT_COMPACT)
            return

        # Stereo AF only -- captioned L / R bars side by side, each with its
        # own dB readout underneath (narrow enough that "-135" still fits
        # without widening the column -- see _af_db_to_text). No RF
        # meter and no battery gauge: an IEM G4 transmitter has neither to
        # report.
        af_row = QHBoxLayout()
        af_row.setSpacing(6)
        self.af_l_meter = MeterBlock("L", "af", show_value=True, dense=True)
        af_row.addWidget(self.af_l_meter)
        self.af_r_meter = MeterBlock("R", "af", show_value=True, dense=True)
        af_row.addWidget(self.af_r_meter)
        outer.addLayout(af_row, stretch=1)

        self.freq_readout = _readout_label()
        outer.addWidget(self.freq_readout)

        self._meter_blocks = [self.af_l_meter, self.af_r_meter]

    def apply_reading(self, reading: DeviceReading):
        self.set_connected(reading.connected, reading.simulated)
        self.name_label.setText(reading.name or "--")

        if self._af_enabled:
            db_l = _af_pct_to_db(reading.af_l)
            db_r = _af_pct_to_db(reading.af_r)
            self.af_l_meter.set_value(_af_db_to_bar_pct(db_l), _af_db_to_text(db_l))
            self.af_r_meter.set_value(_af_db_to_bar_pct(db_r), _af_db_to_text(db_r))

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

    Rows are no longer assumed uniform height: an IEM row can be shorter
    than a Mic row when IEM's AF display is switched off in Preferences
    (IEM_STRIP_HEIGHT_COMPACT instead of STRIP_HEIGHT). `layout_changed(px)`
    fires on every rebuild carrying the *actual* pixel height groupDevices
    needs (computed from the real per-row heights via
    group_devices_height_for_rows()), so MainWindow can grow/shrink it (and
    push the web view down/up) correctly regardless of that mix. `rows_used`
    is still tracked too, informationally.
    """

    layout_changed = Signal(int)   # group height in px, after a rebuild

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
        self.group_height = 0
        self.rebuild_from_settings()

    def rebuild_from_settings(self):
        self._teardown()

        devices_enabled = str(self.settings.get("DEVICES_ENABLED", default="true",
                                                  section="network")).lower() in ("1", "true", "yes", "on")
        poll_ms = self.settings.get("POLL_INTERVAL_MS", default=1000, cast=int, section="network")
        simulate = str(self.settings.get("SIMULATE_DEVICES", default="true",
                                          section="network")).lower() in ("1", "true", "yes", "on")
        # Section-level switch (not per-slot): Preferences -> IEM -> "Show AF
        # level". Off means no L/R AF meters on any IEM strip, and no work
        # done to populate af_l/af_r either -- see G4IemChannelClient.
        iem_af_enabled = str(self.settings.get("IEM_AF_ENABLED", default="true",
                                                section="iem")).lower() in ("1", "true", "yes", "on")

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
                                          section="wireless_mics")).lower() in ("1", "true", "yes", "on"):
                    enabled_devices.append(("mic", i, f"EM2 {i}"))

        row_heights = {}   # row index -> tallest widget height placed in it

        for index, (kind, slot, default_name) in enumerate(enabled_devices):
            row, col = divmod(index, GRID_COLUMNS)
            section = "iem" if kind == "iem" else "wireless_mics"
            prefix = "IEM" if kind == "iem" else "MIC"
            default_port = G4_PORT if kind == "iem" else SSC_PORT
            # The configured Name from Preferences -- this is now what the
            # widget's topmost label shows (see _add_device); the device's
            # own reported name, fetched over the network, shows on the
            # line below it instead. They're two different things and were
            # previously conflated (the header showed a hardcoded slot
            # label, and the name line silently fell back to this
            # configured value whenever the device hadn't reported its own
            # name yet -- see device_network.py's name-fallback removal).
            configured_name = self.settings.get(f"{prefix}{slot}_NAME", default=default_name, section=section)
            ip = self.settings.get(f"{prefix}{slot}_IP", default="", section=section)
            port = self.settings.get(f"{prefix}{slot}_PORT", default=default_port, cast=int, section=section)
            if kind == "iem":
                # SR IEM G4 has no channel-select concept -- one physical
                # unit is one channel -- so there's no per-slot setting for
                # it (removed from Preferences -> IEM entirely). A fixed 1
                # is passed through for interface symmetry with mic; it's
                # never read on the IEM side.
                channel = 1
            else:
                channel = self.settings.get(f"{prefix}{slot}_CHANNEL", default=1, cast=int, section=section)
            widget_height = self._add_device(kind, configured_name, ip, port, channel, poll_ms,
                                              simulate, iem_af_enabled, row, col)
            row_heights[row] = max(row_heights.get(row, 0), widget_height)

        if enabled_devices:
            self.rows_used = min(GRID_MAX_ROWS, math.ceil(len(enabled_devices) / GRID_COLUMNS))
        else:
            # Collapsed state: no channel strips at all, just a short message
            # -- group_devices_height_for_rows([]) shrinks the surrounding
            # group (and grows the web view into the freed space) to match.
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

        ordered_row_heights = [row_heights[r] for r in sorted(row_heights)]
        self.group_height = group_devices_height_for_rows(ordered_row_heights)
        self.layout_changed.emit(self.group_height)

    def _add_device(self, kind, name, ip, port, channel, poll_ms, simulate, iem_af_enabled, row, col):
        """Returns the widget's actual (fixed) height, for row-height tracking."""
        if kind == "mic":
            widget = WirelessMicChannelWidget(name)
        else:
            widget = IemChannelWidget(name, af_enabled=iem_af_enabled)
        self.layout.addWidget(widget, row, col)
        self._widgets.append(widget)

        af_enabled_kwarg = {"af_enabled": iem_af_enabled} if kind == "iem" else {}
        client = make_client(kind, name, ip, port, channel, poll_ms, simulate,
                              registry=self._registry, parent=self, **af_enabled_kwarg)
        client.reading_changed.connect(widget.apply_reading)
        client.connection_changed.connect(widget.set_connected)
        client.start()
        self._clients.append(client)
        return widget.height()

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
            if item.widget() is not None:
                item.widget().deleteLater()
        # Close every shared SSCEM2Device socket and start fresh -- IPs may
        # have changed in Preferences since the last build.
        self._registry.close_all()
        self._registry = DeviceRegistry()
