# Does the Reims recording contain enough of the target manoeuvre?

Type: task
Status: resolved

## Question

Tickets 14 and 18 now depend on labelling **left turns** — the manoeuvre that crosses oncoming
traffic in right-hand traffic — in the Reims recording, and **scoring** teams against that
sealed set.

Nobody has confirmed the recording contains enough of them.

What is known: one continuous session of ~38 minutes, 1 102 384 messages, ~18 GB, at
`D:\Bags\Data Hackathon\2025-07-30 Recording sessions`. Yaw rate is available from
`/zed/zed_node/imu/data.angular_velocity.z`; speed from `/fix_velocity`; objects from
`/zed/zed_node/obj_det/objects`.

Establish:

- **How many left turns occur**, and how many are at junctions where oncoming traffic is genuinely
  crossed rather than a quiet turn or a roundabout exit.
- Their distribution across the drive — clustered or spread.
- Whether the count supports a development/sealed split at all, or whether the whole session must
  be the sealed set with no Reims development data for teams to iterate against.
- Whether `obj_det/objects` carries anything usable for judging conflict, or whether "unprotected"
  stays scenario context here too, as ticket 18 decided for Kashiwa.
- Whether the second, small MCAP in that folder is a fragment or a separate session.

## Why this blocks

A sealed generalisation test cannot rest on an assumption about event counts. If the answer is
"four left turns in 38 minutes", the transfer task needs redesigning — more collection, a
different manoeuvre, or a qualitatively judged rather than scored transfer.

## Also establish, for ticket 25

The extension track (ticket 25) detects passes in front of champagne caves by GNSS. It is only
viable if the drive actually passes a usable number of them, so the same survey should answer:

- **Which city is this**, from the `/fix` track. Champagne caves points at Reims or Épernay, but
  that is inference from the premise, not something anyone has read off the data.
- **The route's extent and shape** — a bounding box and a rough path, enough to check against a
  list of cave locations.
- **How many known caves the route plausibly passes**, and whether they are clustered on one
  street or spread across the drive.
- **GNSS quality** — fix status, visible satellite count, and how much the position jitters when
  stationary. This sets the zone radius in ticket 25 and decides whether the track works at all.

## Method

Decode `/zed/zed_node/imu/data` and `/fix_velocity`, integrate heading, and count sustained
positive yaw-rate excursions above a walking-pace speed floor. Needs `mcap` and
`mcap-ros2-support`; the bag carries its own schemas, so no ROS installation is required.

## Progress - tooling resolved, structure measured

The `mcap` CLI is available at `C:\Program Files\MCAP\mcap.exe` and on PATH, so **no CLI install
is needed**. It handles `info`, `du` and `filter`; its JSON output does not decode `ros2msg`, which
is why the final survey uses ephemeral Python packages through `uv` below.

Established so far:

- The session is **9 chunks totalling 28.1 GB**, ~38 minutes, 8 channels. Chunk 0 covers 4m21s.
- Topic rates: `/tf` 229 Hz, `/zed/.../imu/data` 191 Hz, point cloud / RGB / objects ~19 Hz,
  `/fix` and `/fix_velocity` **4 Hz**.
- Per-topic byte breakdown recorded in ticket 17 - signals are 1.2% of the file.

## Answer — measured and visually validated

### Tooling correction

The `mcap` CLI can inspect and size `ros2msg` channels, but `mcap cat --json` cannot decode them.
The survey therefore used `uv run --no-project` with `mcap` 1.4.0 and
`mcap-ros2-support` 0.5.7. The reproducible streaming helper is
`../research/survey_reims_bag.py`; no project environment or intermediate message dump is
required.

Decoded counts across the nine chunks:

| Topic | Messages |
|---|---:|
| `/fix` | 9,112 |
| `/fix_velocity` | 9,112 |
| `/zed/zed_node/imu/data` | 435,113 |
| `/zed/zed_node/obj_det/objects` | 42,786 |

### Left turns: enough for development and sealed sets

A 0.15 s EMA over yaw rate, 0.06 rad/s positive-yaw threshold, 0.5 m/s speed floor, short-gap
merge and 20 degree minimum produced **25 signal candidates**. The count is stable under stricter
settings: 20–22 candidates remain at a 30 degree minimum, and 16 remain at 45 degrees.

GNSS course change confirmed the yaw sign and magnitude. Before/mid/after camera frames then
separated manoeuvres from road geometry:

- **16 clear junction-left manoeuvres**;
- **2 borderline junction/traffic-island cases**, both in the development portion;
- 6 curves, roundabout/U-turn or roadworks cases;
- one stop-split manoeuvre emitted as two adjacent yaw excursions and merged into one label.

The clear events are spread across the drive rather than clustered at one moment. The natural file
boundary is also the pedagogically useful split:

| Set | Chunks | Duration | Clear events |
|---|---|---:|---:|
| Development | `_0`–`_4` | ~21m49s | 7, plus 2 borderline teaching cases |
| Sealed | `_5`–`_8` | ~16m09s | 9 |

Participants receive the first five signals-only chunks. The final four stay with the organizers.
This supports the scored transfer task without leaking its labels and resolves ticket 17's Reims
distribution dependency.

These are planning-grade counts, not sealed ground truth. The labelling pass must still set the
full intervals and review edge cases; internal evaluation may refine labels without changing the
five-chunk/four-chunk split.

The confirmed Detection split is **15 Kashiwa / 10 Reims**, provisional until ticket 16's
internal evaluator run shows how both sealed sets affect ranking.

### Objects help evidence, not the definition

`obj_det/objects` contains `VEHICLE` and `PERSON` detections with confidence, 3D position,
velocity and tracking state. Objects appear in 82% of frames; vehicles appear around every clear
turn candidate. That makes the topic useful for evidence and failure analysis.

It does **not** carry lane association, road topology or right-of-way state. It cannot establish
that a vehicle is oncoming or that the manoeuvre is protected. "Unprotected" therefore remains
scenario context; sealed labels mark the interval of the turn that crosses the opposing lane by
road geometry, consistent with ticket 18.

### Route, caves and GNSS

The main session is a 13.3 km drive in **Reims**, bounded by:

- south 49.234444, west 4.035455;
- north 49.265558, east 4.061915.

Officially documented cellar addresses were geocoded through Nominatim and compared with the
private track locally; no route coordinates were sent to a public service. The route's nearest
approaches are:

| Cellar | Nearest route point |
|---|---:|
| G.H. Martel | 15.6 m |
| Pommery | 35.7 m |
| Ruinart | 65.4 m |
| Taittinger | 127 m |
| Veuve Clicquot | 250 m |

At a 40 m radius, the extension track therefore has **two clear zone encounters**: Martel and
Pommery. It is viable as a small external-resource exercise, not as a rich many-cave hunt.
Address provenance: [City of Reims cellar directory](https://en.reims.fr/visit-reims/cellars-in-champagne),
the published visitor addresses for [Taittinger](https://www.taittinger.com/faq),
[Ruinart](https://www.ruinart.com/fr-fr/foire-aux-questions.html) and
[Veuve Clicquot](https://www.veuveclicquot.com/fr-FR/conditions-generales-de-vente), plus
OpenStreetMap/Nominatim (© OpenStreetMap contributors).

Every fix has status 0 and known covariance (type 2). Reported horizontal sigma is 0.73 m median,
0.97 m at p95 and 4.36 m maximum. Across 18 stops of at least 5 s:

- median per-stop p95 radial jitter: **0.26 m**;
- p95 of those stop values: **0.81 m**;
- maximum observed radial displacement: **1.32 m**.

`NavSatFix` has no satellite-count field, so visible satellites cannot be recovered from this
recording. The empirical quality is nevertheless comfortably sufficient for the zone exercise.

### The standalone MCAP is a separate session

`rosbag2_2025_07_30-17_00_08_0.mcap` is a prior-day **GNSS-only drive**, not a fragment of the
main session: 16m43s, 4.29 km, with 4,014 fixes and 4,014 velocity messages but no IMU, objects or
camera. Its route stays more than 1 km from the nearest checked cellar, so it adds nothing to the
extension track.
