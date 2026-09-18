# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QFrame, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_PreferencesDialogForm(object):
    def setupUi(self, PreferencesDialogForm):
        if not PreferencesDialogForm.objectName():
            PreferencesDialogForm.setObjectName(u"PreferencesDialogForm")
        PreferencesDialogForm.resize(300, 640)
        palette = QPalette()
        brush = QBrush(QColor(42, 42, 42, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        PreferencesDialogForm.setPalette(palette)
        PreferencesDialogForm.setAutoFillBackground(True)
        self.verticalLayout = QVBoxLayout(PreferencesDialogForm)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.tabWidget = QTabWidget(PreferencesDialogForm)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabGeneral = QWidget()
        self.tabGeneral.setObjectName(u"tabGeneral")
        self.verticalLayoutGeneral = QVBoxLayout(self.tabGeneral)
        self.verticalLayoutGeneral.setObjectName(u"verticalLayoutGeneral")
        self.groupTimecode = QGroupBox(self.tabGeneral)
        self.groupTimecode.setObjectName(u"groupTimecode")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupTimecode.sizePolicy().hasHeightForWidth())
        self.groupTimecode.setSizePolicy(sizePolicy1)
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
        sizePolicy1.setHeightForWidth(self.groupMIDI.sizePolicy().hasHeightForWidth())
        self.groupMIDI.setSizePolicy(sizePolicy1)
        self.formMIDI = QVBoxLayout(self.groupMIDI)
        self.formMIDI.setObjectName(u"formMIDI")
        self.formMIDI.setContentsMargins(8, 24, 8, 8)
        self.label_midi_port = QLabel(self.groupMIDI)
        self.label_midi_port.setObjectName(u"label_midi_port")
        self.label_midi_port.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.formMIDI.addWidget(self.label_midi_port)

        self.cb_midi_ports = QComboBox(self.groupMIDI)
        self.cb_midi_ports.setObjectName(u"cb_midi_ports")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cb_midi_ports.sizePolicy().hasHeightForWidth())
        self.cb_midi_ports.setSizePolicy(sizePolicy2)
        self.cb_midi_ports.setEditable(True)

        self.formMIDI.addWidget(self.cb_midi_ports)


        self.verticalLayoutGeneral.addWidget(self.groupMIDI)

        self.groupOSC = QGroupBox(self.tabGeneral)
        self.groupOSC.setObjectName(u"groupOSC")
        sizePolicy1.setHeightForWidth(self.groupOSC.sizePolicy().hasHeightForWidth())
        self.groupOSC.setSizePolicy(sizePolicy1)
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
        sizePolicy1.setHeightForWidth(self.groupNetworkDevices.sizePolicy().hasHeightForWidth())
        self.groupNetworkDevices.setSizePolicy(sizePolicy1)
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

        self.tabWidget.addTab(self.tabGeneral, "")
        self.tabIem = QWidget()
        self.tabIem.setObjectName(u"tabIem")
        self.verticalLayoutIem = QVBoxLayout(self.tabIem)
        self.verticalLayoutIem.setObjectName(u"verticalLayoutIem")
        self.iem_group_1 = QGroupBox(self.tabIem)
        self.iem_group_1.setObjectName(u"iem_group_1")
        self.formIem1 = QFormLayout(self.iem_group_1)
        self.formIem1.setObjectName(u"formIem1")
        self.formIem1.setContentsMargins(-1, 20, -1, -1)
        self.iem_enabled_1 = QCheckBox(self.iem_group_1)
        self.iem_enabled_1.setObjectName(u"iem_enabled_1")

        self.formIem1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.iem_enabled_1)

        self.label_iem_name_1 = QLabel(self.iem_group_1)
        self.label_iem_name_1.setObjectName(u"label_iem_name_1")

        self.formIem1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_iem_name_1)

        self.iem_name_1 = QLineEdit(self.iem_group_1)
        self.iem_name_1.setObjectName(u"iem_name_1")

        self.formIem1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.iem_name_1)

        self.label_iem_ip_1 = QLabel(self.iem_group_1)
        self.label_iem_ip_1.setObjectName(u"label_iem_ip_1")

        self.formIem1.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_iem_ip_1)

        self.iem_ip_1 = QLineEdit(self.iem_group_1)
        self.iem_ip_1.setObjectName(u"iem_ip_1")

        self.formIem1.setWidget(2, QFormLayout.ItemRole.FieldRole, self.iem_ip_1)

        self.label_iem_port_1 = QLabel(self.iem_group_1)
        self.label_iem_port_1.setObjectName(u"label_iem_port_1")

        self.formIem1.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_iem_port_1)

        self.iem_port_1 = QSpinBox(self.iem_group_1)
        self.iem_port_1.setObjectName(u"iem_port_1")
        self.iem_port_1.setMinimum(1)
        self.iem_port_1.setMaximum(65535)

        self.formIem1.setWidget(3, QFormLayout.ItemRole.FieldRole, self.iem_port_1)

        self.label_iem_channel_1 = QLabel(self.iem_group_1)
        self.label_iem_channel_1.setObjectName(u"label_iem_channel_1")

        self.formIem1.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_iem_channel_1)

        self.iem_channel_1 = QSpinBox(self.iem_group_1)
        self.iem_channel_1.setObjectName(u"iem_channel_1")
        self.iem_channel_1.setMinimum(1)
        self.iem_channel_1.setMaximum(2)

        self.formIem1.setWidget(4, QFormLayout.ItemRole.FieldRole, self.iem_channel_1)


        self.verticalLayoutIem.addWidget(self.iem_group_1)

        self.iem_group_2 = QGroupBox(self.tabIem)
        self.iem_group_2.setObjectName(u"iem_group_2")
        self.formIem2 = QFormLayout(self.iem_group_2)
        self.formIem2.setObjectName(u"formIem2")
        self.formIem2.setContentsMargins(-1, 20, -1, -1)
        self.iem_enabled_2 = QCheckBox(self.iem_group_2)
        self.iem_enabled_2.setObjectName(u"iem_enabled_2")

        self.formIem2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.iem_enabled_2)

        self.label_iem_name_2 = QLabel(self.iem_group_2)
        self.label_iem_name_2.setObjectName(u"label_iem_name_2")

        self.formIem2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_iem_name_2)

        self.iem_name_2 = QLineEdit(self.iem_group_2)
        self.iem_name_2.setObjectName(u"iem_name_2")

        self.formIem2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.iem_name_2)

        self.label_iem_ip_2 = QLabel(self.iem_group_2)
        self.label_iem_ip_2.setObjectName(u"label_iem_ip_2")

        self.formIem2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_iem_ip_2)

        self.iem_ip_2 = QLineEdit(self.iem_group_2)
        self.iem_ip_2.setObjectName(u"iem_ip_2")

        self.formIem2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.iem_ip_2)

        self.label_iem_port_2 = QLabel(self.iem_group_2)
        self.label_iem_port_2.setObjectName(u"label_iem_port_2")

        self.formIem2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_iem_port_2)

        self.iem_port_2 = QSpinBox(self.iem_group_2)
        self.iem_port_2.setObjectName(u"iem_port_2")
        self.iem_port_2.setMinimum(1)
        self.iem_port_2.setMaximum(65535)

        self.formIem2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.iem_port_2)

        self.label_iem_channel_2 = QLabel(self.iem_group_2)
        self.label_iem_channel_2.setObjectName(u"label_iem_channel_2")

        self.formIem2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_iem_channel_2)

        self.iem_channel_2 = QSpinBox(self.iem_group_2)
        self.iem_channel_2.setObjectName(u"iem_channel_2")
        self.iem_channel_2.setMinimum(1)
        self.iem_channel_2.setMaximum(2)

        self.formIem2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.iem_channel_2)


        self.verticalLayoutIem.addWidget(self.iem_group_2)

        self.iem_group_3 = QGroupBox(self.tabIem)
        self.iem_group_3.setObjectName(u"iem_group_3")
        self.formIem3 = QFormLayout(self.iem_group_3)
        self.formIem3.setObjectName(u"formIem3")
        self.formIem3.setContentsMargins(-1, 20, -1, -1)
        self.iem_enabled_3 = QCheckBox(self.iem_group_3)
        self.iem_enabled_3.setObjectName(u"iem_enabled_3")

        self.formIem3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.iem_enabled_3)

        self.label_iem_name_3 = QLabel(self.iem_group_3)
        self.label_iem_name_3.setObjectName(u"label_iem_name_3")

        self.formIem3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_iem_name_3)

        self.iem_name_3 = QLineEdit(self.iem_group_3)
        self.iem_name_3.setObjectName(u"iem_name_3")

        self.formIem3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.iem_name_3)

        self.label_iem_ip_3 = QLabel(self.iem_group_3)
        self.label_iem_ip_3.setObjectName(u"label_iem_ip_3")

        self.formIem3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_iem_ip_3)

        self.iem_ip_3 = QLineEdit(self.iem_group_3)
        self.iem_ip_3.setObjectName(u"iem_ip_3")

        self.formIem3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.iem_ip_3)

        self.label_iem_port_3 = QLabel(self.iem_group_3)
        self.label_iem_port_3.setObjectName(u"label_iem_port_3")

        self.formIem3.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_iem_port_3)

        self.iem_port_3 = QSpinBox(self.iem_group_3)
        self.iem_port_3.setObjectName(u"iem_port_3")
        self.iem_port_3.setMinimum(1)
        self.iem_port_3.setMaximum(65535)

        self.formIem3.setWidget(3, QFormLayout.ItemRole.FieldRole, self.iem_port_3)

        self.label_iem_channel_3 = QLabel(self.iem_group_3)
        self.label_iem_channel_3.setObjectName(u"label_iem_channel_3")

        self.formIem3.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_iem_channel_3)

        self.iem_channel_3 = QSpinBox(self.iem_group_3)
        self.iem_channel_3.setObjectName(u"iem_channel_3")
        self.iem_channel_3.setMinimum(1)
        self.iem_channel_3.setMaximum(2)

        self.formIem3.setWidget(4, QFormLayout.ItemRole.FieldRole, self.iem_channel_3)


        self.verticalLayoutIem.addWidget(self.iem_group_3)

        self.iem_group_4 = QGroupBox(self.tabIem)
        self.iem_group_4.setObjectName(u"iem_group_4")
        self.formIem4 = QFormLayout(self.iem_group_4)
        self.formIem4.setObjectName(u"formIem4")
        self.formIem4.setContentsMargins(-1, 20, -1, -1)
        self.iem_enabled_4 = QCheckBox(self.iem_group_4)
        self.iem_enabled_4.setObjectName(u"iem_enabled_4")

        self.formIem4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.iem_enabled_4)

        self.label_iem_name_4 = QLabel(self.iem_group_4)
        self.label_iem_name_4.setObjectName(u"label_iem_name_4")

        self.formIem4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_iem_name_4)

        self.iem_name_4 = QLineEdit(self.iem_group_4)
        self.iem_name_4.setObjectName(u"iem_name_4")

        self.formIem4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.iem_name_4)

        self.label_iem_ip_4 = QLabel(self.iem_group_4)
        self.label_iem_ip_4.setObjectName(u"label_iem_ip_4")

        self.formIem4.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_iem_ip_4)

        self.iem_ip_4 = QLineEdit(self.iem_group_4)
        self.iem_ip_4.setObjectName(u"iem_ip_4")

        self.formIem4.setWidget(2, QFormLayout.ItemRole.FieldRole, self.iem_ip_4)

        self.label_iem_port_4 = QLabel(self.iem_group_4)
        self.label_iem_port_4.setObjectName(u"label_iem_port_4")

        self.formIem4.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_iem_port_4)

        self.iem_port_4 = QSpinBox(self.iem_group_4)
        self.iem_port_4.setObjectName(u"iem_port_4")
        self.iem_port_4.setMinimum(1)
        self.iem_port_4.setMaximum(65535)

        self.formIem4.setWidget(3, QFormLayout.ItemRole.FieldRole, self.iem_port_4)

        self.label_iem_channel_4 = QLabel(self.iem_group_4)
        self.label_iem_channel_4.setObjectName(u"label_iem_channel_4")

        self.formIem4.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_iem_channel_4)

        self.iem_channel_4 = QSpinBox(self.iem_group_4)
        self.iem_channel_4.setObjectName(u"iem_channel_4")
        self.iem_channel_4.setMinimum(1)
        self.iem_channel_4.setMaximum(2)

        self.formIem4.setWidget(4, QFormLayout.ItemRole.FieldRole, self.iem_channel_4)


        self.verticalLayoutIem.addWidget(self.iem_group_4)

        self.verticalSpacerIem = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutIem.addItem(self.verticalSpacerIem)

        self.tabWidget.addTab(self.tabIem, "")
        self.tabMics = QWidget()
        self.tabMics.setObjectName(u"tabMics")
        self.verticalLayoutMics = QVBoxLayout(self.tabMics)
        self.verticalLayoutMics.setObjectName(u"verticalLayoutMics")
        self.mic_group_1 = QGroupBox(self.tabMics)
        self.mic_group_1.setObjectName(u"mic_group_1")
        self.formMic1 = QFormLayout(self.mic_group_1)
        self.formMic1.setObjectName(u"formMic1")
        self.formMic1.setContentsMargins(-1, 20, -1, -1)
        self.mic_enabled_1 = QCheckBox(self.mic_group_1)
        self.mic_enabled_1.setObjectName(u"mic_enabled_1")

        self.formMic1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.mic_enabled_1)

        self.label_mic_name_1 = QLabel(self.mic_group_1)
        self.label_mic_name_1.setObjectName(u"label_mic_name_1")

        self.formMic1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_mic_name_1)

        self.mic_name_1 = QLineEdit(self.mic_group_1)
        self.mic_name_1.setObjectName(u"mic_name_1")

        self.formMic1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.mic_name_1)

        self.label_mic_ip_1 = QLabel(self.mic_group_1)
        self.label_mic_ip_1.setObjectName(u"label_mic_ip_1")

        self.formMic1.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_mic_ip_1)

        self.mic_ip_1 = QLineEdit(self.mic_group_1)
        self.mic_ip_1.setObjectName(u"mic_ip_1")

        self.formMic1.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mic_ip_1)

        self.label_mic_port_1 = QLabel(self.mic_group_1)
        self.label_mic_port_1.setObjectName(u"label_mic_port_1")

        self.formMic1.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_mic_port_1)

        self.mic_port_1 = QSpinBox(self.mic_group_1)
        self.mic_port_1.setObjectName(u"mic_port_1")
        self.mic_port_1.setMinimum(1)
        self.mic_port_1.setMaximum(65535)

        self.formMic1.setWidget(3, QFormLayout.ItemRole.FieldRole, self.mic_port_1)

        self.label_mic_channel_1 = QLabel(self.mic_group_1)
        self.label_mic_channel_1.setObjectName(u"label_mic_channel_1")

        self.formMic1.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_mic_channel_1)

        self.mic_channel_1 = QSpinBox(self.mic_group_1)
        self.mic_channel_1.setObjectName(u"mic_channel_1")
        self.mic_channel_1.setMinimum(1)
        self.mic_channel_1.setMaximum(2)

        self.formMic1.setWidget(4, QFormLayout.ItemRole.FieldRole, self.mic_channel_1)


        self.verticalLayoutMics.addWidget(self.mic_group_1)

        self.mic_group_2 = QGroupBox(self.tabMics)
        self.mic_group_2.setObjectName(u"mic_group_2")
        self.formMic2 = QFormLayout(self.mic_group_2)
        self.formMic2.setObjectName(u"formMic2")
        self.formMic2.setContentsMargins(-1, 20, -1, -1)
        self.mic_enabled_2 = QCheckBox(self.mic_group_2)
        self.mic_enabled_2.setObjectName(u"mic_enabled_2")

        self.formMic2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.mic_enabled_2)

        self.label_mic_name_2 = QLabel(self.mic_group_2)
        self.label_mic_name_2.setObjectName(u"label_mic_name_2")

        self.formMic2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_mic_name_2)

        self.mic_name_2 = QLineEdit(self.mic_group_2)
        self.mic_name_2.setObjectName(u"mic_name_2")

        self.formMic2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.mic_name_2)

        self.label_mic_ip_2 = QLabel(self.mic_group_2)
        self.label_mic_ip_2.setObjectName(u"label_mic_ip_2")

        self.formMic2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_mic_ip_2)

        self.mic_ip_2 = QLineEdit(self.mic_group_2)
        self.mic_ip_2.setObjectName(u"mic_ip_2")

        self.formMic2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mic_ip_2)

        self.label_mic_port_2 = QLabel(self.mic_group_2)
        self.label_mic_port_2.setObjectName(u"label_mic_port_2")

        self.formMic2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_mic_port_2)

        self.mic_port_2 = QSpinBox(self.mic_group_2)
        self.mic_port_2.setObjectName(u"mic_port_2")
        self.mic_port_2.setMinimum(1)
        self.mic_port_2.setMaximum(65535)

        self.formMic2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.mic_port_2)

        self.label_mic_channel_2 = QLabel(self.mic_group_2)
        self.label_mic_channel_2.setObjectName(u"label_mic_channel_2")

        self.formMic2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_mic_channel_2)

        self.mic_channel_2 = QSpinBox(self.mic_group_2)
        self.mic_channel_2.setObjectName(u"mic_channel_2")
        self.mic_channel_2.setMinimum(1)
        self.mic_channel_2.setMaximum(2)

        self.formMic2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.mic_channel_2)


        self.verticalLayoutMics.addWidget(self.mic_group_2)

        self.mic_group_3 = QGroupBox(self.tabMics)
        self.mic_group_3.setObjectName(u"mic_group_3")
        self.formMic3 = QFormLayout(self.mic_group_3)
        self.formMic3.setObjectName(u"formMic3")
        self.formMic3.setContentsMargins(-1, 20, -1, -1)
        self.mic_enabled_3 = QCheckBox(self.mic_group_3)
        self.mic_enabled_3.setObjectName(u"mic_enabled_3")

        self.formMic3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.mic_enabled_3)

        self.label_mic_name_3 = QLabel(self.mic_group_3)
        self.label_mic_name_3.setObjectName(u"label_mic_name_3")

        self.formMic3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_mic_name_3)

        self.mic_name_3 = QLineEdit(self.mic_group_3)
        self.mic_name_3.setObjectName(u"mic_name_3")

        self.formMic3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.mic_name_3)

        self.label_mic_ip_3 = QLabel(self.mic_group_3)
        self.label_mic_ip_3.setObjectName(u"label_mic_ip_3")

        self.formMic3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_mic_ip_3)

        self.mic_ip_3 = QLineEdit(self.mic_group_3)
        self.mic_ip_3.setObjectName(u"mic_ip_3")

        self.formMic3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mic_ip_3)

        self.label_mic_port_3 = QLabel(self.mic_group_3)
        self.label_mic_port_3.setObjectName(u"label_mic_port_3")

        self.formMic3.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_mic_port_3)

        self.mic_port_3 = QSpinBox(self.mic_group_3)
        self.mic_port_3.setObjectName(u"mic_port_3")
        self.mic_port_3.setMinimum(1)
        self.mic_port_3.setMaximum(65535)

        self.formMic3.setWidget(3, QFormLayout.ItemRole.FieldRole, self.mic_port_3)

        self.label_mic_channel_3 = QLabel(self.mic_group_3)
        self.label_mic_channel_3.setObjectName(u"label_mic_channel_3")

        self.formMic3.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_mic_channel_3)

        self.mic_channel_3 = QSpinBox(self.mic_group_3)
        self.mic_channel_3.setObjectName(u"mic_channel_3")
        self.mic_channel_3.setMinimum(1)
        self.mic_channel_3.setMaximum(2)

        self.formMic3.setWidget(4, QFormLayout.ItemRole.FieldRole, self.mic_channel_3)


        self.verticalLayoutMics.addWidget(self.mic_group_3)

        self.mic_group_4 = QGroupBox(self.tabMics)
        self.mic_group_4.setObjectName(u"mic_group_4")
        self.formMic4 = QFormLayout(self.mic_group_4)
        self.formMic4.setObjectName(u"formMic4")
        self.formMic4.setContentsMargins(-1, 20, -1, -1)
        self.mic_enabled_4 = QCheckBox(self.mic_group_4)
        self.mic_enabled_4.setObjectName(u"mic_enabled_4")

        self.formMic4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.mic_enabled_4)

        self.label_mic_name_4 = QLabel(self.mic_group_4)
        self.label_mic_name_4.setObjectName(u"label_mic_name_4")

        self.formMic4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_mic_name_4)

        self.mic_name_4 = QLineEdit(self.mic_group_4)
        self.mic_name_4.setObjectName(u"mic_name_4")

        self.formMic4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.mic_name_4)

        self.label_mic_ip_4 = QLabel(self.mic_group_4)
        self.label_mic_ip_4.setObjectName(u"label_mic_ip_4")

        self.formMic4.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_mic_ip_4)

        self.mic_ip_4 = QLineEdit(self.mic_group_4)
        self.mic_ip_4.setObjectName(u"mic_ip_4")

        self.formMic4.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mic_ip_4)

        self.label_mic_port_4 = QLabel(self.mic_group_4)
        self.label_mic_port_4.setObjectName(u"label_mic_port_4")

        self.formMic4.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_mic_port_4)

        self.mic_port_4 = QSpinBox(self.mic_group_4)
        self.mic_port_4.setObjectName(u"mic_port_4")
        self.mic_port_4.setMinimum(1)
        self.mic_port_4.setMaximum(65535)

        self.formMic4.setWidget(3, QFormLayout.ItemRole.FieldRole, self.mic_port_4)

        self.label_mic_channel_4 = QLabel(self.mic_group_4)
        self.label_mic_channel_4.setObjectName(u"label_mic_channel_4")

        self.formMic4.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_mic_channel_4)

        self.mic_channel_4 = QSpinBox(self.mic_group_4)
        self.mic_channel_4.setObjectName(u"mic_channel_4")
        self.mic_channel_4.setMinimum(1)
        self.mic_channel_4.setMaximum(2)

        self.formMic4.setWidget(4, QFormLayout.ItemRole.FieldRole, self.mic_channel_4)


        self.verticalLayoutMics.addWidget(self.mic_group_4)

        self.verticalSpacerMics = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutMics.addItem(self.verticalSpacerMics)

        self.tabWidget.addTab(self.tabMics, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.frameButtons = QFrame(PreferencesDialogForm)
        self.frameButtons.setObjectName(u"frameButtons")
        sizePolicy1.setHeightForWidth(self.frameButtons.sizePolicy().hasHeightForWidth())
        self.frameButtons.setSizePolicy(sizePolicy1)
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


        QMetaObject.connectSlotsByName(PreferencesDialogForm)
    # setupUi

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
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGeneral), QCoreApplication.translate("PreferencesDialogForm", u"General", None))
        self.iem_group_1.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"IEM G4 #1", None))
        self.iem_enabled_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enabled", None))
        self.label_iem_name_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"Name", None))
        self.label_iem_ip_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"IP address", None))
        self.label_iem_port_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_iem_channel_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"Channel", None))
        self.iem_group_2.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"IEM G4 #2", None))
        self.iem_enabled_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enabled", None))
        self.label_iem_name_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"Name", None))
        self.label_iem_ip_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"IP address", None))
        self.label_iem_port_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_iem_channel_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"Channel", None))
        self.iem_group_3.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"IEM G4 #3", None))
        self.iem_enabled_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enabled", None))
        self.label_iem_name_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"Name", None))
        self.label_iem_ip_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"IP address", None))
        self.label_iem_port_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_iem_channel_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"Channel", None))
        self.iem_group_4.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"IEM G4 #4", None))
        self.iem_enabled_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enabled", None))
        self.label_iem_name_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"Name", None))
        self.label_iem_ip_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"IP address", None))
        self.label_iem_port_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_iem_channel_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"Channel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabIem), QCoreApplication.translate("PreferencesDialogForm", u"IEM", None))
        self.mic_group_1.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"EW-DX EM2 #1 \u2013 Ch 1", None))
        self.mic_enabled_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enabled", None))
        self.label_mic_name_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"Name", None))
        self.label_mic_ip_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"IP address", None))
        self.label_mic_port_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_mic_channel_1.setText(QCoreApplication.translate("PreferencesDialogForm", u"Channel", None))
        self.mic_group_2.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"EW-DX EM2 #1 \u2013 Ch 2", None))
        self.mic_enabled_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enabled", None))
        self.label_mic_name_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"Name", None))
        self.label_mic_ip_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"IP address", None))
        self.label_mic_port_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_mic_channel_2.setText(QCoreApplication.translate("PreferencesDialogForm", u"Channel", None))
        self.mic_group_3.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"EW-DX EM2 #2 \u2013 Ch 1 (future)", None))
        self.mic_enabled_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enabled", None))
        self.label_mic_name_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"Name", None))
        self.label_mic_ip_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"IP address", None))
        self.label_mic_port_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_mic_channel_3.setText(QCoreApplication.translate("PreferencesDialogForm", u"Channel", None))
        self.mic_group_4.setTitle(QCoreApplication.translate("PreferencesDialogForm", u"EW-DX EM2 #2 \u2013 Ch 2 (future)", None))
        self.mic_enabled_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"Enabled", None))
        self.label_mic_name_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"Name", None))
        self.label_mic_ip_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"IP address", None))
        self.label_mic_port_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"Port", None))
        self.label_mic_channel_4.setText(QCoreApplication.translate("PreferencesDialogForm", u"Channel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMics), QCoreApplication.translate("PreferencesDialogForm", u"Wireless Mics", None))
        self.btn_ok.setText(QCoreApplication.translate("PreferencesDialogForm", u"OK", None))
        self.btn_cancel.setText(QCoreApplication.translate("PreferencesDialogForm", u"Cancel", None))
    # retranslateUi

