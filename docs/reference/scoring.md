# Scoring references

Practice scores are participant self-evaluation against a designated source-bound reference. A supplied reference must use `civ.label-pack/v1alpha1`. Without a reference, `civ score WORKING_DIR` records `not_evaluated` metrics and permits packaging. Precision, recall, F1, counts, and reference identity are `null`, not zero. This does not evaluate the detector.

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

## Point allocation

| Component | Maximum points | Evaluation |
| --- | ---: | --- |
| Detection | 25 | Automatic: Kashiwa RT 15, Reims R&LT 10 |
| Evidence | 15 | Organizer or agent review |
| Reproducibility | 15 | Organizer or agent review |
| Jury | 45 | Investigation, Quality, and Visualization, 15 each |
| Existing bonus | 20 | Agent trace 10, advanced method 5, regression test 5 |
| Cave bonus | 10 | Automatic: weighted recording F1 multiplied by 10 |

The base remains 100 points. Bonuses add up to 30, for a maximum of 130. Cave is separate from the 25 Detection points and needs no manual or Evidence award. Its detector and participant-sourced locations are replayed on the same Reims recordings as the turn track. It uses the same interval matcher, duplicate handling, and F1 calculation. Organizers retain all truth locations and intervals privately.

### Manual technical criteria

Evidence and Reproducibility retain 15 points each. An organizer or agent studies the accepted artifacts and records a score, reason, and artifact references for each subcriterion. Each subcriterion has a maximum of five points. Use 0 for absent or contradictory support, 1–2 for incomplete support, 3–4 for supported work with material limitations, and 5 for complete, inspectable support. Do not award points for claims alone.

| Criterion | Subcriterion, five points each | What to inspect |
| --- | --- | --- |
| Evidence | Relevant synchronized topics | Events, declared evidence topics, signal units, and the submitted figure support the stated event. |
| Evidence | Bounded windows and event coverage | Clip facts in the manifest show useful context and bounded windows. Explain zero-event runs and any missing or invalid evidence. |
| Evidence | Measured extraction and limitations | Manifest byte counts support the claimed reduction; the report explains lost context, ambiguity, and limitations. Smaller output alone earns no points. |
| Reproducibility | One documented reproduction command | The supplied script and instructions reproduce the declared workflow. The scorer never executes submitted scripts. |
| Reproducibility | Exact inputs, resources, and environment | Recording, EventSpec, resource, and manifest identities are consistent; required tools and versions are recorded. |
| Reproducibility | Repeatable outputs and explained differences | Repeated trusted runs produce matching events and metrics, or the reviewer identifies and explains a material difference. |

The batch emits a private `manual-review-template.json` worksheet with these criteria and unawarded scores. Copy it to a separate review file before filling it in; rerunning scoring replaces generated templates. Generating it creates no review or approval. Jury and the existing bonus awards remain separate. Complete the final total after those reviews.

## Cohort aggregation

`summary.json` → `detection_metrics.participants` contains metrics by track and partition. The track aggregate includes all assigned partitions. Counts pool TP, FP, and FN across successful products, then calculate precision, recall, and F1. This calculation does not average product F1 or apply point weights.

Each group reports `complete`, `partial`, or `unavailable` alongside its outcomes. Missing and failed products contribute no invented counts. Ratios with a zero denominator are `null`, including F1 when both predictions and truth are empty. A successful zero-event replay still has `status: "scored"`.

## Detection points

The optional plan `scoring_policy` controls points. Diagnostic replay and pooled metrics work without it. `detection_points` and `bonus_points` assign tracks to separate totals, with each track in exactly one allocation. Set `manual_review` to `organizer_or_agent` for the manual technical categories.

The implemented matching settings are `temporal_iou_threshold: 0.5`, `matching: "one_to_one_best"`, and `cross_product_events: "score_within_product"`. See the [plan schema](../../schemas/civ.evaluation-plan.v1alpha2.schema.json) for policy fields.

For each track, the runner calculates F1 from each recording's event counts, takes the weighted mean, and applies that track's allocation. It retains precision through the calculation. Displayed F1 is informational; points never use rounded F1. With two-decimal `half_up` rounding, round each track's points and then add those displayed points. Pooled precision, recall, and F1 remain separate diagnostics and do not determine points.

### Event policy

- All assigned warm-up, development, and sealed recordings earn points.
- Give recordings equal weight within each turn track. Review durations and reference event counts before reusing this choice with a different product set; these indicators do not establish equal difficulty.
- For Cave, empty recordings collectively receive at most 10% of its weight. Split the remaining weight equally across nonempty recordings and the empty share equally across empty recordings. Never choose weights from participant predictions. If all assigned recordings are empty, revise the product selection before scoring.
- A missing track earns zero. A submission-caused failure earns zero for the affected recording; it never selects an older delivery instead.
- Organizer input, equipment, or software failures leave the affected track pending. Repair the cause and rerun; never charge those failures to participants. Unexpected replay crashes need organizer investigation. A declared replay timeout is a submission limit unless organizer investigation establishes an equipment failure.
- Empty truth earns full recording credit when predictions are also empty, and zero when any prediction remains after gap exclusions.
- Calculate a weighted mean of recording F1, round track points to two decimal places with `half_up`, then sum rounded track points.
- Equal receipt timestamps select `later_ledger_sequence`.

The [example plan](../organizers/examples/cohort-plan.example.json) shows this policy with placeholder products. Replace its paths, hashes, products, roster, cutoff, and weights with the actual session inputs. Keep duration, event-count, and empty-share checks private.

## Official automatic components and final review

`score-batch --official` requires a complete automatic scoring policy and valid organizer inputs. It refuses publication of its outputs if an organizer failure or unresolved allocation remains. A zero for an invalid participant submission is a scored policy outcome, not an organizer failure.

For this mode, `official_score: true` has `official_scope: "automatic_components"`: it covers Detection and the Cave bonus. Evidence, Reproducibility, jury, and other bonus awards are completed outside the scoring engine. The technical and final totals remain `null` and `final_score_status` remains `pending_manual_review`. Without `--official`, outputs remain diagnostic. Neither mode authorizes participant-facing publication.

For the artifact versions and submission boundary, see [participant contracts](participant-contracts.md), the [practice-labels README](../../practice-labels/README.md), the [organizer label-pack contract](../phase3/organizer-label-packs.md), and the [stable contract inventory](participant-contracts.md#producer-and-consumer-responsibilities).
