# Phase 3 two-dataset authority policy

Status: **accepted for the Phase 3 gate**

Recorded: 2026-08-28

One participant entry aggregates two unchanged metadata-only submission bundles: one Kashiwa run
and one Reims run. The stable participant contracts and bundle bytes do not change. Authority is an
organizer concern selected independently for each `(identity, dataset)` key.

## Dataset derivation

Intake validates each submitted bundle and records the `source.sha256` from its stable `v1` run
manifest in the organizer-only receipt. Online, Tally, recovery-form, and local/USB adapters do not
accept or trust a participant-provided dataset name.

During `civ score-batch`, the validated source hash is matched to the organizer mapping carried by
the label-pack `source_sha256` and `dataset` fields. That mapping decides whether a receipt is a
Kashiwa run, a Reims run, or outside the two-dataset scoring set. Participant prose, filenames,
delivery identifiers, and form fields never decide dataset authority.

The scoring run refuses an organizer mapping that does not name exactly both `kashiwa` and `reims`;
an incomplete mapping therefore cannot make a one-component entry appear complete.

The intake database adds a nullable `source_sha256` column in place. New receipts always populate
it. Existing organizer ledgers remain readable; legacy rows without stored provenance are derived
from their validated bundle when possible.

## Authority and cutoff

For each identity and derived dataset, the last receipt at or before 12:30:00 Asia/Tokyo is
authoritative. Timestamp ties retain intake sequence order. Resubmission is unlimited and selection
for one dataset cannot supersede the companion dataset.

The legacy `IntakeLedger.authoritative(identity)` convenience refuses identities with more than one
validated source provenance. This prevents new code from silently restoring one-bundle-per-identity
selection; paired authority belongs behind the `score-batch` interface where the organizer mapping
is available.

Every delivery is retained in deterministic intake order with its delivery identifier, adapter,
original and UTC timestamps, cutoff status, bundle hash, validated source hash, derived dataset,
and terminal state:

| Delivery state | Meaning |
| --- | --- |
| `authoritative` | last on-time receipt selected for its derived dataset |
| `superseded` | earlier on-time run replaced by a later run for the same dataset |
| `duplicate-source` | earlier receipt repeats the authoritative source and exact bundle bytes |
| `late-only` | receipt arrived after the cutoff and cannot become authoritative |
| `cross-dataset` | validated source has no entry in the organizer two-dataset mapping |
| `malformed` | accepted provenance is known, but the stored bundle is missing, corrupt, or fails revalidation |

## Aggregate participant result

`results.jsonl` contains one canonical, identity-sorted organizer result per participant identity.
Each result has ordered Kashiwa and Reims components, all delivery-audit records, the scored dataset
metrics, redacted diagnostics, and one aggregate state:

- `complete`: both components reached `scored`;
- `incomplete`: either component did not reach `scored`.

Component terminal states are `scored`, `failed`, `malformed`, `late-only`, and `missing`. A valid
component remains scored when its companion is missing, late, malformed, or rejected, but the
aggregate entry remains incomplete and cannot masquerade as a two-dataset score.

`summary.json` counts complete and incomplete identities, scored components per dataset, all
receipts by cutoff status, and the organizer mappings used. `results.jsonl` and `summary.json`
remain byte-identical across reruns on identical inputs; runtime measurements remain isolated in
`performance.json`.

## Compatibility and scope

The participant still runs `civ report` once per dataset run and submits each emitted
`submission.zip` unchanged. No raw data, evidence clip, label pack, or combined participant bundle
is introduced. Human/AI report scoring and the real-data 15–30-entry throughput rehearsal remain
outside this policy ticket.
