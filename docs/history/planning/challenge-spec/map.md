# Map: CIV 2026 challenge spec

> Historical planning. Follow the [archive index](../README.md) for current guides and record boundaries.

Label: `wayfinder:map`

## Destination

A complete challenge spec: every decision in `HACKATHON-HANDOFF.md` §8 closed **and §5 Phase 0's
gate satisfied**, so owners can build the kit without re-litigating anything. The spec is the deliverable —
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
- **Tooling will be AI-built with human review.** Ticket 15 defines those gates.
- As decisions close, update §8 of `HACKATHON-HANDOFF.md` so the handoff and the map agree.

> **Status: reopened, destination extended.** The map closed at 19 tickets, then two answers
> widened it. Phase 0's gate turned out to carry three items the original §8 queue never listed
> (cohort, skill floor, licensing — ticket 20), and the high skill floor forced the reversal of
> ticket 14: the Reims dataset is back in the main track as a **scored** generalisation
> test. Tickets 21–25 have now closed; **all 25 tickets are resolved and the destination is reached**.

## Decisions so far

- [Which dataset carries the event?](issues/01-dataset-choice.md) — URT-Kashiwa is the hero
  dataset and the freeze depends only on it. (The Reims bags were additive-only here; ticket
  14 later brought them into the main track as a scored transfer test.)
- [Which scenario anchors the challenge?](issues/02-scenario-anchor.md) — Unprotected right
  turns (URT). Creativity is expected in *how* teams express and capture the scenario with the
  OSS toolchain, not in inventing a different event class.
- [What does the sealed ground truth score against?](issues/03-scoring-basis.md) — Sealed
  labels exist for URT only, keeping the 25-point detection category objective; other event
  types are a qualitatively judged bonus.
- [What machine must the required path run on?](issues/04-target-machine.md) — Container-first,
  BYOD only, Windows/WSL2 + Ubuntu, CPU-only. Risk accepted: setup failure has no hardware
  swap, so the non-ROS fallback pack is load-bearing.
- [Are URT-Kashiwa redistribution terms sufficient?](../../../../.scratch/civ2026-challenge-spec/issues/05-kashiwa-redistribution-rights.md)
  — **Copyright cleared: CC BY 4.0**, subsets and permanent offline attendee copies expressly
  permitted, attribution the only condition. Two catches: a delete-after-the-event clause would
  itself breach the licence, and access is not guaranteed to persist, so mirror the 16 MCAPs now.
  Personal data graduated to ticket 19, since closed.
- [Retrieve and review the previous hackathon's solution](../../../../.scratch/civ2026-challenge-spec/issues/06-retrieve-previous-solution.md)
  — logic, thresholds and workflow extracted; Heex stack and terminology left behind (07). The
  prior "unprotected right turn" detector was really *a right turn while something was detected*,
  and nothing was ever scored against ground truth, so **no historical calibration data exists**.
- [Is the agenda three hours or three and a half?](issues/08-agenda-duration.md) — **not a
  decision; fixed by the programme at three hours.** Plus a separate 14:30–15:00 results slot,
  which means pitches can leave the three-hour block entirely and teams get lunch to prepare.
- [Is the camera imagery clear to redistribute?](../../../../.scratch/civ2026-challenge-spec/issues/19-personal-data-clearance.md) — **yes.**
  T-Lab participates in the hackathon, so this is a direct collaboration with the publishing lab.
  Attribution remains the one live obligation.
- [Is the detector surface CEL-only, or CEL plus a Python API?](issues/09-detector-authoring-surface.md)
  — **EventSpec carries CEL conditions + `timing` (duration, merge gap) + `evidence` + a
  declarative `derive` stage.** `timing` is the pass mark, since ticket 18's interval labels are
  unreachable without it. Python and conflict geometry are **deferred** to the organizer demo and
  an extra track, with a reserved `detector:` seam. The enforceable line is what the runner
  executes for the scored submission, not what teams may write.
- [Where is the clean-room boundary?](issues/07-clean-room-boundary.md) — **independent functional
  reimplementation with provenance review**, drawn around the **Heex stack and its terminology**,
  not the domain logic. Never System/Datasource/Signal/Trigger/Recording; always
  bag/topic/field/EventSpec/detector/event/clip. Condition expressions and their thresholds are
  reusable — they describe the data, not the product.
- [Is PlotJuggler 4 enough?](issues/10-visualization-surface.md) — **PlotJuggler 4 required,
  Lichtblick shipped but optional.** Nothing on the required path needs 3D, but Evidence +
  Visualization is 30 points and the camera is cleared. Contingent on 17 keeping a camera stream.
- [What is the model policy?](issues/11-model-policy.md) — **no model shipped.** The core must
  work without one, CPU inference inside three hours is a trap, and a shared service breaks
  local-first. Teams may bring their own. Revisit with the extra track.
- [How does agentic work score?](issues/12-agent-scoring.md) — **bonus up to 10 points**, judged
  on a trace pointing to executed tools and evidence, never prompt style. Said plainly: with
  rung 3 deferred and no model shipped, the agent track is thin this edition — the AI story is
  carried by how the kit is built.
- [Is the CLI `cive` or `civ`?](issues/13-cli-name.md) — **`civ`**.
- [What are the review and test gates for AI-built tooling?](issues/15-ai-build-review-gates.md)
  — **gate by failure visibility × cost.** Evaluator gets golden files, a determinism check, the
  rank test and line-by-line review; runner gets behavioural tests and actionable errors; clips
  get structural assertions. Nothing ships without a test that fails when it breaks, a human
  writes the Tier A assertions, and a component missing its gate is cut rather than slipped.
- [How is the URT evaluator calibrated?](issues/16-evaluator-calibration.md) — **temporal
  IoU ≥ 0.5, one-to-one best-match, F1 across routes.** Extra overlapping predictions are false
  positives, which is what gives `merge_gap` teeth. Gaps excluded from both sets; deliberate
  quality defects scored under Quality, not Detection. Validated by ranking four deliberately
  different detectors; all values provisional until that run.
- [Zone monitoring: champagne caves by GNSS](issues/25-geofence-agent-track.md) — **the extra
  track becomes the *extension* track.** Participants acquire cave locations by any means they
  like — agent, chat assistant, OSM query, or by hand — because the lesson is that outside
  knowledge plugs in, not that AI does it. Requires an `external-resource seam` in EventSpec
  (`resources:` plus a `min_distance_to` derive op), which must land before the schema freezes.
  Judged qualitatively, not against a sealed cave list. Unifies with ticket 09's deferred rung 3:
  one extends the inputs, the other the computation. Ticket 24 confirms Reims and two clear 40 m
  zone encounters (Martel and Pommery), so this is viable as a small extension exercise.
- **MEASURED** — `mcap du` on the Reims recording shows detection signals are **1.2% of the
  bytes**: point cloud 71.5%, compressed RGB 27.3%, everything a detector reads (IMU, objects, tf,
  fix, fix_velocity) under 40 MB per 3.2 GB chunk. Signals-only for the whole 38-minute session is
  **~350 MB**. Ticket 17's 15 GB target was solving a problem that does not exist; the Reims
  dev/sealed split rests on pedagogy alone. **Kashiwa is still unmeasured.**
- [Does the Reims recording contain enough of the target manoeuvre?](../../../../.scratch/civ2026-challenge-spec/issues/24-survey-reims-bag.md)
  — **yes: 16 clear junction-left manoeuvres plus 2 development-side borderline cases.** Chunks
  `_0`–`_4` become development (~21m49s, 7 clear events); `_5`–`_8` stay sealed (~16m09s, 9 clear
  events). Objects support evidence but cannot establish right-of-way. The 13.3 km route is in
  Reims; 40 m zones produce two clear cellar encounters. GNSS jitter is sub-metre typically and
  1.32 m at the maximum observed stationary displacement; satellite count is not recorded.
- [How do 15–30 submissions get judged?](issues/21-pitch-and-judging-model.md) — **auto-score at
  12:30, jury reads capped one-page reports over lunch, results block is a reveal plus ~4
  walkthroughs including the most instructive failure.** 55 points machine-scored (detection,
  evidence, reproducibility), 45 jury-scored from the report, bonus 20 with the jury. `report.md`
  gains a fixed structure with a "what transferred and what did not" heading, which is what makes
  the transfer insight scoreable. Solo and duos rank together. Detection splits **15 Kashiwa / 10
  Reims**, provisional until the internal evaluator run shows how both sealed sets affect ranking.
- [Cohort, skill floor and "open source"](issues/20-cohort-skill-floor-licensing.md) — **30
  participants, solo or in duos**, all experienced with robotic/vehicular data. Kit ships
  permissively (MIT/Apache-2.0 code, CC BY 4.0 content) with credit suggested; workshop content
  and the site go public. Closes the Phase 0 remainder the first map missed.
- [How is the organizer view kept out of the public site?](../../../../.scratch/civ2026-challenge-spec/issues/22-public-site-organizer-gate.md)
  — **production builds contain only the participant app.** `/` and `/participants` render the
  public participant view; `/organizers` is absent from the route manifest and from both server
  and client bundles. The full organizer app remains available through local development only.
- [Do the golden-path tool licences compose cleanly?](../../../../.scratch/civ2026-challenge-spec/issues/23-tool-licence-audit.md) — **yes,
  with an artifact-level release gate.** Standardize on ROS 2 Humble / Ubuntu 22.04; pin the base
  image by digest; treat PlotJuggler and Lichtblick as MPL-2.0 standalone programs with matching
  source availability; pin custom schemas by commit plus MCAP schema hash; and generate the SBOM,
  third-party notices and copyleft source/relinking paths from the built image. CIV code remains
  MIT/Apache and data/content remain CC BY 4.0, but the aggregate image has no single licence.
- [What do the bespoke Reims bags add?](../../../../.scratch/civ2026-challenge-spec/issues/14-bespoke-collection-scope.md) —
  **REVERSED. In the main track, scored as a sealed generalisation test.** With 30 practitioners
  the Kashiwa core is a warm-up, so the difficulty moves to transfer: manual analysis, then `civ`
  as facilitator, then the same reasoning applied to a structurally different dataset.
- [The event, defined semantically](../../../../.scratch/civ2026-challenge-spec/issues/18-urt-operational-definition.md) — **the turn that
  crosses oncoming traffic.** Right turns in Kashiwa, **left** turns in France, because handedness
  is a property of the country and not of the detector. Converts transfer from a topic remap into
  a comprehension test: copy a threshold and you find nothing.
- [How does 112 GB reach BYOD laptops?](issues/17-dataset-subsetting-and-distribution.md) —
  **1 warm-up + 7 dev routes distributed, 8 sealed**, drop point clouds and the map, keep scalars
  at full rate. Pre-event download with checksums, USB fallback. Superseded in part by the
  measurement above: the ≤ 15 GB target was never the binding constraint, and the split now rests
  on pedagogy rather than bytes.

## Not yet specified

Fog — in scope, not yet sharp enough to ticket. Graduates as the frontier advances.

- **The extra track and the organizer demo** — Python detectors and conflict geometry (rung 3 of
  [ticket 09](issues/09-detector-authoring-surface.md)). Sharp enough to describe, deliberately
  **not** ticketed: it is gated on the main track being complete and rehearsable, and designing
  it earlier would pull effort away from the path every team has to walk. EventSpec reserves a
  `detector:` seam for it.

- **Labelling workflow for the sealed URT set** — who labels, in what tool, to what
  inter-annotator agreement. Definition and tolerance are closed; tool, ownership and agreement
  targets are execution details for Phase 3.
- **Minute-level cadence inside the three hours** — the handoff now carries a rehearsal baseline:
  Kashiwa through 01:30, Reims transfer through 02:45, then submit. Internal evaluation may move
  checkpoint minutes without reopening the two-dataset order or the 12:30 deadline.
- **Warm-up design and the non-ROS fallback pack contents** — load-bearing because of the BYOD
  decision in 04. Waits on 09 (what a detector looks like) and 17 (what data a team holds).
- **Coach guide and checkpoint prompts** — tune against the rehearsal baseline and actual
  solo/duo pacing.
- **Internal mini-hackathon**: with whom, and what counts as passing the release gate. This is
  where the evaluator and two-dataset ranking get validated; scheduling and participant selection
  are execution work.
- **Jury composition and prize structure** — waits on 12 (how agentic work scores).
- **Pre-event setup session** for the BYOD environment risk in 04. The programme has no slot, so
  it would be remote and voluntary in the week before.
- **Publication choice for the organizer-authored sealed labels** — the toolchain obligations are
  closed in ticket 23; whether the label set itself is published after the event remains an event
  policy choice, not a software-licence uncertainty.

## Out of scope

Ruled beyond this map's destination. Does not graduate; would need a fresh effort.

- **Building the kit** — runner, CLI, dataset packaging, evaluator implementation. This map
  ends at the spec that lets five owners start.

- **Post-event deployment modes** (edge triage, OTA, fleet rollout). Teaching material inside
  the event; not something this spec has to settle.
