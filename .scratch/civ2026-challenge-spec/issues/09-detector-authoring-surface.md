# Is the detector surface CEL-only, or CEL plus a Python API?

Type: prototype
Status: open

## Question

`HACKATHON-HANDOFF.md` §8: EventSpec with CEL only, or EventSpec plus an advanced Python
detector API?

`exploration/exploration-notes-INBOX.md` sketches both shapes — a declarative `condition` /
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
