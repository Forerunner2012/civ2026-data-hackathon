# Extension-aware submission v2

> **Historical CIV 2026 record.** The dates, commands, artifact identities and acceptance
> below describe the original event and its recorded scope. Start a current session with the
> [QuickStart](../quickstart.md), [organizer guide](../organizers/README.md) and
> [participant contracts](../reference/participant-contracts.md). See the
> [Phase 1–5 history index](../history/civ-2026.md) for later changes. This record does not grant
> new data rights, platform qualification or public-release approval.

Status: **implemented, agent-verified, and organizer wording approved on 2026-09-02**

Recorded: 2026-09-02

The current [submission archive contract](../reference/submission-archive.md) owns the layout, limits, compatibility, and bonus-evidence boundary. The sections below retain the dated implementation and approval record.

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

The changed participant bytes and universal five-viewer matrix use regenerated inventory and
assembly release identities ending in `participant-kit-v2` and `attendee-kit-v2`; the accepted v1
artifacts are not relabelled.

## Human gate

An organizer must explicitly approve the three revised bonus anchors and final participant wording.
Agent verification did not satisfy that decision. The event owner explicitly approved the fixed
`+10/+5/+5` anchors, final participant wording, universal-viewer architecture, legal risk, and final
go on 2026-09-02 in the issue #54 session. Fresh-host qualification remains separately evidenced;
the approval is not represented as a machine execution record. The event owner subsequently
authorized issue #54 closure and downstream execution without waiting for that separate evidence.
