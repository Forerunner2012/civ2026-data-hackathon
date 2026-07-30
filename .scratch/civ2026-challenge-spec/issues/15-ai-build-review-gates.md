# What are the review and test gates for AI-built tooling?

Type: grilling
Status: open

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
