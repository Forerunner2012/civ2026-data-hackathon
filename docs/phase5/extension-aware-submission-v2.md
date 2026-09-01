# Extension-aware submission v2

Status: **implemented and agent-verified; organizer wording approval pending**

Recorded: 2026-09-02

## Scope

`civ.submission-bundle/v2` removes the extra-track transport inconsistency without changing the
participant/organizer boundary. The bundle remains metadata-only. It retains the seven core
artifacts and may carry a bounded, declared extension containing exact EventSpec resources,
provenance, grounded agent traces, and participant-authored regression tests.

This change does not activate the reserved EventSpec `detector:` field and never executes submitted
trace or test content at intake. Raw evidence and organizer-only artifacts remain out of scope.

## Contracts and compatibility

The three new closed schemas are:

- `civ.run-manifest/v2`, whose `submission` member references the v2 declaration;
- `civ.submission-bundle/v2`, which retains `civ.reproduction/v1` and optionally hash-binds
  `extension/manifest.json`; and
- `civ.submission-extension/v1`, whose sorted entries contain exactly `kind`, `media_type`, `path`,
  and lowercase `sha256`.

The existing v1 schemas and bytes are unchanged. New `civ detect` runs emit run-manifest v2 and new
`civ report` runs emit submission-bundle v2. Canonical v1 bundles continue through the same form and
local/USB validation, storage, authority selection, and scorer-input path. An authority decision can
therefore compare accepted v1 and v2 deliveries for the same source without converting either ZIP;
the later valid on-time delivery wins and its exact accepted bytes are retained.

Events, EventSpecs, point resources, metrics, and reproduction declarations keep their stable v1
contracts. A v2 run manifest containing v1 normalized events is intentional, not a mixed working
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
payloads. Only the existing deterministic EventSpec/resource runner consumes a submitted resource
during an explicit participant or reproduction `civ detect` run.

## Bonus anchors

The participant page, one-page fallback brief, organizer jury pack, and feedback template use the
same maximum +20 split:

- grounded agent trace: +10;
- advanced multimodal, data-quality, or external-resource method: +5; and
- regression test derived from a demonstrated failure: +5.

The GNSS `resources:` plus `min_distance_to` exercise is the external-resource method. Bonus cannot
rescue a non-reproducing core submission. Every non-zero award cites an artifact in the accepted
bundle. Prompt style and transcript length do not score.

## Implementation inventory

- `schemas/civ.run-manifest.v2.schema.json`
- `schemas/civ.submission-bundle.v2.schema.json`
- `schemas/civ.submission-extension.v1.schema.json`
- `src/civ_workshop/contracts.py`: closed field sets and v1/v2 run consumption
- `src/civ_workshop/submission_extension.py`: paths, kinds, media, hashes, forbidden content, and
  nested bounds
- `src/civ_workshop/detection.py`: exact resource staging and deterministic extension manifest
- `src/civ_workshop/reporting.py`: v2 emission, resource/extension validation, and canonical entries
- `src/civ_workshop/intake.py`: case-collision and ZIP symlink rejection plus v1/v2 canonical intake
- `src/civ_workshop/kit_inventory.py`: all v1 and v2 participant schemas in the offline kit
- participant templates, QuickStart, participant page, fallback brief, organizer pack, and tests

## Verification evidence

The automated evidence covers byte-identical repeated v2 reports, exact resource/provenance/trace/
test bytes, GNSS reproduction from an extracted bundle without restoring its source resource, v1
acceptance, mixed v1/v2 authority, canonical ZIP validation, and the path/hash/size/forbidden/
case-collision failure classes. The full release verification commands are:

```text
uv run pytest
uv run ruff check .
uv run mypy src tests
cd handoff-site
npm test
npm run lint
git diff --check
```

On 2026-09-02, the complete Python test suite passed, Ruff passed, `mypy src tests` passed, all
internal/no-form/public/static-export site tests passed, ESLint passed, and `git diff --check`
reported no whitespace errors. Regenerated assembly, release, workstation, intake, and physical
media identities belong to the external release evidence and are not invented in this contract
note.

## Human gate

An organizer must explicitly approve the three revised bonus anchors and final participant wording.
Agent verification cannot satisfy that decision. Until the approval is recorded, the implementation
is technically complete but the final release go/no-go remains pending.
