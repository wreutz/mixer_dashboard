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
| `assets/preferences_dialog.ui` | Wrapped the existing timecode/MIDI/OSC groups in a `QTabWidget` **General** tab (plus the master enable switch, simulate toggle, poll interval), added an **IEM** tab (a section-level "Show AF level" switch, plus 4 slots exposing Enabled / Name / IP / Port -- no Channel field, an SR IEM G4 has no channel-select concept) and **Wireless Mics** tab (4 slots, Channel included -- an EW-DX EM2 genuinely has two, rx1/rx2). OK/Cancel stay outside the tabs. |
| `assets/preferences_dialog.py` | Hand-authored compiled equivalent (uses small loops to build the 4+4 repeated slot groupboxes, but produces identical `objectName`s to what `pyside6-uic` would emit from the `.ui`). |
| `preferences.py` | Loads/saves all General + IEM + Wireless Mics fields to `settings.ini`, emits `settingsApplied` on OK. Greys out Simulate/poll-interval/the IEM & Mic tabs when the master switch is off. |
| `device_network.py` | Talks to real hardware over two confirmed Sennheiser protocols -- see "Protocols" below. `SimulatedDeviceClient` still covers any slot with no IP set, or with Simulate on. `DeviceReading.name` is now purely the device's own reported name (no more silent fallback to the configured name). |
| `device_widgets.py` | `ChannelStripWidget` (+ `IemChannelWidget`, `WirelessMicChannelWidget`) -- segmented RF/LQI/AF bargraphs (AF now dense/near-continuous, WSM-style), a diversity indicator, and a battery gauge -- and `DeviceRow`, which builds the whole grid from `settings.ini`, owns the network clients, and tracks the *actual* per-row heights (rows aren't uniform anymore now that IEM's AF section can be switched off) so the surrounding group can resize correctly. |
| `main.py` | Wires `DeviceRow` into the device grid, extends `SettingsManager` defaults with `[network]` (now including the master `DEVICES_ENABLED` switch), `[iem]` (now including the section-level `IEM_AF_ENABLED` switch, no more per-slot channel), `[wireless_mics]` sections, and reloads/rebuilds + resizes on Preferences apply. |

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

## Layout (320 × 1480 portrait) — dynamic

```
y=0    Clock                          (120px, fixed)
y=130  Timecode + framerate + Prefs   (151px, fixed)
y=285  IEM / Wireless Mics group      (66px collapsed, up to ~502px for 2 full rows)
...    Companion / Stream Deck view   (fills the rest, to 5px from the bottom)
```

`groupDevices` (and therefore `webView`) resizes automatically, computed by
`device_widgets.group_devices_height_for_rows(row_heights)` from the
*actual* height of each occupied grid row, not just a row count. This
matters because rows aren't uniform anymore: an IEM row is
`IEM_STRIP_HEIGHT_COMPACT` (63px) tall when Preferences → IEM → "Show AF
level" is off, vs. `STRIP_HEIGHT` (234px) with it on, while a Mic row is
always 234px. `DeviceRow` tracks the tallest widget actually placed in each
row and emits the resulting total height directly via `layout_changed`, so
mixing a compact IEM row with a full Mic row sizes correctly rather than
assuming every row is the same:

| State | Group height | Web view starts at |
|---|---|---|
| Collapsed (master switch off, or nothing enabled) | 66px | y=356, height=1119 |
| 1 row, AF on (≤4 channels, e.g. all Mic) | 264px | y=554, height=921 |
| 1 row, AF off (≤4 IEM channels only) | 93px | y=383, height=1092 |
| 2 rows, both AF on | 502px | y=792, height=683 |
| 2 rows, IEM row AF off + Mic row | 331px | y=621, height=854 |

(The mixed cases assume a clean IEM-row / Mic-row split, which is what you
get whenever the IEM count is a multiple of 4 — the common case. Fill order
can produce genuinely mixed rows in other configurations; the height
calculation handles that correctly too, it just isn't one of the table
rows above.)

`MainWindow._apply_device_row_geometry()` runs at startup and again every
time Preferences is applied (via `DeviceRow.layout_changed`), so flipping
any of these switches immediately grows or shrinks the device box and hands
the freed/reclaimed space to the web view. Strips are `STRIP_WIDTH`=74 x
`STRIP_HEIGHT`=234 (4 x 74 + gaps = 316px, fits the 320px screen). 234 isn't
an arbitrary number: it's the smallest height that keeps the mic strip's AF
meter bar at/above its own declared 44px minimum once its value label is
showing — verified by simulating the actual QVBoxLayout/QHBoxLayout item
stack (see the STRIP_HEIGHT comment in `device_widgets.py`), not eyeballed;
`IEM_STRIP_HEIGHT_COMPACT` (63px) was derived the same way.

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
reading and no battery gauge to report. Neither has a "channel" setting: one
physical SR IEM G4 unit is one channel (no channel-select command exists in
its protocol), and Preferences → IEM reflects that — there's no Channel
field there, unlike the mic side (an EW-DX EM2 genuinely has two, rx1/rx2).

**Two labels, two different sources.** The topmost (small, dim) label is
your *configured* name from Preferences; the label below it (bold) is the
name the *device itself* reports over the network — these used to be
conflated (the top label showed a hardcoded slot id like "IEM 1", and the
name line silently fell back to your configured name whenever the device
hadn't reported its own yet, which on real hardware could show as e.g. top
`EM2 1` / bottom `EW-DX 1` — your configured label and the device's actual
name, not two views of the same thing). They're independent now: change the
Name field in Preferences and only the top line changes; the bottom line is
always whatever the device says its name is (`--` if nothing's arrived yet,
or on a simulated channel, your configured name as a stand-in since there's
no real device to ask).

**IEM G4** — captioned `L` / `R` bars side by side, each with a dB readout
underneath, MUTE/frequency readout at the bottom:

```
 ● My Configured Name     <- Preferences -> IEM -> Name
   Device's Own Name      <- reported by the device itself (or "--")
  L   R        <- captions
 ███ ███
 ███ ███       <- stereo AF level, ~38 finely-spaced segments
 ███ ███
  0  -22       <- dB readout per channel (0=full scale, floored at -135)
 520.125 MHz   <- MUTE takes priority over this when muted
```

Preferences → IEM → "Show AF level" (one switch, applies to all 4 IEM
slots) turns the whole AF section off — no meters, no L/R data even pulled
out of the cyclic stream on the network side — leaving just name and
frequency in a strip that shrinks to match (`IEM_STRIP_HEIGHT_COMPACT`,
63px, vs. 234px with AF on). Rows aren't forced to a uniform height
anymore: if every IEM slot has AF off, the row they're in is genuinely
shorter, and the surrounding box and web view resize to match — see
"Layout" above.

**EW-DX EM2 (mic channel)** — diversity squares above the RF meter, then
captioned `RF` / `LQI` / `AF` bars side by side, the battery, then
MUTE/frequency at the bottom (same convention as IEM):

```
 ● My Configured Name
   Device's Own Name
  [A][B]          <- diversity, active antenna lights green
 RF  LQI  AF      <- captions
 ███ ███ ███
 ███ ███ ███      <- AF now ~17 finely-spaced segments (was 6)
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

**AF bars are now dense** (`SegmentBar(dense=True)`): instead of a fixed
6-segment step meter, the segment count is computed from the bar's actual
available height at paint time (~3px segments + 1px gap), giving a much
finer, closer-to-continuous look — WSM's own meters read this way. RF and
LQI stay at the original coarse 6-segment style, which suits a
signal-quality indicator fine; this only applies to AF, both here and on
the IEM side.

**Status dot color** has three states: green = connected, red =
disconnected, **orange = this channel is simulated** (a simulated client
always reports itself "connected", so orange is what actually distinguishes
made-up demo data from a real live reading).

RF arrives in dBm but the bar needs a 0-100% fill, so `RF_DBM_FLOOR` (-95)
and `RF_DBM_CEILING` (-25) in `device_widgets.py` define that *display*
window — deliberately narrower than the protocol's full documented -107..0
dBm range (`RSSI_DBM_MIN`/`MAX` in `device_network.py`), since a receiver
sitting anywhere in the "good" part of that huge range would otherwise look
identically full. This affects the **bar only** — the readout always prints
the true dBm value. Likewise `AF_DBFS_FLOOR`/`AF_DBFS_CEILING` in
`device_network.py` map the mic's dBFS audio level onto its 0-100% bar.

IEM's AF is reported as 0-100% ("at 0 dB", per TI 1254 v1.0), not dBFS, so
the L/R dB readouts use `20*log10(pct/100)` — 100% → 0dB, halving amplitude
→ -6dB, etc. — floored at `IEM_AF_DB_FLOOR` (-135) to avoid -infinity at 0%.
**Confirmed against a calibrated reference**, not just estimated: a signal
generator at +4dBu through -30dB sensitivity read -10dBFS on WSM and
exactly -10dB here too — the formula matches WSM's own internal
calculation, not just approximately.

**The bar fill uses that same dB value too, not the raw percentage** —
mapped through a separate, much narrower window, `IEM_AF_BAR_DB_FLOOR`
(-40) to `IEM_AF_BAR_DB_CEILING` (0), the same "narrow display window,
independent of the readout" pattern RF/LQI/mic-AF already use. Comparing
against real WSM side by side (see "Real-hardware findings" below) showed
this genuinely matters, not just for cosmetics: a bar filled from the raw
linear percentage doesn't look like a dB meter *at all* — a receiver at
-10dB would only reach ~7% up a bar mapped across the full -135dB range,
while a real meter (WSM included) shows that as most of the way up. `-40`
is an estimate from where WSM's own tick marks (-10/-20/-30dB, visibly
evenly spaced) stopped being shown in that comparison, confirmed by eye
("scaling of bars looks reasonable") rather than against a calibrated
reference the way the readout formula above now is -- adjust it if it
turns out to need it.

## Real-hardware findings

### Mic (EW-DX EM2): AF level needed a subscription, not a poll

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
distinction. The AF meter is bars-only again (no numeric readout) per your
follow-up request.

### IEM (SR IEM G4): confirmed — the SR firmware rejects flags=7 for `Push`

Debug logging (`SQX_G4_DEBUG=1`) settled this. Every SR device logged the
same thing on every subscription attempt:

```
G4 [IEM 1]: device reported an error: 1020: Value out of range [ Push 60 1000 7 ]
```

The device was rejecting our `Push` subscription outright — which explains
the actual symptom precisely: frequency/name/mute (one-shot GET commands,
sent once in `_bootstrap()`, nothing to do with `Push`) kept working, while
every *cyclic* attribute (AF, States, Msg, Config — all delivered only
through an active `Push` subscription) never arrived, because the
subscription itself never got established.

TI 1254 v1.0's own flag table explains why `7` specifically: the 3rd `Push`
parameter is a 3-bit field — `+1` config-on-change, `+2` cyclic-on-warning-
change, `+4` cyclic-on-change-of-pilot-signal-or-battery-status, and that
`+4` bit is explicitly labeled `(EM only)` in the spec. `7 = 1+2+4`
includes it. An SR transmitter has no pilot signal or battery of its own to
report that way, and apparently the firmware doesn't just ignore that bit
when it's irrelevant — it rejects the whole value as out of range.

**The fix:** `G4Device._send_push()` now sends `flags=3` (the two
device-agnostic bits only) for SR devices, keeping `flags=7` for EM. Same
one-line rejection this debug round would show if this guess is also
wrong, so if AF still isn't moving, running with `SQX_G4_DEBUG=1` again
will show immediately whether the subscription is now accepted or whether
a *different* value is still out of range.

(An earlier theory — that the spec's own inconsistent casing of the SR's
AF example, `Af` vs. its header's `AF`, was the cause — turned out not to
be it, though the case-insensitive parsing that fix added is harmless and
stays in place.)

### IEM AF level, take two: the bar was linear, WSM's meter isn't

With AF actually flowing (the `Push` fix above), a side-by-side comparison
against real WSM showed the numbers reading noticeably different — WSM's
bars sat much fuller than ours for what looked like the same signal.

The bug: the dB readout under each L/R bar was log-scaled
(`20*log10(pct/100)`), but the **bar itself was still filling from the raw
linear percentage** — a leftover from before the readout existed. A linear
bar and a log-scaled number will never agree with each other, let alone
with a real dB meter. Fixed by deriving the bar fill from the same dB value
as the readout, mapped through its own narrow display window
(`IEM_AF_BAR_DB_FLOOR`/`CEILING`, -40..0) instead of the readout's -135
absolute floor — see "Channel strip parameters" above for the reasoning
and an example curve. The `-40` floor is an estimate from where WSM's own
tick marks stopped being visible in the comparison screenshot, not a
documented value.

**Confirmed with a calibrated reference afterward:** a signal generator at
+4dBu through -30dB sensitivity read -10dBFS on WSM and exactly -10dB here
too, and the bar scaling was reported as looking reasonable by eye. The
readout formula match is a real confirmation, not just a visual impression
-- the same `20*log10(pct/100)` calculation independently landed on WSM's
own number for a known, calibrated input.

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
IEM_AF_ENABLED = true   ; section-level switch, see Preferences -> IEM -> "Show AF level"
IEM1_ENABLED = true
IEM1_NAME = IEM 1
IEM1_IP =
IEM1_PORT = 53212   ; G4 Media Control Protocol's fixed port
; no IEM1_CHANNEL -- an SR IEM G4 has no channel-select concept, one
; physical unit is one channel, so there's nothing to configure here
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

## Debugging the network clients

Set an environment variable before launching to see raw protocol traffic on
the console — the fastest way to diagnose a device that isn't behaving as
expected, real hardware included:

```bash
SQX_G4_DEBUG=1 python3 main.py     # every raw line G4Device (IEM) receives
SQX_SSC_DEBUG=1 python3 main.py    # every raw message SSCEM2Device (mic) receives
SQX_NET_DEBUG=1 python3 main.py    # both
```

Error responses from a G4 device (`1020: Value out of range [...]`, etc.)
and `Push` subscription acknowledgments always print regardless of these
flags, since they're rare and high-value to see.

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