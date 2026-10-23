# Scoring references

Practice scores are participant self-evaluation against a designated source-bound reference, not official results or access to held-out truth. `civ score` requires `civ.label-pack/v1alpha1`.

## Practice and organizer references

| Reference | Audience and requirements | Availability |
| --- | --- | --- |
| Practice pack | Participant self-evaluation with a separately supplied pack; `practice-labels/` is reserved for approved repository packs. It covers every relevant event for one designated source or chunk, starting with the Kashiwa warm-up. The `civ.label-pack/v1alpha1` pack binds `source_sha256` to `run-manifest.json` → `source.sha256` and includes `contract`, `dataset`, `source_sha256`, `labels`, and `data_gaps`. Labels use `label_id`, `start_ns`, `end_ns`; gaps use `start_ns`, `end_ns` with optional `gap_id` and `reason`. `provenance` and `scoring` are optional; partial coverage is not expressible. | Complete local practice review and consumer qualification are recorded in [issue #117](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/117). No real practice pack is tracked here. Session availability and authorized distribution remain separate. |
| Full truth | Labels, provenance, review progress, and audit stay organizer-only. Cohort scoring binds truth by track and exact product. Keep full truth out of participant kits, reports, bundles, submissions, and public results. | Organizer workflow only, separate from practice distribution. |

When that complete practice pack is supplied, use:

```sh
civ score WORKING_DIR --labels SUPPLIED_PRACTICE_PACK.json
```

For participant practice, pass the detected-run directory and the exact practice pack supplied for the session. Keep source and product input directories read-only. Re-export corrections through existing contracts. `metrics.json` records `label_pack_sha256` for the exact reference bytes. Export does not authorize broader publication.

For track-aware cohort scoring, use [`civ.evaluation-plan/v1alpha2`](../organizers/cohort-scoring.md). That path selects a track-specific receipt and replays the submitted EventSpec and resources over every assigned product. It scores organizer replay events against truth keyed by track and exact product. It does not use participant-submitted events or metrics as predictions.

## Matching and metrics

Intervals use integer nanoseconds with half-open `[start_ns, end_ns)` bounds. Scoring removes a label or prediction only when it has positive temporal overlap with a supported data gap; touching a gap boundary does not exclude it. Candidate matches require temporal intersection-over-union (IoU) of at least `0.5`. The scorer orders candidates by descending IoU, then stable label and prediction order, and greedily assigns each label and prediction at most once. Unmatched predictions, including duplicates, are false positives; unmatched labels are false negatives. `metrics.json` reports precision, recall, F1, counts, and mean matched IoU.

For example, the synthetic `highest-iou-duplicate` fixture has one label `[0,100)` and predictions `[0,75)` and `[0,100)`: the exact match wins, leaving one true positive, one false positive, and no false negatives. Precision is `1/2`, recall `1`, and F1 is `2/3` (`0.666666666667`); see the [fixture](../../tests/fixtures/scoring/matching_and_duplicates.json) and [scoring test](../../tests/test_scoring.py).

An omitted valid event in an incomplete practice pack can count as a false positive. Treat precision, recall, and F1 as complete-reference results only after every relevant event for that source or chunk is reviewed and included. Adjustments, rejections, and genuine data-gap exclusions need reasons; uncertain intervals and missing context need a human disposition, and export requires missed-event signoff. See the [local review guide](../phase3/label-review.md).

The existing participant rubric uses the fixed 55 machine / 45 jury rubric; up to 20 optional bonus points remain separate. See the [Detection allocation](../phase3/detector-calibration.md#approved-point-allocation) and [accepted jury rubric](../phase4/organizer-ops-jury-acceptance.md#draft-gate). The cohort runner's implementation limits are listed below.

## Cohort aggregation

`summary.json` → `detection_metrics.participants` contains metrics by track and partition. The track aggregate includes all assigned partitions. Counts pool TP, FP, and FN across successful products, then calculate precision, recall, and F1. This calculation does not average product F1 or apply point weights.

Each group reports `complete`, `partial`, or `unavailable` alongside its outcomes. Missing and failed products contribute no invented counts. Ratios with a zero denominator are `null`, including F1 when both predictions and truth are empty. A successful zero-event replay still has `status: "scored"`.

## Detection points

The optional plan `scoring_policy` controls points. Diagnostic replay and pooled metrics work without it. Points require explicit product weights, score-bearing partitions, missing-track and failed-run handling, empty-truth handling, receipt timestamp ties, rounding, and track Detection allocations.

The implemented matching settings are `temporal_iou_threshold: 0.5`, `matching: "one_to_one_best"`, and `cross_product_events: "score_within_product"`. See the [plan schema](../../schemas/civ.evaluation-plan.v1alpha2.schema.json) for policy fields.

For each track, the runner weights product F1 across the declared score-bearing products and applies the track's Detection allocation. It calculates the weighted mean before rounding. It rounds displayed F1 and Detection points separately, then sums rounded track allocations for the participant total.

The existing rubric allocates 15 Detection points to Kashiwa RT and 10 to Reims turns. Cave has no assigned allocation. The runner does not infer Cave points or which partitions count toward points. Omitting Cave from `detection_points` leaves Cave points pending. Its `product_weights` entry can also be omitted while undecided. Configured turn tracks can still calculate points, but the combined Detection total remains `null` until every assigned track has a result.

## Current limits

Evidence and Reproducibility have no implemented deterministic point mapping. Their points and the technical total remain `null`. The technical maximum is also `null` when a track allocation is missing. Jury and bonus decisions remain separate.

All cohort outputs have `official_score: false`. `score-batch --official` rejects cohort scoring while machine policies remain incomplete. A complete replay does not establish an official score or authorize publication.

For the artifact versions and submission boundary, see [participant contracts](participant-contracts.md), the [practice-labels README](../../practice-labels/README.md), the [organizer label-pack contract](../phase3/organizer-label-packs.md), and the [stable contract inventory](../phase2/stable-contracts-and-compatibility.md#organizer-only-exclusions).
