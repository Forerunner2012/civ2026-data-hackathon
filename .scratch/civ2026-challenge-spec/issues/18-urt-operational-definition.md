# What is an "unprotected right turn", operationally?

Type: grilling
Status: open

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
- **Is the honest fallback acceptable?** If a rigorous definition proves too costly at 35 days,
  scoring a well-specified proxy — "right turn with a conflicting object present" — and *saying
  so plainly* is defensible. Silently scoring a proxy while calling it URT is not.

## Why this is on the frontier

Nothing blocks it, and almost everything downstream depends on it: the sealed label set, the
tolerance semantics in ticket 16, the detector surface in ticket 09, and whether the visual
context in ticket 10 is needed to adjudicate a detection.

## Note

The publisher's own framing is worth keeping: they describe the manoeuvre as "a challenging
manoeuvre for autonomous vehicles (equivalent to unprotected left turns in Europe)" — i.e. the
turn that crosses oncoming traffic. That crossing-conflict framing is the substance the
definition should capture.
