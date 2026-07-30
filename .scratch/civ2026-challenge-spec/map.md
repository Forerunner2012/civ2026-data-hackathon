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
- **Event facts** (verified against the published programme): CIV 2026 runs 31 Aug – 4 Sep 2026
  in **Miyazaki, Japan**; the **hackathon is Thu 3 Sep, 09:30–12:30**, with a separate results
  slot at **14:30–15:00** ([ticket 08](issues/08-agenda-duration.md)). These are design inputs —
  the three-hour ladder and the fact that pitches have their own slot — not a countdown.
- **Schedule is not a constraint on this map.** Decide what the event *should* be; the build
  follows. Do not water down a decision to fit a calendar, and do not carry delay caveats into
  tickets.
- **Main track first, ceiling second.** Where a decision has an advanced tier, specify the main
  track now and **defer the ceiling to the organizer demo and an extra track**, to be designed
  once the main track is complete and rehearsable. Leave a named seam rather than an
  implementation. Established in [ticket 09](issues/09-detector-authoring-surface.md).
- Data collection and rights are settled, so the substance lives in **definition, evaluation and
  rehearsal** — the parts that need real runs and real judgement rather than more code.
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
- [Are URT-Kashiwa redistribution terms sufficient?](issues/05-kashiwa-redistribution-rights.md)
  — **Copyright cleared: CC BY 4.0**, subsets and permanent offline attendee copies expressly
  permitted, attribution the only condition. Two catches: a delete-after-the-event clause would
  itself breach the licence, and access is not guaranteed to persist, so mirror the 16 MCAPs now.
  **Personal data is not cleared** — graduated to ticket 19.
- [Retrieve and review the previous hackathon's solution](issues/06-retrieve-previous-solution.md)
  — logic and workflow extracted, tool usage and tuned thresholds deliberately left behind. The
  prior "unprotected right turn" detector was really *a right turn while something was detected*,
  and nothing was ever scored against ground truth, so **no historical calibration data exists**.
- [Is the agenda three hours or three and a half?](issues/08-agenda-duration.md) — **not a
  decision; fixed by the programme at three hours.** Plus a separate 14:30–15:00 results slot,
  which means pitches can leave the three-hour block entirely and teams get lunch to prepare.
- [Is the camera imagery clear to redistribute?](issues/19-personal-data-clearance.md) — **yes.**
  T-Lab participates in the hackathon, so this is a direct collaboration with the publishing lab.
  Attribution remains the one live obligation.
- [What is an "unprotected right turn", operationally?](issues/18-urt-operational-definition.md)
  — **the sealed labels mark the right-turn manoeuvre interval**; "unprotected" is scenario
  context the brief supplies, not something the detector proves. Cheap to label with high
  agreement. Cost, accepted: detection no longer separates teams on cleverness, so separation
  moves to interval precision, robustness across all 16 routes, duplicate handling, and the other
  75 points. Conflict geometry moves to the bonus track.
- [Is the detector surface CEL-only, or CEL plus a Python API?](issues/09-detector-authoring-surface.md)
  — **EventSpec carries CEL conditions + `timing` (duration, merge gap) + `evidence` + a
  declarative `derive` stage.** `timing` is the pass mark, since ticket 18's interval labels are
  unreachable without it. Python and conflict geometry are **deferred** to the organizer demo and
  an extra track, with a reserved `detector:` seam. The enforceable line is what the runner
  executes for the scored submission, not what teams may write.

## Not yet specified

Fog — in scope, not yet sharp enough to ticket. Graduates as the frontier advances.

- **The extra track and the organizer demo** — Python detectors and conflict geometry (rung 3 of
  [ticket 09](issues/09-detector-authoring-surface.md)). Sharp enough to describe, deliberately
  **not** ticketed: it is gated on the main track being complete and rehearsable, and designing
  it earlier would pull effort away from the path every team has to walk. EventSpec reserves a
  `detector:` seam for it.

- **Labelling workflow for the sealed URT set** — who labels, in what tool, to what
  inter-annotator agreement. Now waits on 18 (the definition) and 16 (tolerance semantics).
- **Rebuilding the run-of-show around the real slots** — 09:30–12:30 produces a submission,
  14:30–15:00 presents it, with a two-hour lunch in between to prepare. §4.2's 15-minute Transfer
  block inside the three hours is now the wrong shape. Sharp enough to ticket once 18 lands and
  the first-30-minutes design is known.
- **Warm-up design and the non-ROS fallback pack contents** — load-bearing because of the BYOD
  decision in 04. Waits on 09 (what a detector looks like) and 17 (what data a team holds).
- **Coach guide and checkpoint prompts** — waits on the run-of-show above.
- **Internal mini-hackathon**: with whom, and what counts as passing the release gate. This is
  where the evaluator gets validated, so it graduates once 16 and 18 land.
- **Jury composition and prize structure** — waits on 12 (how agentic work scores).
- **Pre-event setup session** for the BYOD environment risk in 04. The programme has no slot, so
  it would be remote and voluntary in the week before.
- **Attribution and licensing surface of the shipped kit** — the `NOTICE` file, the CLI's
  `--about`, and whether the organizer-authored label set is published CC BY 4.0 to sidestep the
  one grey area in 05.

## Out of scope

Ruled beyond this map's destination. Does not graduate; would need a fresh effort.

- **Building the kit** — runner, CLI, dataset packaging, evaluator implementation. This map
  ends at the spec that lets five owners start.
- **`handoff-site` as a todo/done tracker**, and the auth gate for `/organizers`. Real work and
  worth doing, but it is support tooling for the effort rather than a §8 challenge decision.
  Pull it back in by redrawing the destination if you disagree.
- **Post-event deployment modes** (edge triage, OTA, fleet rollout). Teaching material inside
  the event; not something this spec has to settle.
