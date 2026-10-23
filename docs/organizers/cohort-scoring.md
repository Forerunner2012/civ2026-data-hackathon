# Score a full cohort

Use `civ.evaluation-plan/v1alpha2` to replay every selected track submission against each product assigned to that track. The plan binds the participant cutoff, product and manifest hashes, topic and schema contracts, organizer truth, and scoring decisions. See the [plan schema](../../schemas/civ.evaluation-plan.v1alpha2.schema.json).

The plan's `participants` list is the organizer's complete registered-team roster. Include every team, including teams that submitted no tracks. The scorer emits `missing-track` outcomes for rostered teams without an eligible delivery. Receipts for unregistered identities, receipts without a track ID, and receipts with unknown track IDs remain visible with delivery IDs and reconciliation dispositions in `summary.json`.

`score-batch` keeps the `v1alpha1` diagnostic path for older two-dataset ledgers. For a `v1alpha2` plan, `--labels` is not used because each track and product names its own organizer truth pack.

## Record track-specific deliveries

Use one stable track ID for each submission. For a local delivery, run:

```sh
uv run civ intake-local SUBMISSION.zip --ledger INTAKE_LEDGER \
  --identity TEAM_ID --track-id TRACK_ID --received-at ISO8601_TIMESTAMP \
  --sha256 BUNDLE_SHA256 --delivery-id DELIVERY_ID
```

The `intake-form` response can include a `track_id` field. Tally CSV exports can add a `Track ID` column before `Your submission.zip`. The importer accepts both the original and track-aware header sets.

The ledger keeps every valid receipt. `score-batch` selects the latest receipt on or before the plan cutoff for each identity and track. When timestamps tie, the plan must choose either `earlier_ledger_sequence` or `later_ledger_sequence`. This sequence is the receipt order in the immutable ledger snapshot. A failed selected delivery stays failed. The scorer never substitutes an older delivery.

The receipt `status` field still reflects the historical intake cutoff. Cohort selection uses the cutoff in the `v1alpha2` plan.

## Use the pinned environment

Run `uv sync --locked` in the organizer checkout before scoring. Run scoring with
`uv run --locked civ score-batch` to use that environment.
Remove the `runtime` object from earlier `v1alpha2` plans. The runner records runtime
metadata in the summary instead of requiring hashes in the plan.

The summary records the code revision, whether tracked runtime files have local changes,
the tool and Python versions, and the `uv.lock` hash. Git or lock metadata is `null` when
unavailable. These values describe the run; they do not prove that an environment was synced.
The runner does not hash Python executables or installed dependency files.

## Bind products and replay inputs

Create one track entry for each target. Add every assigned warm-up, development, and sealed product. A product reference contains paths and SHA-256 values for the MCAP, its `civ.data-product-manifest/v1`, and its `civ.label-pack/v1alpha1` truth pack.

Set `partition` to `warmup`, `development`, or `sealed`. Set `dataset` to the source family. Use a distinct `product_id` within each track. The same product can appear on two tracks with different truth packs.

Each product's `input_contract` names its configured topics and exact schema identities. Schema records use `topic`, `schema_name`, `schema_encoding`, `schema_sha256`, and `message_encoding`. The scorer checks the plan against the product manifest and the MCAP itself.

Each track's `replay` record sets accepted EventSpec contracts, allowed signal topics, resource file and byte limits, a timeout, and a retry count. The timeout applies to each trusted replay attempt. `retries` counts attempts after the first. The scorer validates the ZIP, loads only `detector/detector.yaml` and its declared resources, then invokes `civ detect` on every assigned product. It does not run the submitted reproduction script or use submitted `events.jsonl` and `metrics.json` as predictions.

The evaluator writes one result for every identity, track, and assigned product. A successful replay with zero events has `status: "scored"` and `replay.zero_events: true`. Invalid submissions, products, or replay runs have an explicit failure result. Results and replay events belong in organizer-controlled storage.

## Declare scoring decisions

Add `scoring_policy` to the plan before assigning points. The scorer keeps the existing temporal IoU threshold of `0.5` and one-to-one best matching. Points require explicit product weights, score-bearing partitions, handling for missing tracks, failed runs, and empty truth, a rule for receipt timestamp ties, cross-product handling, rounding, and a Detection allocation for the track.

Set the Detection allocation for the Cave track explicitly. The existing rubric assigns 15 points to Kashiwa RT and 10 to Reims turns. It does not assign Cave Detection points. The scorer does not infer that allocation.

To leave Cave points pending, omit the Cave entry from `detection_points`. You can also omit
its `product_weights` entry while those weights are undecided. Configured turn tracks still
calculate points. The Cave track reports `detection_points: null` and a `pending_reason`.
The participant Detection total remains `null` until every assigned track has a point result.
The technical maximum is also `null` when any track allocation is missing.

`score-batch` calculates participant Detection points when the plan supplies those decisions. For each participant and track, it computes product F1 from the exact TP, FP, and FN counts, applies the declared product weights to the included products, and uses that unrounded weighted mean for the Detection allocation. It rounds the displayed F1 and Detection points separately with the declared rounding mode and precision; the participant total is the sum of the rounded track allocations, rounded at the same precision.

Evidence and Reproducibility are machine-scored categories worth 15 points each under issue #168. That issue does not define the eligible validated artifacts, deterministic criteria, point mappings, or outcomes for missing and invalid inputs. No approved deterministic mapping exists in the current rubric or implementation, so both components remain pending: `score-batch` reports their points and the technical total as `null`. Do not execute submitted reproduction scripts. Jury and bonus decisions remain separate from these machine calculations.

## Read detection metrics before assigning points

Use `summary.json` → `detection_metrics.participants` to compare replay outcomes without
a points policy. Each participant has metrics by track, with separate partition summaries.
The track aggregate includes all assigned partitions. Each product's original metrics remain
in `results.jsonl`.

The summary adds TP, FP, and FN counts across successful products, then calculates precision,
recall, and F1 from those pooled counts. It does not average product F1 values or apply point
weights. These diagnostic metrics do not choose which partitions count toward points.

Check `outcomes` and `status` alongside each metric. `complete` means all products in that
group were scored. `partial` means some products failed or had no eligible submission.
`unavailable` means none were scored, and the counts and ratios are `null`. Missing and failed
products do not contribute invented event counts. Ratios with a zero denominator are `null`,
including F1 for a successful replay with both zero predictions and zero truth events.
Any empty-truth point award still follows the plan's explicit `empty_truth` rule.

## Run the cohort comparison

Close intake writers before scoring. Read-only scoring rejects a ledger with a WAL sidecar.
Run the batch with the plan, ledger, and private output directory:

```sh
uv run --locked civ score-batch --ledger INTAKE_LEDGER --plan EVALUATION_PLAN.json \
  --output ORGANIZER_RESULTS
```

The command writes `results.jsonl`, `summary.json`, and organizer-only replay artifacts
under `replays/`. It requires no separate preflight, rehearsal, review-status, or computation
approval records. Existing label-review signoffs remain part of reference preparation.
Legacy readiness flags are rejected for cohort batches so stale approval records cannot
appear to control a run.

The runner freezes receipt selection at the start. Before publishing, it checks that the
plan, ledger, selected submission inputs, products, and references still match.
If those inputs changed during replay, it discards staged output and preserves previous results.

Each replay reports its attempts; failures include a failure stage. The summary records
input diagnostics, pending scoring decisions, and any computed Detection points.
Pending Evidence and Reproducibility policies do not block replay or reference comparison.
The optional `score-readiness --ledger INTAKE_LEDGER --plan EVALUATION_PLAN.json` command
reports input and scoring-policy problems without writing files. A batch runs its own checks.

Cohort outputs have `official_score: false`. `--official` rejects cohort scoring before
writing output while machine scoring policies remain incomplete. Publication remains a
separate organizer decision.

## Keep unresolved reference work open

The historical selected label-pack set remains unchanged and contains left-turn-only Reims references. A separately audited both-direction candidate binds compatible Reims references to the four assigned R&LT products and covers the proposed right-or-left target. Recommend that candidate for a private R&LT plan entry; its validation does not authorize replacing the selected set or changing the official evaluation plan. No additional label review is needed for the candidate's product or target compatibility. An organizer must still authorize its selection into an official plan.

All three tracks use reviewed, source-bound `civ.label-pack/v1alpha1` references. Cave
EventSpecs and private locations propose intervals for the existing label-review workflow;
their detected events do not become scoring truth automatically. Review candidates with
GNSS and camera context, resolve missed events, and sign off completeness before export.

For reviewed development recordings, append `--export-reference PRIVATE_REFERENCE.json`
to the same bound `civ labels review` command. This exports all approved intervals, including
a valid empty pack when the completed review found no events. For sealed recordings, build
the packs from the existing reviewed source-relative truth with `civ_workshop.label_packs`.
See [reviewed reference export](../phase3/label-review.md#export-a-reviewed-organizer-reference).
The scorer consumes these packs through the same track/product mapping used for turn truth;
it does not generate Cave references during scoring.

The current track-aware scorer can bind distinct references for Kashiwa RT, Reims R&LT, and Cave on the same product. Prepare proposed entries with exact product and reference hashes, while keeping them separate by track. Cave's Detection allocation and eligibility of public products for scoring remain pending organizer decisions. Do not take points from Reims turns or infer either decision from generated references. Keep the roster, receipt dispositions, and explicit missing-track outcomes supplied by the cohort workflow.

Keep Cave locations, event times, truth intervals, sealed replay events, generated references, and organizer paths out of participant materials. Participant instructions may describe the `/fix` GNSS, point-distance, threshold, and event-timing method without disclosing private locations or occurrence times.

Use the [organizer label-pack guide](../phase3/organizer-label-packs.md) to verify product-bound truth. Use the [scoring reference](../reference/scoring.md) for matching and the [readiness guide](scoring-readiness.md) for the legacy `v1alpha1` diagnostic path.
