# Stable participant contracts and compatibility policy

Status: **decision for issue #15; enforced by issue #20**

This document fixes the participant-facing contract seam for Phase 2. Issue #20 published the
schemas under `schemas/` and moved producers and consumers to the stable identifiers atomically.
The participant path now emits and accepts only the `v1` contracts below; the candidate `v1alpha1`
identifiers survive only as rejection cases and in historical Phase 1 records.

## Decision

The stable participant set is:

1. EventSpec;
2. point resources referenced by EventSpec;
3. normalized event records;
4. the progressive run manifest;
5. metrics;
6. the deterministic metadata-only submission bundle; and
7. its reproduction entry point.

Stable identifiers use the literal form `civ.<artifact>/v<major>`. Phase 2 reserves major `v1`:

| Artifact | Stable identifier reserved for #20 | Identifier location |
| --- | --- | --- |
| EventSpec | `civ.eventspec/v1` | top-level `spec` field |
| Point resource | `civ.point-resource/v1` | top-level `contract` field |
| Normalized event record | `civ.event/v1` | `contract` in every JSONL record |
| Run manifest | `civ.run-manifest/v1` | top-level `contract` field |
| Metrics | `civ.metrics/v1` | top-level `contract` field |
| Submission bundle | `civ.submission-bundle/v1` | run manifest `submission.contract` |
| Reproduction entry point | `civ.reproduction/v1` | run manifest `submission.reproduction.contract` |

Identifiers are lowercase ASCII, case-sensitive, and are not semantic-version ranges. A consumer
recognizes exact literals, not “compatible-looking” strings. Prerelease identifiers such as
`v1alpha1` remain explicit candidate identifiers; `v1.0`, `V1`, `v01`, and bare `1` are malformed.

The compatibility window is **strict stable-only**. Once #20 promotes the participant path, public
consumers accept exact `v1` contracts. They reject candidate, malformed, mixed, and unknown future
versions before producing or mutating an artifact. There is no implicit or explicit candidate
migration command in Phase 2. Existing candidate work must be regenerated from the source bag and a
stable EventSpec. A previously scored directory or bundle is never rewritten in place.

This keeps the external seam small: every public command uses one contract-version resolver and
one diagnostic vocabulary. Format parsing and command-specific validation remain behind that
interface rather than being reimplemented by each caller.

## Contract inventory

“Owner” below names who controls the bytes, not who owns the repository. Canonical JSON means
UTF-8, sorted keys, compact separators, and one trailing LF. Hashes are SHA-256 of exact file bytes.

| Participant artifact | Owner | Producer | Consumers | Determinism and integrity rule | Identifier before #20 |
| --- | --- | --- | --- | --- | --- |
| EventSpec YAML | Participant authors the file; `civ` owns validation | participant, examples, reference kit | `civ detect`; `civ report` revalidates the bundled copy | Input bytes are not rewritten; `detect` copies them byte-for-byte and hashes the exact bytes. Semantics, units, expression evaluation, sorted evidence topics, and reserved extension behavior are schema-controlled. | `civ.eventspec/v1alpha1` in `spec` |
| Point resource JSON | Participant or reference kit authors the file; `civ` owns validation | participant, examples, reference kit | `civ detect`; `civ report` verifies manifest provenance | Canonical resource semantics are EPSG:4326 points with unique IDs and finite latitude/longitude bounds. Exact external bytes are hashed into sorted manifest provenance and resource-aware event identity, but are neither copied into the working directory nor bundled. | `civ.point-resource/v1alpha1` in `contract` |
| `events.jsonl` normalized records | `civ detect` | `civ detect` | `civ clip`, `civ score`, `civ report`, organizer scoring through bundle validation | One canonical JSON record per line; records sort by `(start_ns, end_ns, event_id)`. `event_id` is SHA-256 of `bag_sha256:spec_sha256:start_ns:end_ns`; each record repeats source/spec provenance. Stable records add their own identifier. | No record identifier; candidate status is only implied by the `v1alpha1` run manifest |
| `run-manifest.json` | `civ` pipeline | `detect` creates; `clip`, `score`, and `report` add facts | `clip`, `score`, `report`, intake validation, `score-batch` | Canonical JSON. It is the factual spine: exact source/spec/event/metric hashes, event count, evidence request, and clip facts must agree with the files. Optional sections reflect completed commands; a consumer requires the sections it uses. Runtime telemetry never enters it. | `civ.run-manifest/v1alpha1` |
| `metrics.json` | `civ score` | `civ score` | `civ report`; organizer batch scoring uses the same scoring module | Canonical JSON; deterministic for the same normalized events, label pack, and scorer semantics. The manifest records its exact hash. Metrics may record the organizer label-pack hash for provenance, but never label contents. | `civ.metrics/v1alpha1` |
| Reproduction entry point | Participant authors the file; `civ report` owns validation | participant or reference kit | `civ report`, intake validation, participant reopening the work | Exactly one UTF-8 top-level `reproduce.ps1` or `reproduce.sh`; it must invoke `civ detect`. `report` records its name, exact hash, and stable reproduction identifier in the manifest. It is metadata, contains no embedded bag/clip/label data, and is copied unchanged. | No embedded or enclosing identifier |
| `submission.zip` | `civ report` | `civ report` | `intake-form`, `intake-tally`, `intake-local`, `score-batch` through shared intake validation | Exactly the seven metadata entries below, sorted by POSIX path. ZIP entries are stored, unencrypted, mode `0644`, timestamp `1980-01-01T00:00:00`, and bounded by the Phase 1 entry/count/size limits. Intake reconstructs the canonical archive and requires byte equality. The final manifest identifies the bundle and reproduction contracts. | No bundle identifier; candidate status is implied by contained artifacts |

The stable bundle keeps the Phase 1 seven-entry boundary:

| Entry | Cardinality and rule |
| --- | --- |
| `detector/<name>.yaml` or `.yml` | exactly one EventSpec and no other file below `detector/` |
| `events.jsonl` | exactly one stable normalized event stream |
| `figure.<ext>` | exactly one top-level `.jpeg`, `.jpg`, `.png`, `.svg`, or `.webp` referenced by `report.md` |
| `metrics.json` | exactly one stable metrics artifact |
| `report.md` | exactly one report containing the five required headings and referencing exactly one figure |
| `reproduce.ps1` or `reproduce.sh` | exactly one stable reproduction entry point |
| `run-manifest.json` | exactly one stable manifest, finalized with `submission.contract` and reproduction name/hash/contract |

The figure and report are required metadata members but are not independent versioned data
contracts. Their structural rules are part of `civ.submission-bundle/v1`. Adding a bundle manifest
would create an eighth artifact and weaken the already-proven boundary, so bundle and reproduction
identifiers live in the existing run manifest. Raw bags, evidence clips, label packs, generated
data, caches, secrets, and runtime telemetry are forbidden from the bundle.

## Organizer-only exclusions

These artifacts may keep their current candidate identifiers until an organizer workflow needs a
separate freeze. They are not allowed to add fields to, select versions for, or otherwise widen the
participant contracts.

| Organizer-only artifact | Current identifier or shape | Reason excluded |
| --- | --- | --- |
| Label pack | `civ.label-pack/v1alpha1` | sealed scoring input supplied separately; never participant-authored or bundled |
| Online form response / Tally CSV | unversioned provider envelopes | transport adapters into the intake ledger, not participant analysis artifacts |
| Intake receipt | `civ.intake-receipt/v1alpha1` | organizer transport/audit result |
| Tally import summary | `civ.tally-import-summary/v1alpha1` | provider-specific operator result |
| Intake SQLite ledger and stored bundle layout | internal schema | organizer runtime state |
| Batch result record | `civ.batch-result/v1alpha1` | organizer evaluation result |
| Batch summary | `civ.batch-summary/v1alpha1` | organizer cohort/accounting result |
| Batch performance | `civ.batch-performance/v1alpha1` | explicitly nondeterministic runtime telemetry |

`civ score` and `score-batch` may consume a candidate organizer label pack while producing or
consuming stable participant artifacts. This is not a mixed participant version: the label pack is
on the organizer side of the seam. A future label-pack change must not change the `v1` participant
schemas or reinterpret an existing `metrics.json`; if scorer semantics change, the affected
organizer contract and tool version must change and scoring must be rerun.

The following public outputs are also outside the persisted participant freeze: human/JSON
`inspect` inventory, `detect` dry-run/command summaries, `clip` command summaries, `report` stdout,
and the `doctor` and `sample` terminal output. They remain deterministic where documented,
but are command output rather than portable participant artifacts.

## Compatibility matrix

The resolver classifies an identifier before a command parses artifact-specific fields. `<kind>`
and `<expected>` below are replaced with the artifact name and its exact `v1` literal. Diagnostics
go to stderr and public CLI commands exit `2`. A rejection must leave existing inputs byte-identical
and must not leave a partial output artifact.

| Input presented to a stable consumer | Classification | Behavior | Required diagnostic |
| --- | --- | --- | --- |
| Exact expected `civ.<kind>/v1` | supported | **Accept**, then validate the complete stable schema and invariants | none |
| Exact candidate `civ.<kind>/v1alpha1` | legacy candidate | **Reject**; regenerate from source with the stable toolchain | `unsupported <kind> contract 'civ.<kind>/v1alpha1'; expected '<expected>'; regenerate with the stable civ workflow` |
| Candidate normalized event with no record `contract` | legacy candidate when enclosed by a candidate manifest; otherwise missing | **Reject** before consuming intervals | same legacy diagnostic when provenance proves candidate; otherwise the missing diagnostic below |
| Missing identifier, `null`, or non-string identifier | malformed | **Reject** | `<kind> contract is required; expected '<expected>'` |
| Wrong namespace/kind or malformed form, including `v1.0`, `V1`, `v01`, or bare `1` | malformed | **Reject** | `invalid <kind> contract '<actual>'; expected '<expected>'` |
| Known namespace/kind with another prerelease, such as `v1beta1` | unsupported | **Reject** | `unsupported <kind> contract '<actual>'; expected '<expected>'` |
| Unknown future stable or prerelease major, such as `v2` or `v2alpha1` | future major | **Reject**; never guess forward compatibility | `unsupported <kind> contract '<actual>'; this civ-workshop supports '<expected>'` |
| Exact `v1` identifier with an unknown field outside a schema-declared extension point | invalid stable artifact | **Reject**; stable schemas are closed by default | `invalid <kind> '<expected>': unknown field '<field>'` |
| Working directory or bundle containing different participant versions | mixed | **Reject** the whole set before mutation or scoring | `mixed participant contract versions: <sorted identifiers>; regenerate the complete working directory with one civ-workshop version` |
| Identifier names the wrong participant artifact, for example metrics presented as a manifest | wrong kind | **Reject** | `invalid <kind> contract '<actual>'; expected '<expected>'` |

There is deliberately no “accept and rewrite,” “best effort,” or in-place migration row. Changing
only identifier strings is unsafe because #16 and #17 changed EventSpec meaning, while event IDs,
spec hashes, metrics, manifest hashes, and bundle hashes are transitively linked. Regeneration must
create a fresh output directory from the original bag and stable EventSpec, followed by
`detect -> clip -> score -> report`. Candidate directories and bundles remain readable as historical
bytes by ordinary archive/text tools, not by the stable scoring path.

Patch-level implementation releases may add diagnostics or fix implementation defects while
continuing to emit and accept the same exact `v1` schemas and semantics. Any required-field removal,
meaning/unit change, ordering/hash change, or new interpretation of existing bytes requires a new
major contract. Additive fields are compatible only at a schema-declared extension point; otherwise
closed-schema rejection prevents one tool release from assigning meaning that another silently
ignores.

## Producer and consumer enforcement

| CLI command | Participant contract role after #20 |
| --- | --- |
| `civ inspect` | no versioned participant artifact input or output; unchanged by the freeze |
| `civ detect` | require `civ.eventspec/v1` and any referenced `civ.point-resource/v1`; emit `civ.event/v1` records, a `civ.run-manifest/v1`, and an unchanged stable EventSpec copy |
| `civ clip` | require a stable event stream and manifest as one version-coherent set before reading the source bag or writing clips; update only the stable manifest |
| `civ score` | require a stable event stream and manifest; consume the separately versioned organizer label pack; emit `civ.metrics/v1` and update only the stable manifest |
| `civ report` | require the complete stable working set; validate the reproduction entry point; finalize the manifest with `civ.submission-bundle/v1` and `civ.reproduction/v1`; emit the canonical stable bundle |
| `civ intake-form`, `intake-tally`, `intake-local` | accept only a complete stable bundle through the shared validator; continue to emit organizer-only receipts/summaries |
| `civ score-batch` | accept only bundles that pass the same shared stable validator; continue to consume organizer label packs and emit organizer-only batch records |
| `civ doctor`, `civ sample` | no persisted participant artifact in this freeze; they do not create an alternative version seam |

Version resolution belongs in one shared module used by EventSpec, point resource, event, manifest,
metrics, bundle, and intake validators. The module interface returns only supported/rejected classification plus the
canonical diagnostic; callers do not compare version strings themselves. Artifact parsers then own
their closed schema and invariants. This concentrates compatibility changes in one place and makes
the public command seam the test surface.

## Freeze implementation and test inventory

Issue #20 must update the participant path atomically. No mergeable intermediate state may emit a
stable artifact beside a candidate participant artifact.

### Producers and consumers to change

- `src/civ_workshop/event_spec.py`: resolve and validate the stable EventSpec.
- `src/civ_workshop/resources.py`: resolve and validate stable point resources without copying or
  bundling their bytes.
- `src/civ_workshop/models.py` and `src/civ_workshop/artifacts.py`: carry, serialize, and read the
  stable event-record identifier.
- `src/civ_workshop/detection.py`: emit stable event records and the stable manifest.
- `src/civ_workshop/clipping.py`: validate event/manifest coherence before output and preserve the
  stable manifest.
- `src/civ_workshop/scoring.py`: validate stable inputs, emit stable metrics, and preserve the
  stable manifest.
- `src/civ_workshop/reporting.py`: validate the complete stable set, finalize the bundle and
  reproduction identifiers, and retain canonical seven-entry ZIP behavior.
- `src/civ_workshop/intake.py`: reject candidate/malformed/mixed bundles through the shared stable
  validator before recording a receipt.
- `src/civ_workshop/batch.py`: consume only intake-validated stable bundles without promoting label
  or batch contracts.
- `src/civ_workshop/cli.py`: use the shared diagnostics and preserve exit status `2`/no traceback.
- `examples/kashiwa/right_turn.yaml` and `examples/reims/left_turn.yaml`: move atomically to the
  final stable EventSpec shape decided by #16/#17.
- `examples/reims/cave-encounter.yaml`, `examples/reims/cave-zones.json`, and the point-resource
  schema: move atomically to the stable EventSpec/resource identifiers.

### Contract fixtures and tests to add or update

- Add one accepted fixture and rejected fixtures for missing, malformed, `v1alpha1`, other
  prerelease, future-major, wrong-kind, unknown-field, and mixed-version cases for every participant
  artifact. Keep them small and human-readable under `tests/fixtures/contracts/`.
- Add resolver table tests that pin every row and exact diagnostic in the compatibility matrix.
- Update `tests/helpers.py` so the micro EventSpec and generated working directory use one stable
  participant version while the organizer label fixture remains independently versioned.
- Update `tests/test_cli_workflow.py` for stable EventSpec/event/manifest production, rejection
  before partial output, manifest provenance, exact seven-entry bundle contents, reproduction
  declaration, and byte-identical fresh-directory reruns.
- Update `tests/test_scoring.py` for stable event/manifest inputs, stable metrics output, and rejection
  without changing pre-existing metrics or manifest bytes.
- Update `tests/test_intake.py` for accepted stable bundles plus candidate, malformed, mixed,
  noncanonical, forbidden-payload, and future-major rejection before any receipt or stored bundle is
  committed.
- Update `tests/test_tally.py` only where its runtime-generated bundle crosses the participant seam;
  keep Tally headers, summaries, and receipt identifiers organizer-only.
- Update `tests/test_batch.py` so every runtime bundle is stable and the organizer label/result
  identifiers remain excluded. Preserve deterministic `results.jsonl`/`summary.json`, telemetry-only
  `performance.json`, and label non-leakage assertions.
- Validate both checked-in EventSpecs and the final derive/resource examples against their stable
  schema, then exercise them through `civ detect` rather than schema-only tests.
- Preserve the Phase 1 limit, canonical-ZIP, offline, Kashiwa/Reims transfer, and exact-byte
  assertions. Historical `docs/phase1/*-acceptance.md` records continue to describe the proven
  candidate run and must not be rewritten as if they had emitted stable identifiers.

The freeze is complete only when a repository search finds no participant-path `v1alpha1` producer
or consumer outside explicit rejection fixtures and historical Phase 1 records. Organizer-only
candidate identifiers are expected to remain.
