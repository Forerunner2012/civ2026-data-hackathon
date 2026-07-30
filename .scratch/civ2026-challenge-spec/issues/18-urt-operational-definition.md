# What is an "unprotected right turn", operationally?

Type: grilling
Status: resolved

## Question

Surfaced by ticket 06, and it is the sharpest finding from the previous event.

**The previous hackathon's "unprotected right turn" detector was really "a right turn while
something was detected"** — a yaw-rate threshold ANDed with a bare
`/perception/object_recognition/is_object_detected` boolean. It had no notion of oncoming-lane
geometry, gap acceptance or conflict, and the presence flag cannot distinguish a pedestrian from
a vehicle without parsing the marker topic. The prior rubric accepted this openly, because it was
scoring tool operation rather than detection accuracy.

Ticket 03 changed that: CIV 2026 scores detection against **sealed labels**. You cannot label
what you have not defined, and "a right turn while something was detected" is not a definition a
jury can defend when a team disputes a false negative.

What has to be settled:

- **What makes a right turn "unprotected" in this data?** Absence of a protective signal phase?
  Presence of a conflicting road user in the opposing or crossing path? A gap-acceptance
  judgement? Something simpler that is still honest?
- **Does the answer need geometry** — relative position and heading from the marker topic — or
  can it stay in the space of scalar comparisons? This determines whether CEL suffices
  (ticket 09) or whether a Python escape hatch is forced.
- **What is the event's extent?** A turn is an interval. Where does it start and end — steering
  onset, yaw-rate threshold crossing, entry to the junction box? Ticket 16's tolerance semantics
  depend entirely on this.
- **Can a labeller apply the definition consistently** to 16 routes without ambiguity, and what
  is the inter-annotator agreement target?
- **Is a proxy acceptable, if named as one?** Scoring a well-specified proxy — "right turn with a
  conflicting object present" — and *saying so plainly* is defensible. Silently scoring a proxy
  while calling it URT is not. Decide which you are doing, on the merits.

## Why this is on the frontier

Nothing blocks it, and almost everything downstream depends on it: the sealed label set, the
tolerance semantics in ticket 16, the detector surface in ticket 09, and whether the visual
context in ticket 10 is needed to adjudicate a detection.

## Note

The publisher's own framing is worth keeping: they describe the manoeuvre as "a challenging
manoeuvre for autonomous vehicles (equivalent to unprotected left turns in Europe)" — i.e. the
turn that crosses oncoming traffic. That crossing-conflict framing is the substance the
definition should capture.

## Answer

**The sealed labels mark the right-turn manoeuvre interval.** "Unprotected" is a property of the
site and the scenario the data was staged for — it is context the brief supplies, not something
the detector has to prove.

This is the cheap, high-agreement definition: the dataset was recorded for this manoeuvre across
16 routes, so a labeller marking turn intervals has an unambiguous job, and inter-annotator
agreement should be high without a written adjudication procedure.

### What this makes easier

- **Labelling is tractable** and needs no judgement about conflict, gap acceptance or intent.
- **Ticket 09** gets much simpler: a yaw-rate threshold with duration and debounce is expressible
  declaratively. CEL-only is now the defensible default rather than a hopeful one.
- **Ticket 16** becomes interval matching — overlap or onset tolerance, duplicates, misses —
  rather than an argument about whether a detection was "really" contested.
- **Ticket 10** weakens: a turn interval can be judged from yaw rate and speed alone, so visual
  context is desirable rather than required.

### The cost, recorded rather than argued

**Detection stops separating teams on cleverness.** A single well-chosen yaw-rate threshold gets
most of the way to the answer, so the 25-point detection category cannot reward insight the way a
conflict-based definition would. That is a real consequence of a deliberate choice, and the
design has to absorb it rather than pretend otherwise.

**Where separation comes from instead** — this is the part that now has to be got right:

- **Interval precision.** Onset and end are the hard part. Where does a turn begin — steering
  onset, yaw-rate threshold crossing, junction entry? A team that thinks about boundaries beats
  one that does not, and the tolerance semantics in ticket 16 are what convert that into points.
- **Robustness across all 16 routes.** One threshold tuned on one route will miss or over-fire on
  others. Scale is the discriminator, which is exactly §2's "reusable logic executed across
  multiple bags".
- **Duplicates and debounce.** A turn is one event, not three overlapping detections.
- **The other 75 points.** Hypothesis, evidence, quality, visualization and reproducibility were
  always the majority of the rubric. This choice leans on that harder.

### Where the ambition goes

The conflict-geometry version — *was a road user actually in the crossing or opposing path during
the turn?* — moves **out of the core and into the bonus/advanced track** established in
ticket 03. It is a natural fit there: it needs `detected_object` position and heading rather than
the bare boolean, it is genuinely harder, and it is judged qualitatively, so it never has to be
labelled. Teams that want to prove a turn was *contested* have somewhere to do it.

That keeps the core honest and cheap while leaving the interesting work available — which is what
the "one ladder, not three hackathons" principle in §4.1 asks for.

### Consequence for the brief

The brief must state plainly that the scored event is **the right-turn manoeuvre**, and that the
scenario context is what makes those turns unprotected. Teams should not be left to guess whether
conflict detection is required for the core score.
