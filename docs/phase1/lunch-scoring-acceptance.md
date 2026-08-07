# Phase 1 lunch scoring acceptance

## Contract

One unattended command turns the intake ledger into the ranked machine results used at the 13:15
selection point:

```powershell
civ score-batch --ledger D:\civ-intake --labels D:\civ-labels --output D:\civ-results
```

The batch reads only the authoritative last-on-time bundle per identity, exactly as the intake
contract selects it. Late responses stay quarantined and cannot enter ranking, and a superseded
on-time bundle is never scored. Organizer label packs are supplied separately through `--labels`;
each pack is matched to a submission by its `source_sha256`, so Kashiwa and French entries are
scored through the same evaluator interface and the same temporal-matching semantics proven by the
earlier slices. Two packs declaring the same source, an unreadable pack or an empty label directory
abort the run before any entry is scored, which keeps organizer paths out of per-entry diagnostics.

Every entry reaches exactly one terminal state:

| Status | Meaning | Validation |
|---|---|---|
| `scored` | validated bundle scored against the matching organizer pack | `passed` |
| `failed` | structurally valid, but no pack matches its source or the evaluator refused it | `passed` |
| `invalid` | the authoritative bundle is missing, corrupt at rest or fails re-validation | `failed` |
| `quarantined` | the identity has no on-time receipt | `skipped` |

One failing entry never stops or corrupts the rest of the batch: bundle, validation and scoring
failures are captured per entry, and an unexpected scorer error is recorded as `failed` rather than
propagated.

## Outputs

- `results.jsonl` — one canonical JSON object per identity, sorted by identity. Each result records
  identity, delivery id, both receipt timestamps, bundle hash, scorer/contract versions, per-dataset
  metrics, validation outcome and diagnostics with sorted keys.
- `summary.json` — counts for `scored`, `failed`, `invalid` and `quarantined` that sum to the entry
  total, scored entries per dataset, receipt totals, the cutoff, and the label packs by dataset and
  hash.
- `performance.json` — the explicitly excluded runtime measurements: total and per-entry elapsed
  time, the slowest five entries, peak traced memory, input bundle bytes and result bytes, plus the
  2,700-second budget and whether the run stayed inside it.

`results.jsonl` and `summary.json` are byte-identical across reruns on identical inputs;
`performance.json` is the only file that moves. Label pack contents never appear in any output —
results carry dataset names, counts and hashes only.

## Automated evidence

`tests/test_batch.py` generates 30 representative metadata-only bundles at runtime and commits none
of them:

- 20 scored entries across two independently sourced dataset packs, cycling competent, low-quality,
  duplicate-heavy, incomplete and missed detector profiles; the recorded metrics pin each profile
  (competent F1 1.0, duplicate-heavy precision 0.25 at recall 1.0, incomplete and missed at zero).
- 3 entries whose source has no organizer pack, 3 whose stored bundle is corrupted at rest, and 4
  whose only receipt is late.
- Extra receipts prove last-on-time selection: one identity resubmits on time, another submits again
  after the cutoff, and neither displaces the authoritative bundle.
- Further cases prove the summary accounts for all 30 entries exactly once, deterministic byte-identical
  reruns, the absent-label-directory and ambiguous-pack refusals, the performance record's shape, and
  that a single `civ score-batch` invocation scores the cohort with no per-entry command.
- The batch is run with `socket.socket` and `socket.create_connection` replaced by failures, proving
  the scoring run performs no network access.

## Measured throughput

Windows proof host (Microsoft Windows 11 Pro, 10.0.26200, CPython 3.12): the 30-entry cohort
validated and scored in 0.86 s total, 0.067 s for the slowest entry, 1,145,294 bytes peak traced
memory, 86,868 bytes of input bundles and 23,075 bytes of results. Real metadata bundles are the
same order of magnitude as the generated ones — 10,596 bytes for Kashiwa and 6,055 bytes for
French — so the 45-minute lunch budget has roughly three orders of magnitude of headroom. Scoring is
sequential on purpose; there is no parallelism to tune until a measurement demands it.

## Routed follow-up

The pinned Ubuntu 26.04 / ROS 2 Lyrical container measurement of this same 30-entry run, with
network access disabled and GNU `time -v` telemetry, belongs to the integrated Phase 1 gate in issue
#11 alongside the two data-stack runs and the attendee-page traversal. This record covers the
code-complete lunch-scoring workflow and its host measurement only.
