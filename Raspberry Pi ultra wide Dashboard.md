# Raspberry Pi ultra wide Dashboard

based on RPi 4, PoE+ hat, Waveshare 11.9" touch display

create SD card with Raspian 13 (Trixie) Lite and settings for SSH, WiFi, username, password, hostname, ...

## Install

```shell
sudo apt update; sudo apt dist-upgrade
sudo apt install git vim rpd-plym-splash
sudo apt install python3-pyside6.qtcore python3-pyside6.qtgui python3-pyside6.qtnetwork python3-pyside6.qtqml python3-pyside6.qtquick python3-pyside6.qttest python3-pyside6.qtwidgets
```

add lines to `/boot/firmware/config.txt`:

```ini
# Waveshare 11.9" touch screen dsi
# DSI1 use (default)
dtoverlay=vc4-kms-dsi-waveshare-panel,11_9_inch,rotation=90
# DSI0 Use
# dtoverlay=vc4-kms-dsi-waveshare-panel,11_9_inch
dtoverlay=WS_xinchDSI_Touch

[pi4]
# poe+ hat fan control
dtparam=poe_fan_temp0=50000
dtparam=poe_fan_temp1=60000
dtparam=poe_fan_temp2=70000
dtparam=poe_fan_temp3=80000
```

add to `/etc/bash.bashrc`:

```ini
alias temp='/usr/bin/vcgencmd measure_temp'
```

PySide6 dependencies for X-less GUI applications:

```shell
sudo apt install libegl1 libgl1
```

build virtualenv

```shell
python3 -m venv --system-site-packages venv
```

https://github.com/lbt/python-gui/tree/main


