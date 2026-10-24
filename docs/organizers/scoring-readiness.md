# Check cohort scoring inputs

Use the [full cohort scoring guide](cohort-scoring.md) for the required-input checklist, plan setup, intake, replay, and result checks.

The runner checks its inputs itself. An optional diagnostic can report input and scoring-policy problems before replay:

```sh
uv run --locked civ score-readiness --ledger INTAKE_LEDGER --plan EVALUATION_PLAN.json
```

The command reads existing inputs without creating a ledger or writing scores. It exits with code 2 when readiness remains unresolved. Missing point policies can remain unresolved while diagnostic replay works. Read the reported problems rather than treating this command as a required approval step.

An empty roster or absent production ledger is not evidence of a missing organizer capability. To assess future-session readiness, use a separate private fixture profile and clearly named fixture deliveries, resolve it with `civ prepare-session`, then exercise all three tracks. Reconcile the expected team-by-track-by-product outcomes, receipt cutoff cases, failures, automatic components, and pending manual awards. Never relabel fixture receipts as genuine submissions. Refresh affected generated guides before the final rehearsal and record the exact code and material identities used.

Cohort scoring uses `civ.evaluation-plan/v1alpha2`. Separate preflight, review-status, and computation-approval records are not inputs to this workflow. Set `manual_review: "organizer_or_agent"` for Evidence and Reproducibility. With complete automatic policy and valid organizer inputs, `score-batch --official` can produce official automatic Detection and Cave components. The final total remains pending manual review. See the [official scope](../reference/scoring.md#official-automatic-components-and-final-review).
