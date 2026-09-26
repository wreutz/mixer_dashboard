# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
## Regenerate with:
##   pyside6-uic assets/preferences_dialog.ui -o assets/preferences_dialog.py
##
## NOTE: pyside6-uic normally emits one flat, fully unrolled setupUi() method
## with no loops. This hand-authored version produces the *exact same*
## objectNames/widget tree that the .ui file describes (so preferences.py can
## reference self.iem_enabled_1 .. self.mic_channel_4 etc. exactly as if it
## had been generated), but uses small loops for the four repeated IEM /
## Wireless-Mic slot groupboxes purely to keep this file maintainable by
## hand. If you have a PySide6 toolchain available, prefer regenerating this
## file for real via pyside6-uic against preferences_dialog.ui.
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtGui import (QBrush, QColor, QPalette)
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget, QVBoxLayout, QWidget)


# Mirrors the styleSheet property of PreferencesDialogForm in
# preferences_dialog.ui -- keep the two in sync.
PREFERENCES_STYLESHEET = u"""\
/* Explicit dark theme. The panel must not rely on the platform palette:
   on macOS (dark mode) the default text is light, but on the Raspberry Pi
   the platform palette is light, which painted black text on the dark
   background of this panel. Every colour used here is stated outright so
   the panel looks identical on both. */
#PreferencesDialogForm { background-color: #2a2a2a; }
#tabGeneral, #tabIem, #tabMics { background-color: #2a2a2a; }

QTabWidget::pane { background-color: #2a2a2a; border: 1px solid #555555; }
QTabBar::tab { background-color: #3a3a3a; color: #f0f0f0; border: 1px solid #555555; border-bottom: none; padding: 6px 10px; }
QTabBar::tab:selected { background-color: #2a2a2a; color: #ffffff; }
QTabBar::tab:disabled { color: #808080; }

QGroupBox { background-color: #2a2a2a; color: #f0f0f0; border: 1px solid #555555; border-radius: 4px; margin-top: 10px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 8px; padding: 0 4px; color: #f0f0f0; }
QGroupBox:disabled { color: #808080; border-color: #444444; }
QGroupBox::title:disabled { color: #808080; }

QLabel { background-color: transparent; color: #f0f0f0; }
QLabel:disabled { color: #808080; }

QCheckBox, QRadioButton { background-color: transparent; color: #f0f0f0; spacing: 8px; }
QCheckBox:disabled, QRadioButton:disabled { color: #808080; }
QCheckBox::indicator, QRadioButton::indicator { width: 18px; height: 18px; background-color: #1e1e1e; border: 1px solid #8a8a8a; }
QCheckBox::indicator { border-radius: 3px; }
QRadioButton::indicator { border-radius: 10px; }
QCheckBox::indicator:checked, QRadioButton::indicator:checked { background-color: #4a9eda; border: 1px solid #4a9eda; }
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled { background-color: #2b2b2b; border: 1px solid #5a5a5a; }
QCheckBox::indicator:checked:disabled, QRadioButton::indicator:checked:disabled { background-color: #4a6a85; border: 1px solid #4a6a85; }

QLineEdit, QComboBox, QSpinBox { background-color: #1e1e1e; color: #f0f0f0; border: 1px solid #555555; border-radius: 3px; padding: 3px 4px; selection-background-color: #2f6fa8; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled { background-color: #262626; color: #777777; border-color: #3c3c3c; }
QComboBox QAbstractItemView { background-color: #1e1e1e; color: #f0f0f0; border: 1px solid #555555; selection-background-color: #2f6fa8; selection-color: #ffffff; }

QFrame#frameButtons { background-color: #2a2a2a; border: 1px solid #555555; border-radius: 4px; }
QPushButton { background-color: #3a3a3a; color: #f0f0f0; border: 1px solid #666666; border-radius: 4px; padding: 6px 16px; }
QPushButton:pressed { background-color: #505050; }
QPushButton:disabled { color: #808080; border-color: #444444; }

QToolTip { background-color: #1e1e1e; color: #f0f0f0; border: 1px solid #555555; }
"""


def _dark_palette() -> QPalette:
    """The panel's colours, stated outright so native sub-controls
    (check marks, spin/drop-down arrows, frames) do not fall back to the
    platform palette -- which is light on the Raspberry Pi.
    Mirrors the palette property in preferences_dialog.ui."""
    palette = QPalette()
    common = {
        QPalette.ColorRole.WindowText: "#f0f0f0",
        QPalette.ColorRole.Button: "#3a3a3a",
        QPalette.ColorRole.Light: "#4a4a4a",
        QPalette.ColorRole.Midlight: "#3f3f3f",
        QPalette.ColorRole.Dark: "#1a1a1a",
        QPalette.ColorRole.Mid: "#444444",
        QPalette.ColorRole.Text: "#f0f0f0",
        QPalette.ColorRole.BrightText: "#ffffff",
        QPalette.ColorRole.ButtonText: "#f0f0f0",
        QPalette.ColorRole.Base: "#1e1e1e",
        QPalette.ColorRole.Window: "#2a2a2a",
        QPalette.ColorRole.Shadow: "#101010",
        QPalette.ColorRole.Highlight: "#2f6fa8",
        QPalette.ColorRole.HighlightedText: "#ffffff",
        QPalette.ColorRole.Link: "#4ea3e0",
        QPalette.ColorRole.LinkVisited: "#a06fd0",
        QPalette.ColorRole.AlternateBase: "#262626",
        QPalette.ColorRole.ToolTipBase: "#1e1e1e",
        QPalette.ColorRole.ToolTipText: "#f0f0f0",
        QPalette.ColorRole.PlaceholderText: "#8a8a8a",
    }
    disabled = {
        QPalette.ColorRole.WindowText: "#808080",
        QPalette.ColorRole.Text: "#777777",
        QPalette.ColorRole.ButtonText: "#808080",
        QPalette.ColorRole.Base: "#262626",
        QPalette.ColorRole.Button: "#333333",
        QPalette.ColorRole.Highlight: "#3f3f3f",
        QPalette.ColorRole.HighlightedText: "#b0b0b0",
        QPalette.ColorRole.PlaceholderText: "#6a6a6a",
        QPalette.ColorRole.BrightText: "#909090",
    }
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive,
                  QPalette.ColorGroup.Disabled):
        for role, color in common.items():
            if group is QPalette.ColorGroup.Disabled and role in disabled:
                color = disabled[role]
            brush = QBrush(QColor(color))
            brush.setStyle(Qt.BrushStyle.SolidPattern)
            palette.setBrush(group, role, brush)
    return palette


class Ui_PreferencesDialogForm(object):
    def setupUi(self, PreferencesDialogForm):
        if not PreferencesDialogForm.objectName():
            PreferencesDialogForm.setObjectName(u"PreferencesDialogForm")
        PreferencesDialogForm.resize(300, 640)

        PreferencesDialogForm.setPalette(_dark_palette())
        PreferencesDialogForm.setAutoFillBackground(True)
        PreferencesDialogForm.setStyleSheet(PREFERENCES_STYLESHEET)

        self.verticalLayout = QVBoxLayout(PreferencesDialogForm)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)

        self.tabWidget = QTabWidget(PreferencesDialogForm)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.tabWidget.setSizePolicy(sizePolicy)

        # ---------------------------------------------------------------
        # General tab
        # ---------------------------------------------------------------
        self.tabGeneral = QWidget()
        self.tabGeneral.setObjectName(u"tabGeneral")
        self.verticalLayoutGeneral = QVBoxLayout(self.tabGeneral)
        self.verticalLayoutGeneral.setObjectName(u"verticalLayoutGeneral")

        groupBoxSizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.groupTimecode = QGroupBox(self.tabGeneral)
        self.groupTimecode.setObjectName(u"groupTimecode")
        self.groupTimecode.setSizePolicy(groupBoxSizePolicy)
        self.hLayoutSource = QHBoxLayout(self.groupTimecode)
        self.hLayoutSource.setObjectName(u"hLayoutSource")
        self.hLayoutSource.setContentsMargins(-1, 24, -1, -1)
        self.rb_midi = QRadioButton(self.groupTimecode)
        self.rb_midi.setObjectName(u"rb_midi")
        self.hLayoutSource.addWidget(self.rb_midi)
        self.rb_osc = QRadioButton(self.groupTimecode)
        self.rb_osc.setObjectName(u"rb_osc")
        self.hLayoutSource.addWidget(self.rb_osc)
        self.verticalLayoutGeneral.addWidget(self.groupTimecode)

        self.groupMIDI = QGroupBox(self.tabGeneral)
        self.groupMIDI.setObjectName(u"groupMIDI")
        self.groupMIDI.setSizePolicy(groupBoxSizePolicy)
        self.formMIDI = QVBoxLayout(self.groupMIDI)
        self.formMIDI.setObjectName(u"formMIDI")
        self.formMIDI.setContentsMargins(8, 24, 8, 8)
        self.label_midi_port = QLabel(self.groupMIDI)
        self.label_midi_port.setObjectName(u"label_midi_port")
        self.label_midi_port.setAlignment(
            Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.formMIDI.addWidget(self.label_midi_port)
        self.cb_midi_ports = QComboBox(self.groupMIDI)
        self.cb_midi_ports.setObjectName(u"cb_midi_ports")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cb_midi_ports.setSizePolicy(sizePolicy1)
        self.cb_midi_ports.setEditable(True)
        self.formMIDI.addWidget(self.cb_midi_ports)
        self.verticalLayoutGeneral.addWidget(self.groupMIDI)

        self.groupOSC = QGroupBox(self.tabGeneral)
        self.groupOSC.setObjectName(u"groupOSC")
        self.groupOSC.setSizePolicy(groupBoxSizePolicy)
        self.formOSC = QFormLayout(self.groupOSC)
        self.formOSC.setObjectName(u"formOSC")
        self.formOSC.setContentsMargins(-1, 24, -1, -1)
        self.label_osc_host = QLabel(self.groupOSC)
        self.label_osc_host.setObjectName(u"label_osc_host")
        self.formOSC.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_osc_host)
        self.le_osc_host = QLineEdit(self.groupOSC)
        self.le_osc_host.setObjectName(u"le_osc_host")
        self.formOSC.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_osc_host)
        self.label_osc_port = QLabel(self.groupOSC)
        self.label_osc_port.setObjectName(u"label_osc_port")
        self.formOSC.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_osc_port)
        self.spin_osc_port = QSpinBox(self.groupOSC)
        self.spin_osc_port.setObjectName(u"spin_osc_port")
        self.spin_osc_port.setMinimum(1)
        self.spin_osc_port.setMaximum(65535)
        self.formOSC.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spin_osc_port)
        self.label_osc_addr = QLabel(self.groupOSC)
        self.label_osc_addr.setObjectName(u"label_osc_addr")
        self.formOSC.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_osc_addr)
        self.le_osc_addr = QLineEdit(self.groupOSC)
        self.le_osc_addr.setObjectName(u"le_osc_addr")
        self.formOSC.setWidget(2, QFormLayout.ItemRole.FieldRole, self.le_osc_addr)
        self.label_fps = QLabel(self.groupOSC)
        self.label_fps.setObjectName(u"label_fps")
        self.formOSC.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_fps)
        self.le_fps_fallback = QLineEdit(self.groupOSC)
        self.le_fps_fallback.setObjectName(u"le_fps_fallback")
        self.formOSC.setWidget(3, QFormLayout.ItemRole.FieldRole, self.le_fps_fallback)
        self.verticalLayoutGeneral.addWidget(self.groupOSC)

        self.groupNetworkDevices = QGroupBox(self.tabGeneral)
        self.groupNetworkDevices.setObjectName(u"groupNetworkDevices")
        self.groupNetworkDevices.setSizePolicy(groupBoxSizePolicy)
        self.formNetworkDevices = QFormLayout(self.groupNetworkDevices)
        self.formNetworkDevices.setObjectName(u"formNetworkDevices")
        self.formNetworkDevices.setContentsMargins(-1, 24, -1, -1)
        self.cb_devices_enabled = QCheckBox(self.groupNetworkDevices)
        self.cb_devices_enabled.setObjectName(u"cb_devices_enabled")
        self.formNetworkDevices.setWidget(0, QFormLayout.ItemRole.LabelRole, self.cb_devices_enabled)
        self.cb_simulate_devices = QCheckBox(self.groupNetworkDevices)
        self.cb_simulate_devices.setObjectName(u"cb_simulate_devices")
        self.formNetworkDevices.setWidget(1, QFormLayout.ItemRole.LabelRole, self.cb_simulate_devices)
        self.label_poll_interval = QLabel(self.groupNetworkDevices)
        self.label_poll_interval.setObjectName(u"label_poll_interval")
        self.formNetworkDevices.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_poll_interval)
        self.spin_poll_interval = QSpinBox(self.groupNetworkDevices)
        self.spin_poll_interval.setObjectName(u"spin_poll_interval")
        self.spin_poll_interval.setMinimum(200)
        self.spin_poll_interval.setMaximum(10000)
        self.spin_poll_interval.setSingleStep(100)
        self.formNetworkDevices.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spin_poll_interval)
        self.verticalLayoutGeneral.addWidget(self.groupNetworkDevices)

        self.verticalSpacerGeneral = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayoutGeneral.addItem(self.verticalSpacerGeneral)

        self.tabWidget.addTab(self.tabGeneral, u"")

        # ---------------------------------------------------------------
        # IEM tab (4 slots) and Wireless Mics tab (4 slots)
        # ---------------------------------------------------------------
        self.tabIem = QWidget()
        self.tabIem.setObjectName(u"tabIem")
        self.verticalLayoutIem = QVBoxLayout(self.tabIem)
        self.verticalLayoutIem.setObjectName(u"verticalLayoutIem")

        self.groupIemAf = QGroupBox(self.tabIem)
        self.groupIemAf.setObjectName(u"groupIemAf")
        self.formIemAf = QFormLayout(self.groupIemAf)
        self.formIemAf.setObjectName(u"formIemAf")
        self.formIemAf.setContentsMargins(-1, 20, -1, -1)
        self.cb_iem_af_enabled = QCheckBox(self.groupIemAf)
        self.cb_iem_af_enabled.setObjectName(u"cb_iem_af_enabled")
        self.formIemAf.setWidget(0, QFormLayout.ItemRole.LabelRole, self.cb_iem_af_enabled)
        self.verticalLayoutIem.addWidget(self.groupIemAf)

        self._build_device_slots(
            parent_tab=self.tabIem,
            parent_layout=self.verticalLayoutIem,
            prefix="iem",
            count=4,
        )
        self.tabWidget.addTab(self.tabIem, u"")

        self.tabMics = QWidget()
        self.tabMics.setObjectName(u"tabMics")
        self.verticalLayoutMics = QVBoxLayout(self.tabMics)
        self.verticalLayoutMics.setObjectName(u"verticalLayoutMics")
        self._build_device_slots(
            parent_tab=self.tabMics,
            parent_layout=self.verticalLayoutMics,
            prefix="mic",
            count=4,
        )
        self.tabWidget.addTab(self.tabMics, u"")

        self.verticalLayout.addWidget(self.tabWidget)

        # ---------------------------------------------------------------
        # OK / Cancel
        # ---------------------------------------------------------------
        self.frameButtons = QFrame(PreferencesDialogForm)
        self.frameButtons.setObjectName(u"frameButtons")
        self.frameButtons.setSizePolicy(groupBoxSizePolicy)
        self.frameButtons.setFrameShape(QFrame.Shape.StyledPanel)
        self.frameButtons.setFrameShadow(QFrame.Shadow.Raised)
        self.hLayoutButtons = QHBoxLayout(self.frameButtons)
        self.hLayoutButtons.setObjectName(u"hLayoutButtons")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.hLayoutButtons.addItem(self.horizontalSpacer)
        self.btn_ok = QPushButton(self.frameButtons)
        self.btn_ok.setObjectName(u"btn_ok")
        self.hLayoutButtons.addWidget(self.btn_ok)
        self.btn_cancel = QPushButton(self.frameButtons)
        self.btn_cancel.setObjectName(u"btn_cancel")
        self.hLayoutButtons.addWidget(self.btn_cancel)
        self.verticalLayout.addWidget(self.frameButtons)

        self.retranslateUi(PreferencesDialogForm)
        self.btn_ok.setDefault(True)
        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(PreferencesDialogForm)
    # setupUi

    def _build_device_slots(self, parent_tab, parent_layout, prefix, count):
        """
        Builds `count` identical QGroupBox slots (objectNames {prefix}_group_N,
        {prefix}_enabled_N, {prefix}_name_N, {prefix}_ip_N, {prefix}_port_N)
        matching the .ui file's IEM / Wireless-Mics tabs. The Channel field
        (rx1/rx2 select) is mic-only -- an SR IEM G4 has no channel-select
        concept, one physical unit is one channel.
        """
        for i in range(1, count + 1):
            group = QGroupBox(parent_tab)
            group.setObjectName(f"{prefix}_group_{i}")
            form = QFormLayout(group)
            form.setObjectName(f"form{prefix.capitalize()}{i}")
            form.setContentsMargins(-1, 20, -1, -1)

            enabled = QCheckBox(group)
            enabled.setObjectName(f"{prefix}_enabled_{i}")
            enabled.setText("Enabled")
            form.setWidget(0, QFormLayout.ItemRole.LabelRole, enabled)

            label_name = QLabel(group)
            label_name.setObjectName(f"label_{prefix}_name_{i}")
            label_name.setText("Name")
            form.setWidget(1, QFormLayout.ItemRole.LabelRole, label_name)
            name = QLineEdit(group)
            name.setObjectName(f"{prefix}_name_{i}")
            form.setWidget(1, QFormLayout.ItemRole.FieldRole, name)

            label_ip = QLabel(group)
            label_ip.setObjectName(f"label_{prefix}_ip_{i}")
            label_ip.setText("IP address")
            form.setWidget(2, QFormLayout.ItemRole.LabelRole, label_ip)
            ip = QLineEdit(group)
            ip.setObjectName(f"{prefix}_ip_{i}")
            form.setWidget(2, QFormLayout.ItemRole.FieldRole, ip)

            label_port = QLabel(group)
            label_port.setObjectName(f"label_{prefix}_port_{i}")
            label_port.setText("Port")
            form.setWidget(3, QFormLayout.ItemRole.LabelRole, label_port)
            port = QSpinBox(group)
            port.setObjectName(f"{prefix}_port_{i}")
            port.setMinimum(1)
            port.setMaximum(65535)
            form.setWidget(3, QFormLayout.ItemRole.FieldRole, port)

            channel = None
            if prefix == "mic":
                label_channel = QLabel(group)
                label_channel.setObjectName(f"label_{prefix}_channel_{i}")
                label_channel.setText("Channel")
                form.setWidget(4, QFormLayout.ItemRole.LabelRole, label_channel)
                channel = QSpinBox(group)
                channel.setObjectName(f"{prefix}_channel_{i}")
                channel.setMinimum(1)
                channel.setMaximum(2)
                form.setWidget(4, QFormLayout.ItemRole.FieldRole, channel)

            parent_layout.addWidget(group)
            setattr(self, f"{prefix}_group_{i}", group)
            setattr(self, f"{prefix}_enabled_{i}", enabled)
            setattr(self, f"{prefix}_name_{i}", name)
            setattr(self, f"{prefix}_ip_{i}", ip)
            setattr(self, f"{prefix}_port_{i}", port)
            if channel is not None:
                setattr(self, f"{prefix}_channel_{i}", channel)

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        parent_layout.addItem(spacer)
        setattr(self, f"verticalSpacer{prefix.capitalize()}s", spacer)

    def retranslateUi(self, PreferencesDialogForm):
        PreferencesDialogForm.setWindowTitle(QCoreApplication.translate("PreferencesDialogForm", u"Preferences", None))
        self.groupTimecode.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"Timecode source", None))
        self.rb_midi.setText(QCoreApplication.translate("PreferencesDialogForm", u"MIDI", None))
        self.rb_osc.setText(QCoreApplication.translate("PreferencesDialogForm", u"OSC", None))
        self.groupMIDI.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"MIDI", None))
        self.label_midi_port.setText(QCoreApplication.translate("PreferencesDialogForm", u"MIDI port", None))
        self.groupOSC.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"OSC", None))
        self.label_osc_host.setText(QCoreApplication.translate("PreferencesDialogForm", u"Host", None))
        self.label_osc_port.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_osc_addr.setText(QCoreApplication.translate("PreferencesDialogForm", u"Address", None))
        self.label_fps.setText(QCoreApplication.translate("PreferencesDialogForm", u"FPS fallback", None))
        self.groupNetworkDevices.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"IEM / mic devices", None))
        self.cb_devices_enabled.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enable Sennheiser IEM / Wireless Mics", None))
        self.cb_simulate_devices.setText(QCoreApplication.translate("PreferencesDialogForm", u"Simulate (no hardware)", None))
        self.label_poll_interval.setText(QCoreApplication.translate("PreferencesDialogForm", u"Poll interval (ms)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGeneral),
                                   QCoreApplication.translate("PreferencesDialogForm", u"General", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabIem),
                                   QCoreApplication.translate("PreferencesDialogForm", u"IEM", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMics),
                                   QCoreApplication.translate("PreferencesDialogForm", u"Wireless Mics", None))

        self.groupIemAf.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"Audio level", None))
        self.cb_iem_af_enabled.setText(
            QCoreApplication.translate("PreferencesDialogForm", u"Show AF level (all IEM channels)", None))

        iem_titles = ["IEM G4 #1", "IEM G4 #2", "IEM G4 #3", "IEM G4 #4"]
        for i, title in enumerate(iem_titles, start=1):
            getattr(self, f"iem_group_{i}").setTitle(
                QCoreApplication.translate("PreferencesDialogForm", title, None))

        mic_titles = [
            "EW-DX EM2 #1 \u2013 Ch 1",
            "EW-DX EM2 #1 \u2013 Ch 2",
            "EW-DX EM2 #2 \u2013 Ch 1 (future)",
            "EW-DX EM2 #2 \u2013 Ch 2 (future)",
        ]
        for i, title in enumerate(mic_titles, start=1):
            getattr(self, f"mic_group_{i}").setTitle(
                QCoreApplication.translate("PreferencesDialogForm", title, None))

        self.btn_ok.setText(QCoreApplication.translate("PreferencesDialogForm", u"OK", None))
        self.btn_cancel.setText(QCoreApplication.translate("PreferencesDialogForm", u"Cancel", None))
    # retranslateUi
