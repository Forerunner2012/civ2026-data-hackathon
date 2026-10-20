# Check organizer scoring readiness

Use the root organizer project to inspect the prerequisites before a batch diagnostic:

```sh
uv run civ score-readiness --ledger LOCAL_INTAKE \
  --plan LOCAL_PLAN.json --preflight LOCAL_PREFLIGHT.json \
  --review-status LOCAL_REVIEW_STATUS.md
```

The command reads existing inputs, prints JSON and exits with code 2 while official scoring
is blocked. It never creates a ledger, changes review records or writes scores. Keep its output
in organizer-controlled storage because diagnostics can contain private evidence paths.

The current `civ.evaluation-plan/v1alpha1` drafts do not establish a named approval,
confirmed session cutoff, runtime rehearsal or authoritative ledger designation. The checker
therefore always reports `ready: false` and `official_score: false`. Adding an `approved`
field or supplying later review prose cannot change that result. `score-batch --official`
reports the blockers and stops before scoring or creating output. This is a fail-closed
reporting path, not a completed official-evaluation implementation.

## Resolve the human gates

The session owner must select the final plan and event definitions, confirm the cutoff and
runtime rehearsal, designate the intake ledger, and record named organizer approval bound to
the final inputs. A future approval contract needs that human decision before code can accept it.
The current intake cutoff remains the historical `2026-09-03T12:30:00+09:00` value.

Source-bound label packs establish reference bytes and source identity. They do not encode
complete contextual coverage or an approved event definition. The checker compares selected
pack hashes, source hashes and datasets, checks each track's reference status, and reports intake
sources without an exact selected reference. It never substitutes a practice pack for a sealed pack.

The selected evaluation plan owns the intended target. A generated preflight is a projection
of a particular plan hash, not approval. A later review-status note cannot silently supersede
either record. The checker preserves every preflight blocker, flags a mismatching plan hash,
and requires explicit human reconciliation with the review-status record.

For the rehearsal, the session owner must resolve the Reims contextual right-or-left target
versus the supplied left-turn EventSpec and selected historical left-turn references. Completed
camera reviews do not select the separate both-direction candidate in a plan. Leave the
reference selection, coverage, deadline and approval gates open until their owners decide.

## Keep diagnostic scores separate

`civ score-batch --ledger LOCAL_INTAKE --labels LOCAL_LABELS --output LOCAL_RESULTS`
continues to compute diagnostics with the existing matching and receipt-selection rules.
Every result and summary records `official_score: false`; the summary includes readiness blockers.
The optional `--plan`, `--preflight` and `--review-status` arguments add their checks.
`complete` still means that both dataset components were scored. It does not mean official approval.
Batch scoring reads receipts without initializing or migrating the intake database.
Close intake writers and use a stable ledger snapshot. Read-only scoring refuses a ledger with
a WAL sidecar and opens the database as immutable so SQLite cannot create shared-memory files.

## Record preparation and scoring decisions

The organizer CLI owns new structured decision records for the repeated preparation and scoring
checks. Prepare a JSON file with these five fields:

```json
{
  "phase": "readiness",
  "decision": "Retain the unresolved scoring gates",
  "why": "The current plan does not establish approval",
  "evidence": ["readiness.json"],
  "result": "blocked"
}
```

Save the check output as `readiness.json` beside the intended log, then run:

```sh
uv run civ record-decision LOCAL_RECORD.json --log LOCAL_OUTPUT/decisions.tsv
```

Pass text through the JSON file rather than constructing a TSV row in a shell. Evidence is a
JSON array of existing artifact paths, relative to the log directory or absolute. The writer
normalizes prose whitespace, serializes quoting and tabs, and checks the header, six-column
rows and evidence paths before and after appending. LF and CRLF logs are accepted. A single
organizer must own a log; this helper is not a concurrent intake ledger.

Historical malformed logs are evidence. The writer refuses them; create a new log and explicitly
record any correction with pointers to the original artifacts. Do not repair old rows in place.
The rehearsal's detector-refinement script has no maintained repository owner. Its guarded
YAML edit and newline regression checks remain local task tooling rather than a new product API.
