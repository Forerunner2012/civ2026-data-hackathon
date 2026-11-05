# Participant contracts

Use these references for the current artifact boundary and exact contract identifiers. Follow the [participant QuickStart](../quickstart.md) for the command sequence; this page records what those commands produce and consume.

## Versioned artifacts

| Artifact | Contract and key fields |
| --- | --- |
| EventSpec YAML | `spec: civ.eventspec/v1`; required `name`, `signals`, `condition`, `timing`, and `evidence`; optional `resources` and `derive`. See the [schema](../../schemas/civ.eventspec.v1.schema.json). |
| Point resource JSON | `contract: civ.point-resource/v1`, `coordinate_reference`, and `points` with `id`, `latitude`, and `longitude`. EventSpecs bind resources by a contained relative path; the run manifest records each resource hash. See [resource rules](eventspec-resources.md) and the [schema](../../schemas/civ.point-resource.v1.schema.json). |
| `events.jsonl` | One `civ.event/v1` record per line: `event_id`, `bag_sha256`, `spec_sha256`, `start_ns`, `end_ns`, and `trigger_values`. Records are ordered deterministically. Event identity uses source, specification, interval, and any bound resource hashes. See the [event schema](../../schemas/civ.event.v1.schema.json). |
| `run-manifest.json` | Current `civ.run-manifest/v2`; `source` names the exact input and its `sha256`, while `spec` and `events` record their names and hashes. The required set is `contract`, `source`, `spec`, `events`, and `evidence`; completed steps add `resources`, `clips`, `metrics`, and `submission`. Canonical v1 manifests remain accepted. See the [v1 schema](../../schemas/civ.run-manifest.v1.schema.json) and [v2 schema](../../schemas/civ.run-manifest.v2.schema.json). |
| `metrics.json` | `civ.metrics/v1` records evaluated metrics and the exact reference-pack digest, not label intervals. Without a practice reference, `civ.metrics/v2` records `status: "not_evaluated"`, a reason, source identity, and null scores, reference digest, and matching. Both retain the required metrics artifact. See the [v1 schema](../../schemas/civ.metrics.v1.schema.json), [v2 schema](../../schemas/civ.metrics.v2.schema.json), and [scoring reference](scoring.md). |

Stable participant identifiers are exact, case-sensitive values. Candidate `v1alpha1` participant artifacts are not silently upgraded; regenerate a stable run from the source and stable EventSpec. The separate practice and organizer label-pack audience boundary is described in [scoring](scoring.md).

## Metadata-only submission

`civ report` writes `submission.zip` with seven core entries: one EventSpec under `detector/`, `events.jsonl`, one top-level figure, `metrics.json`, `report.md`, one `reproduce.ps1` or `reproduce.sh`, and `run-manifest.json`. The manifest's `submission.contract` identifies `civ.submission-bundle/v1` or `civ.submission-bundle/v2`; both retain `civ.reproduction/v1` with the entry-point `name` and `sha256`.

New runs use the v2 manifest and bundle. Canonical v1 bundles remain accepted. A v2 bundle may include declared EventSpec resources and a bounded extension whose exact entries are hash-bound by `extension/manifest.json`; intake treats trace and test payloads as data and does not execute them. Neither version includes the source recording, evidence clips, scoring labels, caches, secrets, or runtime telemetry. See the [packaging steps](../quickstart.md#8-validate-and-keep-the-metadata-only-zip), the [archive contract](submission-archive.md), and the [bundle schemas](../../schemas/civ.submission-bundle.v1.schema.json) and [v2 schema](../../schemas/civ.submission-bundle.v2.schema.json).

## Producer and consumer responsibilities

| Artifact | Producer | Consumers and integrity checks |
| --- | --- | --- |
| EventSpec and point resources | Participant | `detect` validates and copies exact bytes; `report` and intake verify hashes and declared resource paths. |
| Events and run manifest | `detect` | `clip`, `score`, and `report` validate source/spec hashes and event coherence. `clip` adds local evidence facts, `score` adds metrics, and `report` finalizes submission provenance. |
| Metrics | `score` | `report` verifies the manifest-bound bytes. Evaluated metrics identify the reference hash; unevaluated metrics carry null scores. |
| Report, figure, reproduction recipe | Participant | `report` validates their structure and binds exact bytes. Organizers inspect the recipe without executing submitted scripts. |
| Submission ZIP | `report` | Intake validates contracts, hashes, paths, limits, and canonical ZIP bytes. Cohort scoring replays the accepted EventSpec/resources with the trusted organizer runtime. Submitted events and metrics are audit artifacts, not cohort predictions. |

Current runs pair a v2 manifest with v1 events, EventSpec, resources, and reproduction declarations. Metrics use v1 for evaluated runs or v2 for `not_evaluated` runs. These combinations are intentional. Canonical v1 bundles remain accepted without conversion. Unknown versions and fields outside declared extension points are rejected. Regenerate candidate participant artifacts in a fresh directory instead of changing identifier strings.

Practice references and sealed truth stay outside the submission. The saved evaluation plan controls roster, cutoff, and assignments; the intake ledger records receipts. Organizer results and runtime telemetry have separate contracts. See the [scoring reference](scoring.md) and [cohort procedure](../organizers/cohort-scoring.md).

The [Phase 2 freeze](../history/phase2/stable-contracts-and-compatibility.md#contract-inventory) preserves the original inventory, v1 compatibility diagnostics, and implementation history.
