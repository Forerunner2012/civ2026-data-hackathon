# Check cohort scoring inputs

Use the [full cohort scoring guide](cohort-scoring.md) for the required-input checklist, plan setup, intake, replay, and result checks.

The runner checks its inputs itself. An optional diagnostic can report input and scoring-policy problems before replay:

```sh
uv run --locked civ score-readiness --ledger INTAKE_LEDGER --plan EVALUATION_PLAN.json
```

The command reads existing inputs without creating a ledger or writing scores. It exits with code 2 when readiness remains unresolved. Missing point policies can remain unresolved while diagnostic replay works. Read the reported problems rather than treating this command as a required approval step.

Cohort scoring uses `civ.evaluation-plan/v1alpha2`. Separate preflight, review-status, and computation-approval records are not inputs to this workflow. Evidence and Reproducibility points remain pending, and `score-batch --official` rejects the run. See the [current scoring limits](../reference/scoring.md#current-limits).
