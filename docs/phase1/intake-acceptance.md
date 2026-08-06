# Phase 1 submission intake acceptance

## Contract

Participants submit the unchanged metadata-only `submission.zip` emitted by `civ report`, together
with their stable participant/team identity and the SHA-256 printed by that command. Evidence clips,
raw bags, organizer labels, caches, virtual environments, and runtime state never enter the bundle.
The published transport limit is 12 MiB per bundle, 8 MiB per artifact, at most 10 MiB total
uncompressed metadata, and at most 16 artifacts. `civ report` enforces the same limits before it
emits the bundle, so intake cannot reject an unchanged successful report on size or shape.

The online form must collect these public fields:

1. stable participant or team identity;
2. pasted SHA-256;
3. the unchanged `submission.zip` upload.

The form provider owns the server receipt timestamp and unique response identifier. Its confirmation
must display the receipt timestamp to the participant. Organizer credentials, response exports, and
Drive internals are not embedded in the attendee site.

## Organizer adapters

Download one form response and its uploaded bundle to the same directory, then create a small JSON
envelope using the provider's response identifier and original server timestamp:

```json
{
  "bundle": "submission.zip",
  "delivery_id": "provider-response-id",
  "identity": "participant-or-team-id",
  "received_at": "2026-09-03T12:20:00+09:00",
  "sha256": "participant-pasted-sha256"
}
```

Import it without changing the bundle:

```powershell
civ intake-form form-response.json --ledger D:\civ-intake
```

For a local or USB receipt, use the identical bundle and record the operator receipt time:

```powershell
civ intake-local submission.zip `
  --ledger D:\civ-intake `
  --identity participant-or-team-id `
  --received-at 2026-09-03T12:20:00+09:00 `
  --sha256 participant-pasted-sha256 `
  --delivery-id usb-receipt-id
```

Both commands return the same `civ.intake-receipt/v1alpha1` confirmation. The ledger retains the
original timestamp and its UTC normalization, stores bundles by content hash, and exposes the last
valid on-time bundle per identity as scorer input. A receipt exactly at 12:30:00 Asia/Tokyo is
on-time; anything later is retained with `status: late` and cannot replace the authoritative entry.
Receipts are committed transactionally in `intake.sqlite3`; verified bundles are published by
content hash through a flushed temporary file and atomic replacement. Intake first copies the
caller-controlled upload into a bounded, intake-owned snapshot, validates that snapshot, and
byte-compares it with a canonical rebuild so unpacked or repacked archives are rejected.

## Automated evidence

- `tests/test_intake.py` passes the same bundle through both adapters and proves identical content
  hash and scorer bytes.
- It proves unlimited resubmission, the inclusive exact cutoff, late quarantine, timestamp
  normalization, mismatched hash rejection, malformed-bundle rejection, duplicate delivery
  diagnostics, and preservation of the earlier authoritative receipt. Additional cases reject
  compressed/oversized/repacked archives before extraction, prove source-path replacement cannot
  alter accepted bytes, and exercise concurrent duplicate imports plus recovery from an interrupted
  bundle copy.
- `handoff-site/tests/live-rendered.test.mjs` proves the configured HTTPS form action, local hash
  instructions, participant-visible confirmation requirement, and USB fallback are rendered. A
  second build without a configured form proves the current USB-only status remains usable, while
  environment variable names, coach credentials, and ledger internals stay out of browser assets.
- `handoff-site/tests/rendered-html.test.mjs` continues to prove the production artifact contains no
  live route, coach control, hidden guidance, or organizer-only content.

## Operator check — required before closing issue #9

This is deliberately not marked complete by local automation. Record the date, operator, configured
form URL, and response identifier in the issue after completing both paths:

1. From a device on public Internet, open `/live`, follow the configured form action, upload a known
   `submission.zip`, paste its `civ report` hash, submit, and retain the visible server timestamp.
2. Export that response, import it with `civ intake-form`, and compare the receipt hash/timestamp with
   the known bundle and provider confirmation.
3. Remove connectivity from the intake laptop, copy the same bundle by USB, import it with
   `civ intake-local`, and confirm the same hash and scorer bytes are retained.
4. Restore connectivity only after the local receipt and authoritative selection have been checked.

Current status: **pending a real configured form URL and operator-owned public-Internet rehearsal**.
This is tracked as an external owner task and does not block publishing the code-complete intake
implementation; issue #9 remains open until the operator evidence is attached.
