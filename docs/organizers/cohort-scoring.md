# Score a full cohort

Use `civ.evaluation-plan/v1alpha2` to replay every selected track submission against each product assigned to that track. The plan binds the participant cutoff, replay runtime, product and manifest hashes, topic and schema contracts, organizer truth, and scoring decisions. See the [plan schema](../../schemas/civ.evaluation-plan.v1alpha2.schema.json).

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

## Bind products and replay inputs

Create one track entry for each target. Add every assigned warm-up, development, and sealed product. A product reference contains paths and SHA-256 values for the MCAP, its `civ.data-product-manifest/v1`, and its `civ.label-pack/v1alpha1` truth pack.

Set `partition` to `warmup`, `development`, or `sealed`. Set `dataset` to the source family. Use a distinct `product_id` within each track. The same product can appear on two tracks with different truth packs.

Each product's `input_contract` names its configured topics and exact schema identities. Schema records use `topic`, `schema_name`, `schema_encoding`, `schema_sha256`, and `message_encoding`. The scorer checks the plan against the product manifest and the MCAP itself.

Each track's `replay` record sets accepted EventSpec contracts, allowed signal topics, resource file and byte limits, a timeout, and a retry count. The timeout applies to each trusted replay attempt. `retries` counts attempts after the first. The scorer validates the ZIP, loads only `detector/detector.yaml` and its declared resources, then invokes `civ detect` on every assigned product. It does not run the submitted reproduction script or use submitted `events.jsonl` and `metrics.json` as predictions.

The evaluator writes one result for every identity, track, and assigned product. A successful replay with zero events has `status: "scored"` and `replay.zero_events: true`. Invalid submissions, products, or replay runs have an explicit failure result. Results and replay events belong in organizer-controlled storage.

## Declare scoring decisions

Add `scoring_policy` to the plan before assigning points. The scorer keeps the existing temporal IoU threshold of `0.5` and one-to-one best matching. It requires explicit product weights, score-bearing partitions, handling for missing tracks, failed runs, and empty truth, a rule for receipt timestamp ties, cross-product handling, rounding, and Detection points for every track.

Set the Detection allocation for the Cave track explicitly. The existing rubric assigns 15 points to Kashiwa RT and 10 to Reims turns. It does not assign Cave Detection points. The scorer does not infer that allocation.

`score-batch` can calculate participant Detection points when the plan supplies those decisions. For each participant and track, it computes product F1 from the exact TP, FP, and FN counts, applies the declared product weights to the included products, and uses that unrounded weighted mean for the Detection allocation. It rounds the displayed F1 and Detection points separately with the declared rounding mode and precision; the participant total is the sum of the rounded track allocations, rounded at the same precision. Evidence and Reproducibility remain uncomputed because their deterministic rubric calculations are not implemented yet. The full 55-point machine score and official scoring therefore remain blocked. Jury points, bonus points, and publication approval remain outside this command.

## Validate readiness and approvals

Close intake writers before scoring. Read-only scoring rejects a ledger with a WAL sidecar. Run the readiness check with the exact files you plan to use:

```sh
uv run civ score-readiness --ledger INTAKE_LEDGER --plan EVALUATION_PLAN.json \
  --preflight PREFLIGHT.json --review-status REVIEW_STATUS.json \
  --approval COMPUTATION_APPROVAL.json
```

The checker hashes the plan, immutable receipt database, selected bundles, EventSpecs and resources, products and manifests, truth packs, and runtime identity. The fingerprint changes if any bound input changes.

The preflight record uses `civ.cohort-preflight/v1alpha1`. It contains `plan_sha256`, `input_fingerprint`, `ledger_designation`, a hashed `runtime_rehearsal` artifact, one hashed `reference_reviews` artifact for every track and product, and `official_blockers`. A ledger designation names the reviewer and exact ledger hash. A runtime rehearsal artifact uses `civ.runtime-rehearsal/v1alpha1` and records the exact plan, input fingerprint, runtime identity, tool and Python versions, and a passed outcome.

Each reference review artifact uses `civ.reference-review-approval/v1alpha1`. It names the exact track, product, target, and truth hash. It records an approved decision, complete coverage, a reviewer, and a timestamp. Reuse an existing review only when its target and bound truth match the plan. A review for left turns does not approve a right-or-left target.

The review-status record uses `civ.cohort-review-status/v1alpha1`. It binds the plan, input fingerprint, and preflight hash. It records an approving reviewer and confirms the cutoff, runtime, ledger, references, and scoring policy. The computation approval uses `civ.computation-approval/v1alpha1` and binds the same plan and input fingerprint plus the exact preflight and review-status hashes.

These records must come from the responsible organizers. The tool checks their contents and hashes. It cannot create human signoff. A computation approval does not approve publication.

Run a nonofficial cohort replay with:

```sh
uv run civ score-batch --ledger INTAKE_LEDGER --plan EVALUATION_PLAN.json \
  --output ORGANIZER_RESULTS --approval COMPUTATION_APPROVAL.json
```

The command writes `results.jsonl`, `summary.json`, and organizer-only replay artifacts under `replays/`. Each replay record reports the number of attempts; failed outcomes also report a failure stage. `summary.json` reports readiness blockers and the computed Detection portion. Nonofficial runs always set `official_score` to false. `--official` stops before creating output unless every readiness gate passes.

## Keep unresolved reference work open

The current plan must not claim that Reims R&LT truth is complete from left-turn references alone. The Cave truth must come from recorded GNSS and the bound label evidence. Keep Cave locations, event times, truth intervals, sealed replay events, and organizer paths out of participant materials.

Use the [organizer label-pack guide](../phase3/organizer-label-packs.md) to verify product-bound truth. Use the [scoring reference](../reference/scoring.md) for matching and the [readiness guide](scoring-readiness.md) for the legacy `v1alpha1` diagnostic path.
