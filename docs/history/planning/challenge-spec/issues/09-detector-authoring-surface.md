# Is the detector surface CEL-only, or CEL plus a Python API?

> Historical planning. Follow the [archive index](../../README.md) for current guides and record boundaries.

Type: prototype
Status: resolved

## Question

`HACKATHON-HANDOFF.md` §8: EventSpec with CEL only, or EventSpec plus an advanced Python
detector API?

`docs/history/planning/exploration/exploration-notes-INBOX.md` sketches both shapes — a declarative `condition` /
`evidenceWindow` / `topicsToCollect` YAML, and a `def detect(signals) -> list[EventCandidate]`
escape hatch — without choosing.

## Why this is a prototype ticket

This is not answerable by argument. **Write a URT reference detector in CEL first.** If an
unprotected right turn can be expressed declaratively — heading change over time, plus
oncoming-lane occupancy, plus a speed profile — CEL-only holds and the Python API is scope you
do not need. If it cannot, the answer is forced and the bonus track has somewhere to live.

Note from ticket 02: the existing INBOX example is *hard-braking*, not URT. This ticket produces
the first real URT spec, which several later artifacts depend on.

Produce and link:

- A URT EventSpec in CEL against real Kashiwa bags, with the topics and fields it needs.
- An honest note on what it could not express.
- A rough sense of whether a mixed-skill team could have written it in the 30-minute Formalize
  block, or whether it needs a stronger warm-up.

## Why this is on the frontier

Nothing blocks it. It unblocks ticket 16 (you cannot calibrate an evaluator without knowing
what a submission looks like) and graduates the warm-up and fallback-pack fog.

## What the previous event actually supported

From the setup script (ticket 06): a flat list of `(signal, operator, scalar)` conditions
combined with an implicit global AND, plus a fixed `{signal_id, start, end}` evidence window per
recorded topic.

```json
[ {"signal_id": TURN,   "operator": "LESS_THAN", "value": {"double": …}},
  {"signal_id": OBJECT, "operator": "EQUAL",     "value": {"boolean": true}} ]
```

No OR, no arithmetic, no duration, no derived features. **CEL is already a large step up from
this**, which reframes the question as how far above that line to go — not whether CEL is enough.

## Answer

**EventSpec carries rungs 1 and 2. Rung 3 is deferred.**

```yaml
spec: civ.eventspec/v1
name: unprotected-right-turn

signals:                       # bind names to topic + field
  yaw_rate:       { topic: /localization/acceleration, field: accel.accel.angular.z }
  speed:          { topic: /vehicle/status/velocity_status, field: longitudinal_velocity_mps }
  object_present: { topic: /perception/object_recognition/is_object_detected, field: data }

derive:                        # RUNG 2 — declarative preprocessing
  yaw_smooth: { from: yaw_rate, op: ewma, alpha: 0.2 }

condition: >                   # CEL — the floor
  yaw_smooth < THRESH && speed > MIN_SPEED

timing:                        # RUNG 1 — what makes it an interval
  min_duration: 1.2s
  merge_gap:    0.8s
  max_duration: 15s

evidence:
  before: 4s
  after:  6s
  topics: [ /localization/acceleration, /vehicle/status/velocity_status,
            /sensing/camera/traffic_light/image_raw ]
```

All values above are **placeholders**. Real thresholds get derived from the data; the previous
solution's tuned numbers stay behind the clean-room line (ticket 06).

### The rungs

| Rung | Content | Who reaches it |
|---|---|---|
| 0 | One CEL comparison, no timing | Everyone, first 30 minutes |
| 1 | CEL + `timing` + `evidence` | **Pass mark — expected of every team** |
| 2 | `derive` stage, multi-signal OR/nesting, transitions | Strong teams |
| 3 | Python detector, conflict geometry from `detected_object` pose | **Deferred** |

**Rung 1 is non-negotiable** because ticket 18 made the labels intervals. Without `timing`, a
team emits one detection per *sample* where yaw rate was high, not one per turn. That block is
what converts "a threshold fired" into "a turn happened", and it is where the interval-precision
points live.

**Rung 2 delivers what §4.5 promises.** Attendees genuinely own preprocessing and derived
features, declaratively, without a second runtime.

### Rung 3 is deferred, not cancelled

Python detectors and conflict geometry — *was a road user actually in the crossing path?* — move
to the **organizer demo and an extra track**, to be designed **once the main track is complete**.
Rationale: the main track has to be finished and rehearsable before effort goes into a ceiling
almost nobody will reach, and deferring it keeps the scored core on one deterministic declarative
path that is trivial to sandbox, reproduce and compare.

This means the EventSpec schema should leave room for a `detector:` key without specifying it
now — a reserved seam, not an implementation.

### One thing to state plainly in the brief

The line is not "attendees may not write Python" — teams can preprocess bags however they like
beforehand, and that is unenforceable and not worth policing. The line is **what the runner
executes for the scored submission**. Say so explicitly rather than leaving teams to infer it.
