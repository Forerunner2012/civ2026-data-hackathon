# Phase 4 submission packaging acceptance

Status: **accepted for participant submission packaging**

Recorded: 2026-08-29

This gate packages the participant-facing submission experience around the stable metadata-only
bundle: a deliberately incomplete workspace, one fixed report template, and the same six outcomes
stated identically on the live page, the public participant view, and the static fallback. It does
not qualify a release candidate. Fresh-machine rehearsal, event-hardware intake, and the final form
freeze remain Phase 5.

The transport, validation, and authority core was already accepted in
[`../phase1/intake-acceptance.md`](../phase1/intake-acceptance.md) and is unchanged here. Phase 4
adds the scaffold, the participant wording, and the tests that hold the wording to the code.
The per-dataset authority described below is the legacy receipt behavior. The track-aware cohort
workflow selects one receipt per identity and track under `civ.evaluation-plan/v1alpha2`; see the
[cohort scoring guide](../organizers/cohort-scoring.md).

## The workspace scaffold

`civ submission-init WORKSPACE --shell powershell|posix` creates one deterministic workspace from
templates packaged inside `civ_workshop`:

```
README.md                 what is submitted, what stays local, what each prompt means
detector/detector.yaml    EventSpec shape with CIV_TEMPLATE_REPLACE_ME topic, field, and value
report.md                 the five fixed headings and exactly one figure reference
figure.svg                a placeholder figure that must be replaced
reproduce.ps1 | .sh       one platform-specific entry point, never both
```

Three properties are load-bearing and each has a test:

- **Deliberately incomplete.** Every substantive value is a `CIV_TEMPLATE_REPLACE_ME` prompt. The
  scaffold supplies the stable shape and never a detector, a threshold, or an answer.
- **Never destructive.** An existing destination is refused before anything is written; the command
  builds into a sibling temporary directory and renames it into place, so a failed run leaves no
  partial workspace.
- **Refused if untouched.** `civ report` rejects a report or figure that still carries the marker,
  so the placeholder cannot reach intake as a submission.

The six template files are tracked in the participant kit inventory by relative path, byte size, and
hash under `templates/submission/`, and appear in the generated `SHA256SUMS` manifest.

## The six outcomes, and what enforces each

The participant view, the live page, and the static fallback state the same six outcomes. Each maps
to one existing code path rather than to prose:

| Outcome | Participant statement | Enforced by |
| --- | --- | --- |
| Accepted | keep the reference, hash, and receipt time | receipt written with `status="on_time"`, bundle stored under its content hash |
| Replaced | a later valid on-time bundle for the same dataset wins | `latest_receipt` selects the newest on-time receipt, ties broken by insertion order |
| Incomplete or invalid | fix the named artifact and rebuild | `unexpected submission artifacts (...)`, and the canonical-bundle comparison that rejects a repacked ZIP |
| Hash mismatch | upload the unchanged ZIP and its printed hash | `pasted sha256 does not match the bundle: expected …` |
| Duplicate reference | the existing receipt stands | unique `delivery_id`, checked before and enforced at insert |
| Late | retained, never replaces an on-time bundle | `status="late"`, returned by `quarantined()`, excluded from `authoritative()` |

**Authority is per identity *and* per dataset.** Participants are told that a later bundle replaces
an earlier one *for the same dataset*, and the ledger holds that line: two on-time receipts for one
identity with different run-manifest source hashes do not produce a silent winner. `authoritative()`
and `scorer_input()` both refuse and route to the organizer `score-batch` product mapping, with both
bundles retained intact. This branch backs the newly published wording and was previously untested;
`tests/test_intake.py::test_authority_is_scoped_per_dataset_rather_than_per_identity` now covers it.

## Both paths carry the same rules

The online form and the disconnected USB path share the bundle validator, the hash check, the
cutoff, and the ledger. The participant instruction is therefore the same three items on both — the
unchanged `submission.zip`, the printed SHA-256, and the same participant or team identity — and the
organizer returns the same hash-and-time receipt either way. The organizer-side `civ intake-local`
procedure is recorded in [`../phase1/intake-acceptance.md`](../phase1/intake-acceptance.md);
`tests/test_intake.py` proves the two adapters retain identical bundle bytes and scorer input.

The static fallback repeats the outcomes and the limits with no script, no coach control, and no
organizer command. The public participant view carries no form URL, no `intake-local`, and no
provider name; that absence is asserted, not assumed.

## Evidence

All gates were run on the working tree recorded by this commit:

- `uv run pytest` — full suite green, including the submission-scaffold and intake suites;
- `uv run ruff check .` and `uv run mypy src tests` — clean;
- `npm test` in `handoff-site` — internal build with a configured form, internal build with the form
  deliberately unset, then the public build; live-state, live-rendered, print-materials, and
  rendered-HTML suites all pass;
- `npm run lint` — clean;
- `git diff --check` — clean;
- `uv build --wheel` — all six templates are present under `civ_workshop/_templates/submission/` in
  the built wheel, so `civ submission-init` works from an installed kit and not only from a source
  checkout.

The rendered-HTML suite asserts the scaffold command, the identity rule, the receipt-time authority
sentence, and all six outcome labels on the participant view, and asserts that `tally.so`,
`SUBMISSION_FORM_URL`, and `intake-local` appear nowhere in it. The live-rendered suite asserts the
same receipt-authority wording on the live page and on the static fallback. No organizer route,
answer key, sealed interval, source path, form secret, or personal data appears in the public
server, client, or static export.

The configured form endpoint was confirmed live and open on 2026-08-29.

## Routed to Phase 5

- The configured form is still the Phase 1 rehearsal form and holds three rehearsal responses.
  Naming it for the event and clearing the rehearsal responses is a release-freeze action, not a
  Phase 4 packaging change, and needs an organizer decision on whether the rehearsal receipts are
  archived or discarded.
- Concurrent intake under the real cohort, the event-hardware USB handoff, and the 12:30 cutoff
  under load remain rehearsal items.
- A human organizer still approves the final participant wording on this surface before release.
