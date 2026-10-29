# Phase 4 extension track acceptance

Status: **accepted with a scope reduction — one exemplar, not two**

Recorded: 2026-08-29

This gate packages the optional extension branch: an executable external-input exemplar on the
stable `resources:` / `min_distance_to` seam, a bounded participant task, provenance guidance, and
the page section that offers it without scheduling it. It does not qualify a release candidate.

## The scope reduction, and why

Ticket 25 framed the track as *one track, two exemplars* — "one extends the **computation**, the
other extends the **inputs**". The computation exemplar was always the reserved `detector:` field
carrying Python and conflict geometry. Phase 4 may not activate it:

- issue #44 requires the second example to execute "without activating the reserved `detector:`
  field or changing any stable `v1` contract";
- `tests/test_eventspec_resources.py::test_detector_field_is_reserved_with_a_correction` proves the
  runner refuses `detector:` today, with a correction;
- the only other computation surface is `derive`, whose operation set is closed to `ewma`,
  `magnitude` and `min_distance_to` (`src/civ_workshop/event_spec.py:115`). All three are
  main-track "reach" tooling under ticket 09, and adding a fourth changes a frozen `v1` contract,
  which map #37 puts out of scope for this phase.

No honest second axis therefore exists on the stable seams. Issue #44's third criterion governs
this case: the ticket stops for an explicit human scope decision and may not publish a fictional or
non-executable path to satisfy the old two-example wording. **The organizer decision on 2026-08-29
was to ship the one real exemplar and supersede the two-example phrasing.** The computation exemplar
returns if and when `detector:` is unreserved, which is a contract decision for a later phase.

## The exemplar is real, and reaches the participant data

The worked spec is the already-tracked `examples/reims/cave-encounter.yaml` with its
`civ.point-resource/v1` seed file. Its shipped points are deliberately illustrative: sourcing real
ones is the exercise.

The design risk this gate had to close was whether the encounters are reachable at all from the
**development** products. Ticket 24 measured its nearest approaches against the full 13.3 km route,
and the development subset is not the whole route — the latitude strip 49.23444–49.24002 exists only
in the held-back chunks, and that strip is the cellar district. Measured directly from `/fix` across
both product sets:

| Cellar | Nearest approach, development set | Nearest approach, held-back set | Development chunk |
| --- | ---: | ---: | --- |
| G.H. Martel | 15.6 m | 120.5 m | chunk 4 |
| Pommery | 35.4 m | 220.0 m | chunk 2 |

Both encounters land in the development set, on two different chunks, and **neither is in the
held-back set** — so the task is fully doable on the products a participant keeps, and the held-back
data carries no part of the answer. The two development figures reproduce ticket 24's full-route
measurements (15.6 m and 35.7 m) to within geocoding precision, which cross-validates both the
survey and this one. Ruinart, at 65.4 m on the full route, stays outside, so the published 40 m
radius genuinely discriminates.

Cellar coordinates are not recorded here. They are reproducible from the published addresses by
ticket 24's method, and writing them into a tracked file would hand over the exercise.

## Executed evidence

Running the tracked spec with a real two-point resource across all five Reims development products:

| Chunk | Events | Duration |
| --- | ---: | ---: |
| 0, 1, 3 | 0 | — |
| 2 | 1 | 4.00 s |
| 4 | 1 | 9.25 s |

Exactly the two encounters ticket 24 predicted, and nothing else. The full five-chunk sweep took
**4.7 s** wall time; the tracked illustrative spec runs against one real product in **0.93 s** and
correctly emits nothing. Detection is therefore free, and the published 30–45 minute budget is
almost entirely acquisition — which is the lesson rather than a cost.

Products used were the accepted set at manifest SHA-256
`d515c0a7cd748f8b2ad0cb41b93d8847b0917c2e6469be2f8be09582fc62ef9b`, verified before use. No product
byte, resource file, or run output from this gate enters git.

## The page section

`/participants` gains section 06, which states the lesson, that the branch is open and scored before
12:30, that it receives no time in the run of show, and that it stays available afterwards on the
same products. It carries the task, the provenance rule that method is unconstrained, and the note
that no model is required and nothing on the required path needs the network.

The section names no coordinate, no cellar, and no chunk, and `rendered-html.test.mjs` asserts all
three absences by pattern rather than by review. The leakage suite also caught the first draft of
this copy for using the word *organizer*; the published wording uses answer key and held-back list
instead, per map #37's public-teaching-copy rule.

## Evidence

- `npm test` in `handoff-site` — internal build with a configured form, internal build without one,
  then the public build; 13 rendered-HTML and print tests plus 6 live tests pass, including the new
  `optional extension is offered, scored, and never scheduled`;
- `npm run lint`, `uv run pytest`, `uv run ruff check .`, `uv run mypy src tests`, `git diff --check`
  — all clean.

## Routed to Phase 5

- The extension section's wording needs the same human approval as the rest of the participant copy.
- Offline behaviour of the branch was exercised only in the sense that `civ detect` needs no network;
  the acquisition step is by design online, and the rehearsal should confirm that a participant who
  starts it after an internet loss is not left mid-task.
- If `detector:` is ever unreserved, the computation exemplar this gate cut becomes available again
  and this record is the place that says why it was missing.
