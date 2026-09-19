# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
## Regenerate with:
##   pyside6-uic assets/mainwindow.ui -o assets/mainwindow.py
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox,
    QLabel, QLCDNumber, QMainWindow, QPushButton, QScrollArea, QSizePolicy,
    QWidget)

# QWebEngineView is a custom widget declared in the .ui <customwidgets> block.
from PySide6.QtWebEngineWidgets import QWebEngineView


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(320, 1480)
        MainWindow.setEnabled(True)
        MainWindow.setStyleSheet(u"background-color: black")

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # ---- Clock ---------------------------------------------------
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(0, 0, 320, 120))
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setStyleSheet(u"background-color: #444")
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)

        self.lcdClock = QLCDNumber(self.groupBox)
        self.lcdClock.setObjectName(u"lcdClock")
        self.lcdClock.setGeometry(QRect(0, 20, 320, 100))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lcdClock.sizePolicy().hasHeightForWidth())
        self.lcdClock.setSizePolicy(sizePolicy)
        font = QFont()
        font.setBold(False)
        self.lcdClock.setFont(font)
        self.lcdClock.setLineWidth(2)
        self.lcdClock.setSmallDecimalPoint(False)
        self.lcdClock.setDigitCount(8)
        self.lcdClock.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        # ---- Timecode --------------------------------------------------
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(0, 130, 320, 151))
        self.groupBox_2.setAutoFillBackground(False)
        self.groupBox_2.setStyleSheet(u"background-color: #444")
        self.groupBox_2.setFlat(False)
        self.groupBox_2.setCheckable(False)

        self.lcdTimecode = QLCDNumber(self.groupBox_2)
        self.lcdTimecode.setObjectName(u"lcdTimecode")
        self.lcdTimecode.setGeometry(QRect(0, 20, 321, 80))
        sizePolicy.setHeightForWidth(self.lcdTimecode.sizePolicy().hasHeightForWidth())
        self.lcdTimecode.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(False)
        self.lcdTimecode.setFont(font1)
        self.lcdTimecode.setLineWidth(2)
        self.lcdTimecode.setSmallDecimalPoint(True)
        self.lcdTimecode.setDigitCount(8)
        self.lcdTimecode.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self.layoutWidget = QWidget(self.groupBox_2)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 100, 321, 21))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.frate_24 = QLabel(self.layoutWidget)
        self.frate_24.setObjectName(u"frate_24")
        font2 = QFont()
        font2.setPointSize(14)
        self.frate_24.setFont(font2)
        self.frate_24.setStyleSheet(u"color: rgb(135, 135, 135)")
        self.frate_24.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.frate_24, 0, 0, 1, 1)

        self.frate_25 = QLabel(self.layoutWidget)
        self.frate_25.setObjectName(u"frate_25")
        font3 = QFont()
        font3.setPointSize(13)
        self.frate_25.setFont(font3)
        self.frate_25.setStyleSheet(u"color: rgb(135, 135, 135)")
        self.frate_25.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.frate_25, 0, 1, 1, 1)

        self.frate_29 = QLabel(self.layoutWidget)
        self.frate_29.setObjectName(u"frate_29")
        self.frate_29.setFont(font2)
        self.frate_29.setStyleSheet(u"color: rgb(135, 135, 135)")
        self.frate_29.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.frate_29, 0, 2, 1, 1)

        self.frate_30 = QLabel(self.layoutWidget)
        self.frate_30.setObjectName(u"frate_30")
        self.frate_30.setFont(font2)
        self.frate_30.setStyleSheet(u"color: rgb(135, 135, 135)")
        self.frate_30.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.frate_30, 0, 3, 1, 1)

        self.btnPreferences = QPushButton(self.groupBox_2)
        self.btnPreferences.setObjectName(u"btnPreferences")
        self.btnPreferences.setGeometry(QRect(10, 125, 100, 20))

        # ---- IEM / Wireless mic device row ------------------------------
        # Geometry here (502 / 482) matches a 2-row grid of 234px-tall strips
        # -- see device_widgets.group_devices_height_for_rows(). MainWindow
        # recalculates and overrides both this and webView's geometry at
        # runtime as channels are enabled/disabled (or the feature is
        # switched off entirely, which collapses groupDevices to a 66px
        # "nothing enabled" message), so these are just first-paint defaults.
        self.groupDevices = QGroupBox(self.centralwidget)
        self.groupDevices.setObjectName(u"groupDevices")
        self.groupDevices.setGeometry(QRect(0, 285, 320, 502))
        self.groupDevices.setAutoFillBackground(False)
        self.groupDevices.setStyleSheet(u"background-color: #444")
        self.groupDevices.setFlat(False)
        self.groupDevices.setCheckable(False)

        self.scrollDevices = QScrollArea(self.groupDevices)
        self.scrollDevices.setObjectName(u"scrollDevices")
        self.scrollDevices.setGeometry(QRect(0, 20, 320, 482))
        self.scrollDevices.setStyleSheet(u"background-color: #444; border: none;")
        self.scrollDevices.setWidgetResizable(True)
        self.scrollDevices.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollDevices.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.deviceRowContents = QWidget()
        self.deviceRowContents.setObjectName(u"deviceRowContents")
        self.deviceRowContents.setGeometry(QRect(0, 0, 320, 482))
        self.deviceRowContents.setStyleSheet(u"background-color: #444;")
        # 4 columns (slots 1-4), up to 2 rows (IEM row, then Mic row).
        # Populated at runtime by device_widgets.DeviceRow.
        self.deviceRowLayout = QGridLayout(self.deviceRowContents)
        self.deviceRowLayout.setObjectName(u"deviceRowLayout")
        self.deviceRowLayout.setContentsMargins(4, 2, 4, 2)
        self.deviceRowLayout.setHorizontalSpacing(4)
        self.deviceRowLayout.setVerticalSpacing(4)
        self.scrollDevices.setWidget(self.deviceRowContents)

        # ---- Companion / Stream Deck web view ---------------------------
        self.webView = QWebEngineView(self.centralwidget)
        self.webView.setObjectName(u"webView")
        self.webView.setGeometry(QRect(0, 792, 321, 683))

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Clock", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Timecode", None))
        self.frate_24.setText(QCoreApplication.translate("MainWindow", u"24", None))
        self.frate_25.setText(QCoreApplication.translate("MainWindow", u"25", None))
        self.frate_29.setText(QCoreApplication.translate("MainWindow", u"29.97", None))
        self.frate_30.setText(QCoreApplication.translate("MainWindow", u"30", None))
        self.btnPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.groupDevices.setTitle(QCoreApplication.translate("MainWindow", u"IEM / Wireless Mics", None))
    # retranslateUi
