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
must display the unique response identifier to the participant, so any dispute resolves against the
organizer-held receipt time for that identifier. Organizer credentials, response exports, and
provider internals are not embedded in the attendee site.

## Form provider

The selected provider is **Tally** (`tally.so`), chosen because attendees upload a file without an
account or organizational-domain sign-in. Google Forms and Microsoft Forms both gate file-upload
questions behind a signed-in respondent and are therefore unusable for a BYOD cohort.

One form, three questions plus the upload, mapped to the organizer envelope:

| Contract field | Tally element | Envelope key |
|---|---|---|
| participant or team identity | short answer, required | `identity` |
| pasted SHA-256 | short answer, required, 64-character validation if offered | `sha256` |
| the unchanged bundle | file upload, single `.zip` | `bundle` |
| unique response identifier | `Submission ID` export column | `delivery_id` |
| server receipt timestamp | `Submitted at` export column | `received_at` |

Configuration that the contract depends on:

- Leave every respondent-limiting option off. Unlimited resubmission is contractual, and any
  one-response-per-person setting implies sign-in.
- The per-file upload cap must be at least the published 12 MiB transport limit. If the active plan
  caps lower, either raise the plan or lower the published limit — a rejected in-limit bundle breaks
  the participant contract.
- The thank-you page shows the response identifier. **Tally cannot inject the server receipt time
  into a thank-you page** — it offers only `Submission ID` and `Respondent ID` mentions — so the
  built page shows the submission reference and states that the receipt time held against that
  reference is authoritative. The respondent-confirmation-email fallback is deliberately *not*
  adopted: it would require an email question, pulling participant personal data into scope, while
  the identifier already resolves any dispute against the `Submitted at` export column.
- `SUBMISSION_FORM_URL` is the public form URL, `https://tally.so/r/81Yy1x`, configured in
  `handoff-site/.env` — copy the committed `handoff-site/.env.example`, which carries this value.
  It is participant-visible by design and carries no credentials.

**Timezone hazard.** `civ intake-form` rejects a timestamp without an offset, and the 12:30:00
Asia/Tokyo cutoff is enforced to the second. Establish which zone the export column is in and copy
it across unchanged — write a UTC export as `Z` or `+00:00`. Never append `+09:00` to a UTC value:
that shifts every receipt nine hours earlier and can turn a late submission into an on-time one.

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
   `submission.zip`, paste its `civ report` hash, submit, and retain the visible submission
   reference.
2. Export that response and import it with `civ intake-form`. Confirm the receipt hash matches the
   known bundle, `received_at` matches the `Submitted at` export column with its zone unchanged, and
   `delivery_id` matches the submission reference the confirmation displayed.
3. Remove connectivity from the intake laptop, copy the same bundle by USB, import it with
   `civ intake-local`, and confirm the same hash and scorer bytes are retained.
4. Restore connectivity only after the local receipt and authoritative selection have been checked.

Current status: **form built and published at `https://tally.so/r/81Yy1x`; pending the operator-owned
public-Internet rehearsal**. As built: identity short answer (200-character maximum), SHA-256 short
answer pinned to exactly 64 characters, single `.zip` upload capped at 20 MB, all three required, no
respondent limit, no unique-submission key, no password, no partial-response capture, and no
scheduled close — a post-cutoff submission is still recorded so it can be retained as `late`.
This is tracked as an external owner task and does not block publishing the code-complete intake
implementation; issue #9 remains open until the operator evidence is attached.
