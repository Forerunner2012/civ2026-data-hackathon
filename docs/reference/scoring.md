# Scoring references

Practice scores are participant self-evaluation against a designated source-bound reference, not official results or access to held-out truth. `civ score` requires `civ.label-pack/v1alpha1`.

## Practice and organizer references

| Reference | Audience and requirements | Availability |
| --- | --- | --- |
| Practice pack | Participant self-evaluation with a separately supplied pack; `practice-labels/` is reserved for approved repository packs. It covers every relevant event for one designated source or chunk, starting with the Kashiwa warm-up. The `civ.label-pack/v1alpha1` pack binds `source_sha256` to `run-manifest.json` → `source.sha256` and includes `contract`, `dataset`, `source_sha256`, `labels`, and `data_gaps`. Labels use `label_id`, `start_ns`, `end_ns`; gaps use `start_ns`, `end_ns` with optional `gap_id` and `reason`. `provenance` and `scoring` are optional; partial coverage is not expressible. | Complete local practice review and consumer qualification are recorded in [issue #117](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/117). No real practice pack is tracked here. Session availability and authorized distribution remain separate. |
| Full truth | Sealed labels, provenance, review progress, and audit stay organizer-only. `score-batch` selects packs by exact source hash. Keep them out of participant kits, reports, bundles, and submissions. | Organizer workflow only, separate from practice distribution. |

When that complete practice pack is supplied, use:

```sh
civ score WORKING_DIR --labels SUPPLIED_PRACTICE_PACK.json
```

For private cohort scoring, the CLI requires an intake ledger, a directory of organizer packs, and an output directory:

```sh
uv run civ score-batch --ledger INTAKE_LEDGER --labels ORGANIZER_LABEL_PACKS/packs --output ORGANIZER_RESULTS
```

Replace the placeholders with your detected-run directory and the exact practice pack supplied for your session. Install the participant CLI through the [setup guide](../setup.md); no organizer-root install is needed. Keep source and product input directories read-only. Re-export corrections through existing contracts; `metrics.json` records `label_pack_sha256` for the exact reference bytes. Export does not authorize broader publication.

## Matching and metrics

Intervals use integer nanoseconds with half-open `[start_ns, end_ns)` bounds. Scoring removes a label or prediction only when it has positive temporal overlap with a supported data gap; touching a gap boundary does not exclude it. Candidate matches require temporal intersection-over-union (IoU) of at least `0.5`. The scorer orders candidates by descending IoU, then stable label and prediction order, and greedily assigns each label and prediction at most once. Unmatched predictions, including duplicates, are false positives; unmatched labels are false negatives. `metrics.json` reports precision, recall, F1, counts, and mean matched IoU.

For example, the synthetic `highest-iou-duplicate` fixture has one label `[0,100)` and predictions `[0,75)` and `[0,100)`: the exact match wins, leaving one true positive, one false positive, and no false negatives. Precision is `1/2`, recall `1`, and F1 is `2/3` (`0.666666666667`); see the [fixture](../../tests/fixtures/scoring/matching_and_duplicates.json) and [scoring test](../../tests/test_scoring.py).

An omitted valid event in an incomplete practice pack can count as a false positive. Treat precision, recall, and F1 as complete-reference results only after every relevant event for that source or chunk is reviewed and included. Adjustments, rejections, and genuine data-gap exclusions need reasons; uncertain intervals and missing context need a human disposition, and export requires missed-event signoff. See the [local review guide](../phase3/label-review.md).

Practice metrics are diagnostic, not final points. Private full-truth scoring supplies F1 for the approved 25-point Detection allocation (15 Kashiwa, 10 Reims) within the fixed 55 machine / 45 jury rubric; up to 20 optional bonus points and jury evidence anchors remain separate. See the [Detection allocation](../phase3/detector-calibration.md#approved-point-allocation) and [accepted jury rubric](../phase4/organizer-ops-jury-acceptance.md#draft-gate).

For the artifact versions and submission boundary, see [participant contracts](participant-contracts.md), the [practice-labels README](../../practice-labels/README.md), the [organizer label-pack contract](../phase3/organizer-label-packs.md), and the [stable contract inventory](../phase2/stable-contracts-and-compatibility.md#organizer-only-exclusions).
