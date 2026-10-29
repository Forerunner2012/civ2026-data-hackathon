# How does 112 GB reach BYOD laptops offline?

> Historical planning. Follow the [archive index](../../README.md) for current guides and record boundaries.

Type: grilling
Status: resolved

## Question

Surfaced by ticket 06. The dataset as published is **16 bags, ~7 GB each, ~112 GB total,
~400 000 messages per bag**. Ticket 04 fixed the environment as **BYOD containers, offline**.
Those two facts do not currently fit together, and nothing in §6's "CPU/laptop-sized variant and
distribution plan" has been sized.

What has to be settled:

- **How much data does a team actually need?** The three-hour ladder needs one warm-up bag, a
  handful of development bags, and a sealed test set the teams never hold. That is not 16 bags on
  every laptop.
- **What is the reduction?** Topic filtering is the big lever — dropping camera and point-cloud
  topics collapses size by orders of magnitude, and the URT logic (ticket 06) runs off
  acceleration, velocity, steering, gear, GNSS and object topics, not RGB. But ticket 10 suggests
  visual context is what makes a turn judgeable, so this trades directly against evidence quality.
  Note ticket 19 may force the camera decision anyway.
- **Time-window trimming** as a second lever: keep the segments around candidate events plus
  margin, rather than whole routes. Risk: this leaks where the events are.
- **How is it physically distributed?** With no venue download assumption and no organizer
  hardware, the realistic options are USB-C SSDs handed out, a pre-event download link, or a
  local LAN share in the room. Each has a failure mode; the pre-event download is the only one
  that does not consume session time.
- **Disk space on a BYOD laptop** is itself a prerequisite to publish alongside the RAM floor.

**Correction on what the constraint actually is.** MCAP is read as a *stream* with an index —
neither the runner nor Polars holds a whole bag in memory, so a 7 GB bag does not need 7 GB of
RAM. 16 GB is a comfort recommendation, not a gate. The binding constraints are therefore
**transfer size, disk space and per-bag processing time**, not memory. That means the reduction
below is justified by what attendees can realistically download and store, not by what their
machine can compute over — and if transfer turns out to be cheap, keeping more data costs little.

## Why this is on the frontier

Nothing blocks it. It is a hard constraint on ticket 04's environment and on the warm-up design
sitting in the map's fog.

## Note

Ticket 05 established that redistributing subsets is expressly permitted under CC BY 4.0 and that
attendees may keep them permanently; ticket 19 confirmed the camera topic is cleared, so this is
a pure size-and-logistics question, not a rights one. Attribution travels with the subset.

One thing worth doing early regardless of the answer: **take a pinned local copy of all 16 MCAPs
with checksums**, since the published distribution is a Drive folder the publisher can change at
any time. That is cheap insurance, not a deadline.

## Answer

### Split

| Set | Routes | Distributed | Labels |
|---|---|---|---|
| Warm-up | 1 | yes | fully published |
| Development | 7 | yes | partial |
| Sealed test | 8 | **never** | held by organizers |

### Reduction

- **Drop point clouds and the map entirely.** `/map/pointcloud_map` and the
  `/perception/object_recognition/detection/clustering/*/pointcloud` topics are the bulk of the
  7 GB and contribute nothing to an interval-based right-turn detector.
- **Keep every scalar topic at full rate** — localization, acceleration, vehicle status, GNSS,
  IMU, object flags. These are small and are where the detector actually operates.
- **Keep `/sensing/camera/traffic_light/image_raw`, downscaled and rate-limited** (target ~5 Hz
  at 640×360). Preserves the evidence and pitch value that ticket 10 depends on at a fraction of
  the size. Ticket 19 cleared the imagery.

**Target: ≤ 15 GB for the 8 distributed routes.**

### Distribution

Pre-event download with published checksums as the primary path — it is the only option that
consumes no session time and it pairs with the pre-arrival setup the BYOD decision (ticket 04)
already requires. USB SSDs at the venue as the fallback. The container image ships separately so
a failed data download does not also cost the environment.

### Required next step, before the numbers are trusted

**Measure per-topic bytes on one bag** (`civ inspect`, or a plain MCAP topic-size pass) and
confirm the reduction actually lands under target. The 15 GB figure is derived from the stated
7 GB per bag and the assumption that point clouds and raw camera dominate — plausible from the
topic list, but unverified. If camera cannot be reduced enough, the fallback is to keep it on the
warm-up route only, and ticket 10's Lichtblick decision falls with it.

Also worth doing early, independent of the answer: **take a pinned local copy of all 16 source
MCAPs with checksums**, since the published Drive folder can change at any time (ticket 05).

## Update - a second dataset now has to be distributed

Ticket 14's reversal puts the Reims recording in participants' hands. That adds to this
ticket rather than changing what is above:

- A **Reims subset** must be cut and distributed alongside the Kashiwa one. Source is ~18 GB for
  a single 38-minute session, so the same levers apply: drop the ZED point cloud
  (`/zed/zed_node/point_cloud/cloud_registered`), keep IMU, GNSS, fix velocity and object topics
  at full rate, keep `rgb/image_rect_color/compressed` - already compressed, so cheaper than
  Kashiwa's raw camera.
- Ticket 24 resolves the **Reims development/sealed split** at a natural file boundary:
  chunks `_0`–`_4` are development (~21m49s, 7 clear left turns plus 2 borderline teaching
  cases); chunks `_5`–`_8` stay sealed (~16m09s, 9 clear left turns).
- The Reims stack shares **no topics** with Kashiwa, so it needs its own topic inventory and its
  own viewer layout. That is real preparation work, not a copy.

## Update - MEASURED. The size problem was an illusion.

Measured with the `mcap` CLI (`<tools-root>/MCAP/mcap.exe`, on PATH) against Reims chunk 0
(3.22 GB, 4m21s, 127 102 messages, uncompressed chunks):

| Topic | Bytes | Share |
|---|---|---|
| `/zed/zed_node/point_cloud/cloud_registered` | 2.30 GB | **71.5%** |
| `/zed/zed_node/rgb/image_rect_color/compressed` | 877 MB | **27.3%** |
| `/zed/zed_node/imu/data` | 16.6 MB | 0.52% |
| `/zed/zed_node/obj_det/objects` | 15.4 MB | 0.48% |
| `/tf` | 7.2 MB | 0.22% |
| `/fix_velocity` | 372 kB | 0.01% |
| `/fix` | 134 kB | 0.004% |

**Every signal a detector operates on is 1.2% of the bytes.** Extrapolated across the 9 chunks
(28.1 GB on disk for the full 38-minute session):

- **signals only: ~350 MB**
- signals + compressed images: **~8 GB**
- point cloud alone: **~21 GB**, and it contributes nothing to any track in this event

### What this changes

- **The 15 GB target and the "8 of 16 routes" split were solving a problem that does not exist.**
  Size stopped being the constraint the moment images and point clouds came off. The dev/sealed
  split still stands, but it is now justified **only by pedagogy** — you need a sealed set — not
  by bytes.
- **Ship signals-only as the default distribution.** It fits anywhere, downloads in seconds, and
  it is the complete input surface for detection, timing, transfer and the geofence track.
- **Images become an optional context pack**, per the organizer's direction that video and images
  are "highly contextual (can be stripped for faster pipelines when prototyping/testing)". This
  also settles ticket 10's contingency: PlotJuggler over signals is the required path, and image
  context is an opt-in extra rather than a distribution problem.
- **The progressive plan still helps, for a different reason.** Starting with roughly a quarter of
  the data by SSD and expanding as people settle their pipelines is now about *iteration speed*,
  not disk space. A smaller working set means faster runs while prototyping.
- **The "send only CLI calls to the organizer's machine" option** stays valuable for full-resolution
  or image-heavy work, and it has a side benefit worth naming: a run that only exists as a CLI
  invocation someone else executes is **reproducible by construction**, which is exactly what the
  Reproducibility category (15 points) is trying to measure.

### Still unmeasured

**Kashiwa has not been measured** - this ratio is from Reims data. Kashiwa carries *uncompressed*
`image_raw` plus clustering point clouds, so its signal fraction is likely even smaller, but that
is inference. Run `mcap du` on one Kashiwa route before fixing the numbers.
