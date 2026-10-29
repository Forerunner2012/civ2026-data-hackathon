# Submission archive contract

This reference defines the current v2 archive and accepted v1 compatibility. Follow the [QuickStart](../quickstart.md#8-validate-and-keep-the-metadata-only-zip) to produce a bundle. The [Phase 5 record](../history/phase5/extension-aware-submission-v2.md) retains the original implementation, verification, and approval.

## Scope

`civ.submission-bundle/v2` retains seven core metadata artifacts. Its optional, bounded extension carries declared EventSpec resources, provenance, grounded agent traces, and participant-authored regression tests.

The bundle does not activate the reserved EventSpec `detector:` field and never executes submitted
trace or test content at intake. Raw evidence and organizer-only artifacts remain out of scope.

## Contracts and compatibility

The extension-aware archive uses these closed schemas:

- `civ.run-manifest/v2`, whose `submission` member references the v2 declaration;
- `civ.submission-bundle/v2`, which retains `civ.reproduction/v1` and optionally hash-binds
  `extension/manifest.json`; and
- `civ.submission-extension/v1`, whose sorted entries contain exactly `kind`, `media_type`, `path`,
  and lowercase `sha256`.

The existing v1 schemas and bytes are unchanged. New `civ detect` runs emit run-manifest v2 and new
`civ report` runs emit submission-bundle v2. Canonical v1 bundles continue through the same intake validation, storage, authority
selection, and scorer-input path. Collection routes are session-specific. An authority decision can
therefore compare accepted v1 and v2 deliveries for the same source without converting either ZIP;
the later valid on-time delivery wins and its exact accepted bytes are retained.

Events, EventSpecs, point resources, and reproduction declarations keep their stable v1
contracts. Metrics use v1 for evaluated runs or v2 for `not_evaluated` runs, as defined in [participant contracts](participant-contracts.md#versioned-artifacts). A v2 run manifest containing v1 normalized events is intentional, not a mixed working
directory.

## Canonical archive layout

```text
detector/<eventspec>.yaml              core 1 of 7
events.jsonl                           core 2 of 7
<one top-level figure>                 core 3 of 7
metrics.json                           core 4 of 7
report.md                              core 5 of 7
reproduce.ps1 | reproduce.sh           core 6 of 7
run-manifest.json                      core 7 of 7
detector/<declared resource path>      optional external-resource payload
extension/manifest.json                present when any extension payload exists
extension/<participant path>           optional provenance, agent-trace, regression-test payload
```

`civ detect` resolves each EventSpec resource under the source EventSpec directory, rejects escape,
and copies its bytes beside the bundled EventSpec at the already-declared relative path. The
EventSpec itself is not rewritten. Its archive-relative resource path is declared with kind
`external-resource` in the extension manifest. Non-resource payloads must live under `extension/`.

Supported inert payload media are JSON, newline-delimited JSON, YAML, CSV, Markdown, and plain text.
The kinds are closed to `external-resource`, `provenance`, `agent-trace`, and `regression-test`.

## Bounds and threat model

The existing whole-bundle limits remain:

- 12 MiB ZIP;
- 10 MiB total uncompressed;
- 8 MiB maximum core artifact; and
- 16 archive entries.

The extension adds stricter nested limits: at most eight payloads, at most 1 MiB each, and at most
4 MiB combined. Seven core entries plus one extension manifest plus eight payloads exactly fits the
unchanged 16-entry ceiling.

Report and intake reject undeclared, missing, changed, oversized, forbidden, absolute, traversing,
backslash, non-normalized, encrypted, compressed, symlinked, duplicate, and case-colliding entries.
Recordings, bags, MCAPs, evidence, clips, frames, labels, caches, environments, secrets, models,
weights, checkpoints, archives, and runtime state are forbidden. Intake extracts into a private
directory, validates hashes and contracts, reconstructs the canonical stored ZIP, and requires byte
equality with the accepted upload. It does not import, invoke, or otherwise execute extension
payloads. The deterministic EventSpec/resource runner consumes declared resources during participant detection or trusted organizer replay. It does not execute submitted scripts, traces, or tests.

## Bonus anchors

The three judgment-based bonuses total at most +20:

- grounded agent trace: +10;
- advanced multimodal, data-quality, or external-resource method: +5; and
- regression test derived from a demonstrated failure: +5.

Follow the [extension guide](../extension.md#optional-bonus-evidence) for accepted trace and test evidence. The [scoring reference](scoring.md#point-allocation) defines eligibility and the full point allocation, including the separate Cave bonus.
