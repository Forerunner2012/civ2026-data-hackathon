# What are the review and test gates for AI-built tooling?

Type: grilling
Status: resolved

## Question

The plan is to implement most of the tool suite with AI plus careful review — "review, test of
each step and internal try-outs: humans and AI". This ticket turns that into something with a
definition of done, because until it has one, "we'll generate it" is an unbounded estimate
sitting on the critical path.

What has to be settled:

- **What is the gate per component?** The runner, the evaluator and the clip extractor have
  very different failure costs. A wrong evaluator silently mis-ranks teams and nobody notices.
- Which parts must be human-reviewed line by line versus tested behaviourally?
- What test evidence is required before a component counts as done — golden files against known
  bags? Property tests on time semantics? Determinism checks across reruns?
- Who reviews? A single reviewer is a bottleneck at this runway; two is a scheduling problem.
- How do AI-assisted internal try-outs differ from the human mini-hackathon, and can they
  substitute for it, or only precede it?
- What is the rollback rule when a component fails its gate close to the freeze — cut the
  feature, or slip?

## Why this is on the frontier

Nothing blocks it, and it governs how fast everything downstream can honestly be estimated.
The evaluator is the component where a silent defect is most expensive, so gate that first.

## Answer

**Gate by failure visibility × cost, not uniformly.** AI makes it cheap to produce more surface
than anyone can review, so the gate is a throughput limit on *unreviewed surface entering the
kit* — not a limit on generation.

The asymmetry that drives everything: a crashing runner announces itself, but **a subtly wrong
evaluator is invisible and mis-ranks teams**. Nobody would find out, and the event's credibility
is the thing it was supposed to protect.

### Tier A — the evaluator

- **Golden files.** Hand-checked `(bag, detector, expected score)` triples. Any change must
  reproduce them exactly.
- **Determinism.** Score the same submission twice, require byte-identical `metrics.json`.
  Catches dict ordering, float accumulation and parallelism races — all of which AI-written code
  produces readily.
- **Rank test.** The four calibration detectors from ticket 16 must come out in the expected
  order.
- **Human line-by-line review.** The one component where reading every line pays for itself.

### Tier B — runner and CLI

- One behavioural test per verb against a fixture bag.
- `--dry-run` asserted to write nothing.
- Error messages tested for being **actionable** rather than a stack trace. Attendees hit these
  in minute five, and a bad message costs the room fifteen minutes.

### Tier C — clip extraction

Assert clip duration equals `before + after` within tolerance, contains exactly the requested
topics, and re-opens as valid MCAP. One human visual check per change.

### Tier D — docs, layouts, warm-up

Someone who did not write it follows it start to finish. That is the whole gate.

### Three standing rules

1. **Nothing ships without a test that fails if the component breaks.** If that test cannot be
   written, the component is not yet understood well enough to ship.
2. **For Tier A a human writes the assertion**, even when AI writes the code and the test
   scaffolding. Otherwise the test merely encodes whatever the code happens to do — the failure
   mode specific to AI-built tooling, and the one that would silently pass every other gate.
3. **A component that misses its gate gets cut, not slipped.** The main track stays complete;
   the ceiling is already deferred (ticket 09) and is where anything cut should land.
