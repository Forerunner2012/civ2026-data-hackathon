# Map: CIV 2026 challenge spec

Label: `wayfinder:map`

## Destination

A complete challenge spec: every decision in `HACKATHON-HANDOFF.md` §8 closed, so five
owners can build the kit without re-litigating anything. The spec is the deliverable —
building the runner, dataset and evaluator is downstream execution, not part of this map.

## Notes

- **Domain:** event design for a three-hour ROS 2 data-investigation hackathon. Source of
  truth is `../../HACKATHON-HANDOFF.md`; `../../exploration/` holds the precedence chain.
- **Skills to consult:** `/grilling` and `/domain-modeling` by default, `/prototype` for the
  detector-surface and visualization tickets, `/research` for the licence ticket.
- **Plan, don't do.** This map produces decisions. The one exception is ticket 06, a task
  that retrieves an artifact a decision waits on.
- **Runway is the binding constraint:** event is under three months out (charted 30 Jul 2026).
  Data collection is already solved; **evaluation and rehearsal are the long poles.** Prefer
  the answer that shortens the path to a frozen, rehearsable kit.
- **Tooling will be AI-built with human review.** Ticket 15 defines those gates; until it
  closes, treat "we'll generate it" as an unbounded estimate.
- As decisions close, update §8 of `HACKATHON-HANDOFF.md` so the handoff and the map agree.

## Decisions so far

- [Which dataset carries the event?](issues/01-dataset-choice.md) — URT-Kashiwa is the hero
  dataset and the freeze depends only on it; French-city bespoke bags are additive-only behind
  a hard drop-dead date.
- [Which scenario anchors the challenge?](issues/02-scenario-anchor.md) — Unprotected right
  turns (URT). Creativity is expected in *how* teams express and capture the scenario with the
  OSS toolchain, not in inventing a different event class.
- [What does the sealed ground truth score against?](issues/03-scoring-basis.md) — Sealed
  labels exist for URT only, keeping the 25-point detection category objective; other event
  types are a qualitatively judged bonus.
- [What machine must the required path run on?](issues/04-target-machine.md) — Container-first,
  BYOD only, Windows/WSL2 + Ubuntu, CPU-only. Risk accepted: setup failure has no hardware
  swap, so the non-ROS fallback pack is load-bearing.

## Not yet specified

Fog — in scope, not yet sharp enough to ticket. Graduates as the frontier advances.

- **Labelling workflow for the sealed URT set** — who labels, in what tool, to what
  inter-annotator agreement. Waits on 05 (rights) and 16 (tolerance semantics).
- **Warm-up design and the non-ROS fallback pack contents** — now load-bearing because of the
  BYOD decision in 04. Waits on 09 (what a detector looks like).
- **Coach guide, checkpoint prompts and the run-of-show** — waits on 08 (duration).
- **Internal mini-hackathon**: when, with whom, and what counts as passing the release gate.
  Waits on most of the frontier.
- **Jury composition and prize structure** — waits on 12 (how agentic work scores).
- **Event taxonomy for the bespoke French-city bags** (localization, signal behaviour, state
  transition, pattern match) — waits on 14.

## Out of scope

Ruled beyond this map's destination. Does not graduate; would need a fresh effort.

- **Building the kit** — runner, CLI, dataset packaging, evaluator implementation. This map
  ends at the spec that lets five owners start.
- **`handoff-site` as a todo/done tracker**, and the auth gate for `/organizers`. Real work and
  worth doing, but it is support tooling for the effort rather than a §8 challenge decision.
  Pull it back in by redrawing the destination if you disagree.
- **Post-event deployment modes** (edge triage, OTA, fleet rollout). Teaching material inside
  the event; not something this spec has to settle.
