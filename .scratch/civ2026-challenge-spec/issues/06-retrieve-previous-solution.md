# Retrieve and review the previous hackathon's solution

Type: task
Status: resolved

## Question

Nothing to decide here — this retrieves an artifact that two later decisions wait on.

Locate the previous CIV hackathon's solution and reference material, and record in this ticket:

- Where it lives and what form it takes (repo, notebooks, slides, Heex project export).
- Which parts were **Heex product** versus organizer-written glue.
- How events were expressed, and what the detection contract looked like.
- What was scored, and how ground truth was produced and held.
- Which event types teams actually caught beyond the intended one.
- What visibly failed or ran long, if that was recorded anywhere.

The user offered to point at this directly — ask rather than search blind.

## Why this is on the frontier

Blocks ticket 07 (clean-room boundary): you cannot draw a line against an implementation you
have not seen. Also feeds ticket 16 — the prior event's outcomes are the only real calibration
data available before the internal mini-hackathon.

## Notes

HITL: the human supplies the pointer, the agent does the review. Once retrieved, link the
artifact from this ticket rather than pasting it in.

## Answer

### Sources (read-only, outside this repo — not copied in)

- `D:\heex\demo-showcase-win\04-hackathon-urt-kashiwa-demo` — viewer layouts, a data shortcut,
  and a scripted hands-on walkthrough recorded 22 Oct 2025.
- `D:\heex\r-i\heex-samples\02-hackathon-urt-kashiwa-demo` — attendee instructions, run-of-show
  script, and the solution key.

### Extraction boundary applied

Per instruction, only the **logic combination** and the **workflow leading from raw bags to
captured evidence** were extracted. Deliberately **not** carried across:

- The product entity model, its CLI verbs, its session/replay mechanics, and the setup scripts.
- **The previous solution's tuned numeric thresholds.** They exist and were recorded per signal,
  but §3.3 protects historical thresholds, and re-deriving them from the data is both the
  cleaner position and better engineering — a threshold nobody on the team can defend from the
  physics is a liability in a scored event. Ticket 07 should confirm this line.
- Product naming and UI.

### The dataset, as it actually is

Facts any attendee would find by inspecting the bags:

- **16 bags**, ~3 minutes each, **~7 GB each (~112 GB total)**, ~400 000 messages per bag.
- MCAP plus a `metadata.yaml` descriptor per bag; directories `final_route_02` … `final_route_18`
  (note the gaps — no 01, no 10).
- Autoware-style topic namespace. Some signals need **custom message packages**
  (`tier4_vehicle_msgs`, `pix_hooke_driver_msgs`), which is what §5 Phase 2's "embed or bundle
  custom ROS schemas" is about — now confirmed as required, not hypothetical.
- Scenario families present in the data: emergency stop, unprotected right turn, right turn with
  oncoming vehicles, right turn with pedestrians, pedestrian crossing.

### Signals that carried the detection

- `/localization/acceleration` (`geometry_msgs/AccelWithCovarianceStamped`)
  - `.accel.accel.linear.x` — longitudinal acceleration, the braking signal.
  - `.accel.accel.angular.z` — yaw rate, the turn signal. Sign follows REP-103: positive is
    counter-clockwise (left), so a right turn is negative.
- `/perception/object_recognition/is_object_detected` (`std_msgs/Bool`) — a bare presence flag.
- `/perception/object_recognition/detected_object` (`visualization_msgs/Marker`) — position and
  orientation of a detection.
- Alternates and guards: `/sensing/imu/imu_data`, `/sensing/gnss/chc/imu`,
  `/vehicle/status/steering_status`, `/vehicle/status/velocity_status`,
  `/vehicle/status/gear_status`, `/vehicle/status/actuation_status`, `/pix_hooke/*`.

Explicitly noted in the source: signals like speed or twist **require preprocessing** before
they can be used in a bare comparison — which is exactly the "derived features" the CIV 2026
ownership boundary (§4.5) hands to attendees.

### The logic combination

Three detectors of increasing ambition, all expressible as threshold comparisons combined with
boolean AND:

1. **Emergency stop** — longitudinal acceleration below a negative threshold. Single condition.
2. **Basic turn** — yaw rate beyond a threshold, sign selecting the direction. Single condition.
3. **Unprotected right turn** — *(turn condition)* **AND** *(object-present flag is true)*.
   Optional extra AND guards, all chosen because they need no preprocessing: steering enabled,
   no steering out-of-range warning, longitudinal velocity above a walking-pace threshold, gear
   within the drive range.

### The finding that matters most

**The previous "unprotected right turn" detector was really "a right turn while something was
detected".** It had no notion of oncoming-lane geometry, gap acceptance, or conflict — and
`is_object_detected` is a plain boolean that cannot distinguish a pedestrian from a vehicle
without parsing the marker topic. The rubric even acknowledged this, accepting the flag because
it "satisfies oncoming vehicles or pedestrians without extra parsing".

That approximation was fine for a tool-operation exercise. It is **not** fine as the basis for
sealed ground truth: you cannot label what you have not defined. See new ticket 18.

### The workflow, in the previous event's shape

Prepare data → environment setup (optionally building custom messages) → model the vehicle and
its topics → declare signals → author and deploy conditions → replay all bags to generate events
and recordings → analyse event frequency and statistics → clean up.

Mapped onto the CIV 2026 vocabulary this is: `inspect` → `sample` → author EventSpec → `detect`
across the dataset → `clip` → `score`/`report`. The shape carries over cleanly; the tooling does
not, and does not need to.

### Viewer

The layouts are **Foxglove-family** (Lichtblick lineage) — panel types present are 3D, Image,
Plot, RawMessages and StateTransitions, over camera, point-cloud, GNSS and acceleration topics.
The previous event needed camera and 3D context to judge a turn, not time-series alone. Direct
evidence for ticket 10.

### What was scored, and how it differs

100 points, roughly: 15 for creating the tool's entities, 35 for condition logic, 50 for
generating events plus statistical analysis and a written training/evaluation/operations
rationale. Bonus 15 for an optional pedestrian-crossing detector. Submission was a list of CLI
commands, entity IDs, statistics and the written rationale.

**Around half the score was tool operation.** CIV 2026's §4.6 rubric deliberately spends those
points on evidence, quality, visualization and reproducibility instead — this comparison is the
clearest statement of the 2026 shift, and worth keeping.

No ground truth was sealed and no accuracy was measured: teams were scored on having built the
thing, not on whether it found the right events. **There is therefore no historical calibration
data** — ticket 16 must generate its own, and the internal mini-hackathon is the only source.

### Consequences raised elsewhere

- **New ticket 17** — 112 GB will not reach BYOD laptops offline. Subsetting and distribution.
- **New ticket 18** — an operational definition of "unprotected right turn" for labelling.
- **Ticket 07** is now unblocked.
- **Ticket 10** gains strong evidence that time-series alone was insufficient.
- **Ticket 09** — the previous logic is entirely thresholds plus AND, so CEL is sufficient *for
  that level of ambition*. A geometric URT definition (ticket 18) may not be.
