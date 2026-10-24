# Score a full cohort

Use this procedure to collect track submissions, replay their detectors against assigned recordings, and compare results with reviewed organizer truth. All three tracks use `civ.evaluation-plan/v1alpha2` and source-bound `civ.label-pack/v1alpha1` references.

The runner produces metrics and, with an explicit policy, the 25 Detection points and a separate Cave bonus of up to 10 points. Evidence and Reproducibility retain 15 points each for organizer or agent review. See the [current scoring policy and manual subcriteria](../reference/scoring.md).

## 1. Gather the required inputs

Confirm that you have the following inputs:

- [ ] The organizer checkout, `uv`, and access to its locked dependencies.
- [ ] Every assigned MCAP recording, including sealed products, and its `civ.data-product-manifest/v1` manifest.
- [ ] One reviewed truth pack for each assigned track and exact recording. An approved empty pack is valid.
- [ ] The complete team roster, stable team IDs, and cutoff with a time zone.
- [ ] Submitted metadata-only ZIPs, with each delivery's team, track, receipt time, SHA-256, and unique delivery ID.
- [ ] A private directory for the plan, ledger, and results.

Use consistent track IDs in the plan and intake:

| Track ID | Target |
| --- | --- |
| `kashiwa-rt` | Kashiwa right turns |
| `reims-rlt` | Reims right or left turns |
| `reims-caves-optional` | Reims Cave encounters |

Labels alone are insufficient because scoring replays detectors against recordings. Review images, GUIs, and previous rehearsal results are unnecessary once reviewed references are ready. Prepare missing references through the [label-review procedure](../phase3/label-review.md#export-a-reviewed-organizer-reference) before scoring.

## 2. Set up the environment and session directory

From the repository root, run:

```sh
uv sync --locked
SESSION="$HOME/civ-organizer/scoring-session"
mkdir -p "$SESSION"
cp docs/organizers/examples/cohort-plan.example.json "$SESSION/plan.json"
```

Use a private session path outside Git:

```text
scoring-session/
  plan.json
  incoming/    # Delivered ZIPs, if stored here
  ledger/      # Intake creates the database and stored bundles
  results/     # Scoring creates summaries and replay artifacts
```

## 3. Bind the plan to the session inputs

Edit the copied [example plan](examples/cohort-plan.example.json). It contains three tracks and one placeholder product per track. Its paths, zero hashes, schema names, roster, and cutoff must be replaced before scoring.

1. Set `session_id`, `cutoff`, and `participants`. Include registered teams that submitted nothing, so missing tracks remain visible.
2. Add every assigned product to each track. Set its unique `product_id` and `partition` to `warmup`, `development`, or `sealed`.
3. Set each product's `recording`, `manifest`, and `truth` paths and SHA-256 values. Relative paths resolve from `plan.json`. The truth pack's `source_sha256` must identify the exact recording.
4. Copy the required schema bindings from the manifest's `product.topics` into `input_contract.schemas`. Retain `topic`, `schema_name`, `schema_encoding`, `schema_sha256`, and `message_encoding`. Set `input_contract.topics` to those same topics.
5. Set each track's accepted EventSpec contracts, allowed signal topics, resource limits, timeout, and retries. Include the signal topics that accepted participant detectors need. Check these settings against the assigned recordings.

Calculate a file hash with:

```sh
sha256sum /path/to/recording.mcap
```

The same Reims recording can appear in both Reims tracks, with different truth packs. Never substitute turn labels for Cave truth. The scorer consumes reviewed Cave packs through the same mapping as turn packs. It does not generate truth during scoring.

The example includes the agreed event policy. Replace its placeholder product weights with weights for every assigned recording. Use equal turn-track weights, and limit empty Cave recordings collectively to 10% of its weight. Check duration ranges, event counts, and the score of an always-silent detector before freezing weights. These are private checks, not participant hints. The [points policy](../reference/scoring.md#event-policy) and [plan schema](../../schemas/civ.evaluation-plan.v1alpha2.schema.json) describe the fields.

## 4. Record each track delivery

Set these values from the actual delivery, then run intake:

```sh
BUNDLE="$SESSION/incoming/team-a-kashiwa.zip"
TEAM_ID='team-a'
TRACK_ID='kashiwa-rt'
RECEIVED_AT='2026-11-01T12:00:00+01:00' # Replace with the actual receipt time
SUBMITTED_SHA256='REPLACE_WITH_SUBMITTED_SHA256'
DELIVERY_ID='team-a-kashiwa-delivery-1'
uv run --locked civ intake-local "$BUNDLE" \
	--ledger "$SESSION/ledger" \
	--identity "$TEAM_ID" --track-id "$TRACK_ID" \
	--received-at "$RECEIVED_AT" --sha256 "$SUBMITTED_SHA256" \
	--delivery-id "$DELIVERY_ID"
```

The first accepted delivery creates `ledger/intake.sqlite3` and stores the validated bundle. No separate ledger initialization is needed. Preserve the printed receipt and repeat intake for every delivery and track. Use the SHA-256 supplied with the delivery. Check that each receipt identifies the intended team and track.

For exported online deliveries, use `civ intake-form` with a `track_id`, or `civ intake-tally` with the `Track ID` CSV column. See each command's `--help` for arguments.

The runner selects the latest eligible receipt on or before the plan cutoff for each team and track. A selected delivery that fails replay stays failed. The runner does not substitute an older delivery. Equal timestamps require `scoring_policy.receipt_timestamp_ties` to select `earlier_ledger_sequence` or `later_ledger_sequence`.

Cohort selection uses the cutoff in this plan. The receipt's historical intake `status` does not determine cohort eligibility.

## 5. Run the cohort

Stop intake writers and keep scoring inputs unchanged during replay. Read-only scoring rejects a ledger with a SQLite WAL sidecar.

```sh
uv run --locked civ score-batch \
	--ledger "$SESSION/ledger" \
	--plan "$SESSION/plan.json" \
	--output "$SESSION/results"
```

The runner checks product hashes and schema bindings, validates selected bundles, and runs their EventSpecs and resources on every assigned recording. It does not execute submitted reproduction scripts or use submitted events and metrics as predictions. No separate detector-run command or rehearsal wrapper is needed.

The runner records one outcome per registered team, track, and assigned product. Before committing outputs, it checks that the inputs still match. If inputs changed during replay, it discards staged output and preserves previous results.

No separate preflight, review-status, runtime, or computation-approval file is required. The batch runs its own checks. An [optional input diagnostic](scoring-readiness.md) is available before replay.

To request official automatic components after session inputs and policy are settled, add `--official` to the same command. Its scope is automatic Detection and Cave points. The final total stays pending manual review; this option creates no manual awards or publication permission. Participant submission errors receive the configured zero without falling back. Organizer failures leave points pending and require repair and rerun.

## 6. Check completeness and read results

Inspect the private outputs:

| Output | What to check |
| --- | --- |
| `summary.json` | Outcome counts, receipt dispositions, unregistered identities, runtime, and pending scoring decisions |
| `summary.json` → `detection_metrics.participants` | Track metrics and separate partition metrics, including sealed products |
| `results.jsonl` | Individual outcomes, metrics, selected submissions, replay attempts, and failure stages |
| `replays/` | Generated events, metrics, and source-bound replay artifacts |
| `manual-review-template.json` | Unawarded Evidence and Reproducibility worksheet, with subcriteria and input identities; copy it before recording awards |

Complete these checks before using the comparison:

- [ ] Confirm the roster, cutoff, and selected deliveries match the session.
- [ ] Confirm the outcome count equals `summary.identities` multiplied by the sum of assigned product counts across tracks. This identity count includes rostered teams and any additional identities found in receipts. Reconcile `unregistered_identities` before interpreting the comparison.
- [ ] Investigate missing tracks, invalid inputs, and failed replays. A successful command does not mean every assignment scored.
- [ ] Read `complete`, `partial`, or `unavailable` alongside each metric. Successful zero-event runs still count as scored outcomes.
- [ ] Compare sealed metrics separately from development and warm-up metrics.
- [ ] Check pending point components before interpreting totals. Do not replace `null` with zero. Complete the manual technical, jury, and existing bonus awards separately before calculating final totals. Cave points require no manual award.

Pooled metrics sum TP, FP, and FN across successful products. They do not average product F1 or apply point weights. Missing and failed products contribute no invented counts. See the [scoring reference](../reference/scoring.md) for matching and point calculations.

Keep plans, ledgers, truth, Cave locations, event times, and replay artifacts in organizer-controlled storage. Share only authorized participant results. Publication remains a separate decision.
