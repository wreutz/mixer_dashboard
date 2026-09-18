# SQx Mixer Dashboard — IEM / Wireless Mic extension

Extends the existing clock + timecode + Companion web-view kiosk app with a
row of channel-strip widgets for:

- up to **4x Sennheiser IEM G4** channels (in-ear monitoring)
- up to **4x wireless-mic channels** served by **2x Sennheiser EW-DX EM2**
  2-channel receivers (2 channels enabled today, 2 more ready to switch on
  once a second EM2 is added)

Both device kinds are individually enabled/disabled from **Preferences**,
which now has three tabs: **General** (timecode/MIDI/OSC settings, plus a
master "Enable Sennheiser IEM / Wireless Mics" switch, a simulation toggle,
and the poll interval), **IEM**, and **Wireless Mics**.

## What changed

| File | What |
|---|---|
| `assets/mainwindow.ui` | Web view shrunk to make room for a new `groupDevices` box (a `QScrollArea` → `deviceRowContents` / `deviceRowLayout`, a `QGridLayout`) between the Timecode box and the web view. Both `groupDevices` and `webView` are resized at runtime -- see "Layout" below. |
| `assets/mainwindow.py` | Hand-authored compiled equivalent of the above (see regeneration note below). |
| `assets/preferences_dialog.ui` | Wrapped the existing timecode/MIDI/OSC groups in a `QTabWidget` **General** tab (plus the master enable switch, simulate toggle, poll interval), added an **IEM** tab (4 slots) and **Wireless Mics** tab (4 slots), each slot exposing Enabled / Name / IP / Port / Channel. OK/Cancel stay outside the tabs. |
| `assets/preferences_dialog.py` | Hand-authored compiled equivalent (uses small loops to build the 4+4 repeated slot groupboxes, but produces identical `objectName`s to what `pyside6-uic` would emit from the `.ui`). |
| `preferences.py` | Loads/saves all General + IEM + Wireless Mics fields to `settings.ini`, emits `settingsApplied` on OK. Greys out Simulate/poll-interval/the IEM & Mic tabs when the master switch is off. |
| `device_network.py` | Talks to real hardware over two confirmed Sennheiser protocols -- see "Protocols" below. `SimulatedDeviceClient` still covers any slot with no IP set, or with Simulate on. |
| `device_widgets.py` | `ChannelStripWidget` (+ `IemChannelWidget`, `WirelessMicChannelWidget`) -- segmented RF/LQI/AF bargraphs, a diversity indicator, and a battery gauge, styled after Sennheiser WSM / Shure Wireless Workbench channel strips -- and `DeviceRow`, which builds the whole grid from `settings.ini`, owns the network clients, and reports how many rows it's actually using (0/1/2) so the surrounding group can resize. |
| `main.py` | Wires `DeviceRow` into the device grid, extends `SettingsManager` defaults with `[network]` (now including the master `DEVICES_ENABLED` switch), `[iem]`, `[wireless_mics]` sections, and reloads/rebuilds + resizes on Preferences apply. |

### Regenerating the `.ui` → `.py` files for real

The two `assets/*.py` files in this deliverable were **hand-written** to
match what `pyside6-uic` would produce from the accompanying `.ui` files
(same class name, same `objectName`s, same widget tree), since this
environment can't run the Qt tool. Once you have a normal PySide6 dev
environment, regenerate them for 1:1 fidelity:

```bash
pyside6-uic assets/mainwindow.ui -o assets/mainwindow.py
pyside6-uic assets/preferences_dialog.ui -o assets/preferences_dialog.py
```

Nothing else needs to change — `main.py` and `preferences.py` only depend on
the class names and `objectName`s, both of which match exactly.

## Layout (320 × 1480 portrait) — dynamic, 3 states

```
y=0    Clock                          (120px, fixed)
y=130  Timecode + framerate + Prefs   (151px, fixed)
y=285  IEM / Wireless Mics group      (66px collapsed / 264px for 1 row / 502px for 2 rows)
...    Companion / Stream Deck view   (fills the rest, to 5px from the bottom)
```

`groupDevices` (and therefore `webView`) resizes automatically at three
possible heights, chosen by `device_widgets.group_devices_height(rows)`:

| `rows` | When | Group height | Web view starts at |
|---|---|---|---|
| 0 | Master switch off, **or** no individual IEM/Mic slot enabled | **66px** (just the "nothing enabled" message) | y=356, height=1119 |
| 1 | ≤4 channels enabled (fit in one row) | 264px | y=554, height=921 |
| 2 | 5-8 channels enabled | 502px | y=792, height=683 |

`MainWindow._apply_device_row_geometry()` runs at startup and again every
time Preferences is applied (via `DeviceRow.layout_changed`), so flipping
the master switch, or enabling/disabling individual channels, immediately
grows or shrinks the device box and hands the freed/reclaimed space to the
web view. Strips are `STRIP_WIDTH`=74 x `STRIP_HEIGHT`=234 (4 x 74 + gaps =
316px, fits the 320px screen). 234 isn't an arbitrary number: it's the
smallest height that keeps the mic strip's AF meter bar at/above its own
declared 44px minimum once its value label is showing -- verified by
simulating the actual QVBoxLayout/QHBoxLayout item stack (see the
STRIP_HEIGHT comment in `device_widgets.py`), not eyeballed.

## Device grid — 4 columns x up to 2 rows

Row 0 = IEM G4 slots, row 1 = EW-DX EM2 mic channels, filling left-to-right /
top-to-bottom as they're enabled. With IEM 1-4 and Mic 1-2 on (your setup):

```
IEM 1   IEM 2   IEM 3   IEM 4
Mic 1   Mic 2    --      --
```

With ≤4 channels enabled only row 0 is used (264px); with the master switch
off, or nothing enabled at all, the group collapses to 66px -- just tall
enough for a one-line message, no empty channel-strip row wasting space.

## Channel strip parameters (per device type)

The two device types show genuinely different things, because they *are*
different things — an IEM G4 is a **transmitter**, so it has no received-RF
reading and no battery gauge to report.

**IEM G4** — captioned `L` / `R` bars side by side, MUTE/frequency readout
at the bottom:

```
 ● IEM 1
   NAME
  L   R        <- captions
 ███ ███
 ███ ███       <- stereo AF level
 ███ ███
 520.125 MHz   <- MUTE takes priority over this when muted
```

**EW-DX EM2 (mic channel)** — diversity squares above the RF meter, then
captioned `RF` / `LQI` / `AF` bars side by side (AF now with its own dBFS
readout, like RF and LQI have), the battery, then MUTE/frequency at the
bottom (same convention as IEM):

```
 ● EM2 1
   NAME
  [A][B]          <- diversity, active antenna lights green
 RF  LQI  AF      <- captions
 ███ ███ ███
 ███ ███ ███
 RF  -58 dBm      <- RF readout (dBm)
 LQI 87%          <- link quality readout (0-100%)
                  <- extra 10px breathing room
 BATT
 [████████  ]
 76%
 548.100 MHz      <- MUTE takes priority over this when muted
```

Bars sit side by side (as WSM / Wireless Workbench do it) rather than
stacked: stacking three meters vertically left segments too thin to read.
Side by side gives ~8px segments on mic strips (the tighter of the two
layouts) and much taller ones on IEM strips, which have fewer elements to
fit.

**Status dot color** now has three states, not two: green = connected, red =
disconnected, **orange = this channel is simulated** (a simulated client
always reports itself "connected", so orange is what actually distinguishes
made-up demo data from a real live reading -- there's no separate "sim" text
label taking up a row anymore).

RF arrives in dBm but the bar needs a 0-100% fill, so `RF_DBM_FLOOR` (-95)
and `RF_DBM_CEILING` (-25) in `device_widgets.py` define that *display*
window — deliberately narrower than the protocol's full documented -107..0
dBm range (`RSSI_DBM_MIN`/`MAX` in `device_network.py`), since a receiver
sitting anywhere in the "good" part of that huge range would otherwise look
identically full. This affects the **bar only** — the readout always prints
the true dBm value. Likewise `AF_DBFS_FLOOR`/`AF_DBFS_CEILING` in
`device_network.py` map the mic's dBFS audio level onto its 0-100% bar.
Adjust any of these if your setup sits in a different part of the range in
practice.

## Real-hardware finding: AF level needed a subscription, not a poll

Tested against a real EW-DX EM2: connection, diversity, frequency, RF and
LQI, and battery all came back correctly from `_poll()`'s plain `null`-get
requests. AF level did not, even though it's requested in the exact same
batched message as the fields that did work.

AF is a fast, audio-rate metering value, and unlike the other confirmed
paths, it seems to need the SSC protocol's documented subscription
mechanism (`/osc/state/subscribe`, developer's guide section 5) rather than
a one-shot get to actually start being reported. `SSCEM2Device._subscribe_af()`
now sends that subscription request for `/m/rx1/af` and `/m/rx2/af` on
startup and renews it every 20s (comfortably inside its 30s requested
lifetime), purely additively -- nothing about the already-working polled
fields changed. The device's push notifications for the subscribed
addresses arrive as ordinary `{"m":{"rx1":{"af": <value>}}}` messages,
which the existing generic parser already handled correctly, so no
receive-side changes were needed either.

I don't have a citation that explicitly states *why* AF specifically
requires a subscription where the others don't (plausibly: computing/
reporting a continuous audio-rate value costs the device something, so it
only does it while someone's actually subscribed) -- this is the protocol's
documented mechanism for exactly this kind of data, reasoned from what your
hardware showed, not confirmed against a passage that spells out the
distinction. Worth confirming it actually fixes it on your unit.

While debugging this the AF meter also gained a numeric dBFS readout (like
RF and LQI already had) instead of just a bar, so if it's still not moving
after this fix, the readout should make it obvious whether that's "no data
arriving" (stuck at `--`) or "receiving 0 signal" (a real number, just low).

## Protocols — confirmed, not guessed

`device_network.py` implements two distinct, officially-documented
Sennheiser protocols; nothing here is reverse-engineered or placeholder:

- **SR IEM G4** — `G4Device` — Sennheiser's Media Control Protocol
  (TI 1254 v1.0): ASCII `Command param1 ... paramN\r` over UDP/**53212**.
  Subscribes to cyclic attribute pushes via `Push` (renewed automatically
  before the 60s timeout expires) rather than polling.
- **EW-DX EM2** — `SSCEM2Device` — legacy SSC: JSON objects over UDP/**45**,
  unauthenticated ("Legacy" 3rd Party Access mode on the device — if it's
  been claimed with SSCv2 this client can't reach it; switch it back, or
  extend `SSCEM2Device` to speak SSCv2/HTTPS instead).

The EM2 side is checked directly against Sennheiser's own **"Sound Control
Protocol, Developer's guide for EW-DX"** (EW-DX EM 2 firmware 1.1.3, Publ.
03/2023) — every mic-strip element maps to a documented, numbered section of
that guide:

| Mic strip element | SSC path | Guide section |
|---|---|---|
| Name / frequency / mute | `/rxN/name`, `/frequency`, `/mute` | 8.62-8.66, 8.87-8.91 |
| RF (dBm) | `/m/rxN/rssi` (-107.0..0.0 dBm) | 8.96, 8.100 |
| LQI (%) | `/m/rxN/rsqi` (0..100%) | 8.97, 8.101 |
| Diversity A/B | `/m/rxN/divi` (0=none, 1=A, 2=B) | 8.98, 8.102 |
| AF level | `/m/rxN/af` (-138.5..0.0 dBFS) | 8.99, 8.103* |
| Battery | `/mates/txN/battery/gauge` (0..100%) | 8.106, 8.122 |
| Warnings (RF) | `/rxN/warnings` (`LowSignal`, `NoLink`, `RfPeak`, `Aes256Error`) | 8.61, 8.86 |
| Warnings (battery/AF) | `/mates/txN/warnings` (`LowBattery`, `AfPeak`) | 8.107, 8.123 |

\* The guide's own section heading for 8.103 misprints its path as
`/m/rx1/af` (a duplicate of 8.99) — its body text ("Returns audio level for
receiver channel 2") and the surrounding numbering make clear it's actually
`/m/rx2/af`; the code uses it that way.

So: RF, LQI, diversity, AF level and battery are **all real, all live** off
confirmed paths — none of the mic strip is placebo data against actual
hardware anymore. `rxN/warnings` and `mates/txN/warnings` are also read and
folded into `DeviceReading.rf_warning` / `.battery_warning` / `.warnings`
(OR'd with the previous threshold-based checks as a belt-and-suspenders
fallback, in case a warning hasn't been polled yet).

Once your IPs are filled in under Preferences → IEM / Wireless Mics, flip
`SIMULATE_DEVICES = false` (Preferences → General, or `settings.ini` →
`[network]`) to switch from the fake data generator to these real clients.

## New `settings.ini` sections

```ini
[network]
DEVICES_ENABLED = true    ; master switch -- see Preferences -> General
SIMULATE_DEVICES = true
POLL_INTERVAL_MS = 1000

[iem]
IEM1_ENABLED = true
IEM1_NAME = IEM 1
IEM1_IP =
IEM1_PORT = 53212   ; G4 Media Control Protocol's fixed port
IEM1_CHANNEL = 1    ; not used by this protocol -- kept for UI symmetry with mics
; ... IEM2_*, IEM3_*, IEM4_* follow the same pattern

[wireless_mics]
MIC1_ENABLED = true
MIC1_NAME = Mic 1
MIC1_IP =
MIC1_PORT = 45      ; SSC's fixed port
MIC1_CHANNEL = 1    ; rx1 on the EM2 at MIC1_IP
; MIC2 defaults to CHANNEL=2 (rx2 -- same EM2 IP as MIC1 -> shares one socket)
; MIC3/MIC4 default to disabled, CHANNEL 1/2 (second EM2 unit's IP)
```

Setting `DEVICES_ENABLED = false` (or unchecking "Enable Sennheiser IEM /
Wireless Mics" in Preferences → General) skips starting any client at all,
regardless of individual slot settings, and collapses the group to its
66px minimum.

Point `MIC1_IP` and `MIC2_IP` at the *same* EM2 unit's address with
`CHANNEL` 1 and 2 respectively — `DeviceRegistry` recognizes the shared IP
and opens one UDP socket / one `SSCEM2Device` for both, reading `rx1` and
`rx2` off it, rather than two redundant sockets to the same unit.

## Dependencies

Same as before, plus `PySide6.QtNetwork` (ships with `PySide6`, no extra
package needed):

```
PySide6
PySide6-Addons   # QtWebEngineWidgets
mido
python-rtmidi
python-osc
```
