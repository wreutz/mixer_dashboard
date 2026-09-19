"""
preferences.py

Embedded preferences panel (shown/hidden over the main window rather than a
modal dialog, for kiosk/touch operation). Wraps Ui_PreferencesDialogForm and
handles:
  - General tab: timecode source (MIDI/OSC), MIDI port, OSC host/port/address/
    fps fallback, device simulation toggle + poll interval.
  - IEM tab: a section-level "Show AF level" switch, plus 4 IEM G4 slots
    (enabled, name, ip, port -- no channel field, an SR IEM G4 has no
    channel-select concept).
  - Wireless Mics tab: 4 EW-DX EM2 channel slots (enabled, name, ip, port,
    channel) -- 2 enabled by default today, 2 more ready for "future" units.

On OK: writes everything to SettingsManager, saves settings.ini, and emits
`settingsApplied` so MainWindow can tell the timecode reader and the device
row to reload. On Cancel: discards edits and just hides.
"""

from __future__ import annotations

import mido
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from assets.preferences_dialog import Ui_PreferencesDialogForm


def _to_bool(value) -> bool:
    return str(value).strip().lower() in ("1", "true", "yes", "on")


class PreferencesPanel(QWidget):
    settingsApplied = Signal()

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.ui = Ui_PreferencesDialogForm()
        self.ui.setupUi(self)

        self.ui.btn_ok.clicked.connect(self._on_ok)
        self.ui.btn_cancel.clicked.connect(self._on_cancel)
        self.ui.rb_midi.toggled.connect(self._update_source_enabled_state)
        self.ui.cb_devices_enabled.toggled.connect(self._update_devices_enabled_state)
        self.ui.cb_simulate_devices.toggled.connect(self._update_simulate_enabled_state)

    # ------------------------------------------------------------------
    def showEvent(self, event):
        self._load_from_settings()
        super().showEvent(event)

    def _update_source_enabled_state(self):
        is_midi = self.ui.rb_midi.isChecked()
        self.ui.groupMIDI.setEnabled(is_midi)
        self.ui.groupOSC.setEnabled(not is_midi)

    def _update_devices_enabled_state(self):
        enabled = self.ui.cb_devices_enabled.isChecked()
        self.ui.cb_simulate_devices.setEnabled(enabled)
        self.ui.spin_poll_interval.setEnabled(enabled)
        self.ui.tabWidget.setTabEnabled(self.ui.tabWidget.indexOf(self.ui.tabIem), enabled)
        self.ui.tabWidget.setTabEnabled(self.ui.tabWidget.indexOf(self.ui.tabMics), enabled)

    def _update_simulate_enabled_state(self):
        simulate = self.ui.cb_simulate_devices.isChecked()
        for prefix in ("iem", "mic"):
            for i in range(1, 5):
                for suffix in ("ip", "port"):
                    getattr(self.ui, f"{prefix}_{suffix}_{i}").setEnabled(not simulate)

    # ------------------------------------------------------------------
    def _load_from_settings(self):
        s = self.settings

        # -- General: timecode source --
        source = (s.get("TIMECODE_SOURCE", default="midi") or "midi").lower()
        self.ui.rb_midi.setChecked(source != "osc")
        self.ui.rb_osc.setChecked(source == "osc")

        self.ui.cb_midi_ports.clear()
        try:
            self.ui.cb_midi_ports.addItems(mido.get_input_names())
        except Exception:
            pass
        current_port = s.get("MIDI_PORT_NAME", default="")
        if current_port:
            idx = self.ui.cb_midi_ports.findText(current_port)
            if idx >= 0:
                self.ui.cb_midi_ports.setCurrentIndex(idx)
            else:
                self.ui.cb_midi_ports.setEditText(current_port)

        self.ui.le_osc_host.setText(str(s.get("OSC_LISTEN_HOST", default="0.0.0.0")))
        self.ui.spin_osc_port.setValue(int(s.get("OSC_LISTEN_PORT", default=9001, cast=int)))
        self.ui.le_osc_addr.setText(str(s.get("OSC_ADDRESS", default="/timecode")))
        self.ui.le_fps_fallback.setText(str(s.get("OSC_FRAMERATE_FALLBACK", default=30)))

        devices_enabled = _to_bool(s.get("DEVICES_ENABLED", default="true", section="network"))
        self.ui.cb_devices_enabled.setChecked(devices_enabled)
        simulate = _to_bool(s.get("SIMULATE_DEVICES", default="true", section="network"))
        self.ui.cb_simulate_devices.setChecked(simulate)
        self.ui.spin_poll_interval.setValue(
            int(s.get("POLL_INTERVAL_MS", default=1000, cast=int, section="network")))

        # -- IEM tab --
        self.ui.cb_iem_af_enabled.setChecked(
            _to_bool(s.get("IEM_AF_ENABLED", default="true", section="iem")))
        for i in range(1, 5):
            getattr(self.ui, f"iem_enabled_{i}").setChecked(
                _to_bool(s.get(f"IEM{i}_ENABLED", default="false", section="iem")))
            getattr(self.ui, f"iem_name_{i}").setText(
                str(s.get(f"IEM{i}_NAME", default=f"IEM {i}", section="iem")))
            getattr(self.ui, f"iem_ip_{i}").setText(
                str(s.get(f"IEM{i}_IP", default="", section="iem")))
            getattr(self.ui, f"iem_port_{i}").setValue(
                int(s.get(f"IEM{i}_PORT", default=53212, cast=int, section="iem")))  # G4 Media Control Protocol

        # -- Wireless Mics tab --
        for i in range(1, 5):
            getattr(self.ui, f"mic_enabled_{i}").setChecked(
                _to_bool(s.get(f"MIC{i}_ENABLED", default="false", section="wireless_mics")))
            getattr(self.ui, f"mic_name_{i}").setText(
                str(s.get(f"MIC{i}_NAME", default=f"Mic {i}", section="wireless_mics")))
            getattr(self.ui, f"mic_ip_{i}").setText(
                str(s.get(f"MIC{i}_IP", default="", section="wireless_mics")))
            getattr(self.ui, f"mic_port_{i}").setValue(
                int(s.get(f"MIC{i}_PORT", default=45, cast=int, section="wireless_mics")))  # SSC (legacy)
            getattr(self.ui, f"mic_channel_{i}").setValue(
                int(s.get(f"MIC{i}_CHANNEL", default=1, cast=int, section="wireless_mics")))

        self._update_source_enabled_state()
        self._update_devices_enabled_state()
        self._update_simulate_enabled_state()

    # ------------------------------------------------------------------
    def _save_to_settings(self):
        s = self.settings

        s.set("TIMECODE_SOURCE", "midi" if self.ui.rb_midi.isChecked() else "osc")
        s.set("MIDI_PORT_NAME", self.ui.cb_midi_ports.currentText())
        s.set("OSC_LISTEN_HOST", self.ui.le_osc_host.text())
        s.set("OSC_LISTEN_PORT", self.ui.spin_osc_port.value())
        s.set("OSC_ADDRESS", self.ui.le_osc_addr.text())
        s.set("OSC_FRAMERATE_FALLBACK", self.ui.le_fps_fallback.text() or "30")

        s.set("DEVICES_ENABLED", self.ui.cb_devices_enabled.isChecked(), section="network")
        s.set("SIMULATE_DEVICES", self.ui.cb_simulate_devices.isChecked(), section="network")
        s.set("POLL_INTERVAL_MS", self.ui.spin_poll_interval.value(), section="network")
        s.set("IEM_AF_ENABLED", self.ui.cb_iem_af_enabled.isChecked(), section="iem")

        for i in range(1, 5):
            s.set(f"IEM{i}_ENABLED", getattr(self.ui, f"iem_enabled_{i}").isChecked(), section="iem")
            s.set(f"IEM{i}_NAME", getattr(self.ui, f"iem_name_{i}").text(), section="iem")
            s.set(f"IEM{i}_IP", getattr(self.ui, f"iem_ip_{i}").text(), section="iem")
            s.set(f"IEM{i}_PORT", getattr(self.ui, f"iem_port_{i}").value(), section="iem")

        for i in range(1, 5):
            s.set(f"MIC{i}_ENABLED", getattr(self.ui, f"mic_enabled_{i}").isChecked(), section="wireless_mics")
            s.set(f"MIC{i}_NAME", getattr(self.ui, f"mic_name_{i}").text(), section="wireless_mics")
            s.set(f"MIC{i}_IP", getattr(self.ui, f"mic_ip_{i}").text(), section="wireless_mics")
            s.set(f"MIC{i}_PORT", getattr(self.ui, f"mic_port_{i}").value(), section="wireless_mics")
            s.set(f"MIC{i}_CHANNEL", getattr(self.ui, f"mic_channel_{i}").value(), section="wireless_mics")

        s.save()

    # ------------------------------------------------------------------
    def _on_ok(self):
        self._save_to_settings()
        self.hide()
        self.settingsApplied.emit()

    def _on_cancel(self):
        self.hide()
