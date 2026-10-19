# Phase 1 submission intake acceptance

> Historical acceptance record. The participant form and USB intake route described here are
> retired; there is no current collection route or intended recipient. Use
> [the submission fields and bundle contract](../submission-fields.md) for the current bundle
> definition and retired-field reference.

> Phase 3 preserves these adapters and bundle bytes but selects authority per identity and derived
> dataset. See [two-dataset authority](../phase3/two-dataset-authority.md).

## Contract

The historical form requested the unchanged metadata-only `submission.zip` emitted by `civ report`,
the participant or team identity, and the SHA-256 printed by that command. Evidence clips,
raw bags, organizer labels, caches, virtual environments, and runtime state never enter the bundle.
The published transport limit is 12 MiB per bundle, 8 MiB per artifact, at most 10 MiB total
uncompressed metadata, and at most 16 artifacts. `civ report` enforces the same limits before it
emits the bundle, so intake cannot reject an unchanged successful report on size or shape.

The retired online form collected these three required participant fields:

1. stable participant or team identity;
2. pasted SHA-256;
3. the unchanged `submission.zip` upload.

The form provider owns the server receipt timestamp and unique response identifier. Its confirmation
must display the unique response identifier to the participant, so any dispute resolves against the
organizer-held receipt time for that identifier. Organizer credentials, response exports, and
provider internals are not embedded in the attendee site.

## Form provider

The historical provider was **Tally** (`tally.so`), chosen because attendees could upload a file
without an account or organizational-domain sign-in. Google Forms and Microsoft Forms both gate
file-upload questions behind a signed-in respondent and were therefore unusable for a BYOD cohort.

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
- `SUBMISSION_FORM_URL` configured the retired route at the time of acceptance. The public route is
  not part of current participant guidance; its value has been removed from `.env.example`.

**Timezone hazard.** `civ intake-tally` treats Tally's timezone-naive `Submitted at` value as UTC,
while `civ intake-form` rejects a timestamp without an offset. The 12:30:00 Asia/Tokyo cutoff is
enforced to the second. Never append `+09:00` to a UTC value: that shifts every receipt nine hours
earlier and can turn a late submission into an on-time one.

## Organizer adapters

For adapter reuse, the commands below use POSIX shell syntax. Replace `/srv/civ-intake` with your
organizer-owned ledger directory outside the repository. The historical collection route remains retired.

The normal Tally path is a manually exported submissions CSV. `civ intake-tally` reads the exact
UTF-8 CSV export, treats its timezone-naive `Submitted at` value as UTC, downloads each row's own
signed upload URL, verifies the participant-provided SHA-256 and unchanged `submission.zip`, and
passes the bytes through the same online intake ledger. Tally's aggregate batch-download ZIP is
retained only as operator backup; its renamed member order is not an authoritative row-to-upload
association.

```sh
civ intake-tally tally-submissions.csv --ledger /srv/civ-intake
```

The adapter requires these export columns exactly: `Submission ID`, `Respondent ID`, `Submitted at`,
`Participant or team identity`, `SHA-256 printed by civ report`, and `Your submission.zip`. It emits
a deterministic `civ.tally-import-summary/v1alpha1` JSON summary with one terminal outcome per row.
Rows that fail validation, download, hash verification or bundle validation do not stop later rows;
rerunning an identical delivery reports `already_imported`, while a conflicting duplicate delivery
identifier is terminal `invalid`. The manually supplied export is bounded to 5 MiB and 1,000 rows,
well above the 30-participant event scope.

If a CSV export is unavailable or a provider-specific recovery is needed, download one form response
and its uploaded bundle to the same directory, then create a small provider-neutral JSON envelope:

```json
{
  "bundle": "submission.zip",
  "delivery_id": "provider-response-id",
  "identity": "participant-or-team-id",
  "received_at": "2026-09-03T12:20:00+09:00",
  "sha256": "participant-pasted-sha256"
}
```

Import the recovery envelope without changing the bundle:

```sh
civ intake-form form-response.json --ledger /srv/civ-intake
```

`intake-form` is deliberately provider-neutral/manual recovery; it is not the normal Tally import
path. `intake-local` remains the disconnected USB fallback:

For a local or USB receipt, use the identical bundle and record the operator receipt time:

```sh
civ intake-local submission.zip \
  --ledger /srv/civ-intake \
  --identity participant-or-team-id \
  --received-at 2026-09-03T12:20:00+09:00 \
  --sha256 participant-pasted-sha256 \
  --delivery-id usb-receipt-id
```

All adapters return the same `civ.intake-receipt/v1alpha1` confirmation (the CSV adapter wraps its
row receipts in a versioned summary). The ledger retains the
original timestamp and its UTC normalization, stores bundles by content hash, and exposes the last
valid on-time bundle per identity as scorer input. A receipt exactly at 12:30:00 Asia/Tokyo is
on-time; anything later is retained with `status: late` and cannot replace the authoritative entry.
Receipts are committed transactionally in `intake.sqlite3`; verified bundles are published by
content hash through a flushed temporary file and atomic replacement. Intake first copies the
caller-controlled upload into a bounded, intake-owned snapshot, validates that snapshot, and
byte-compares it with a canonical rebuild so unpacked or repacked archives are rejected.

## Automated evidence

- `tests/test_intake.py` passes the same bundle through the online and USB adapters and proves
  identical content hash and scorer bytes.
- `tests/test_tally.py` exercises the BOM CSV export, row-specific signed uploads, UTC normalization,
  row isolation, repeated identical bundles, idempotent reruns, conflicting delivery identifiers,
  hash/download failures and redaction of signed URLs from diagnostics.
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

## Operator check — completed for issue #9

This is deliberately not marked complete by local automation. Record the date, operator, configured
form URL, and response identifier in the issue after completing both paths:

1. From a device on public Internet, open `/live`, follow the configured form action, upload a known
   `submission.zip`, paste its `civ report` hash, submit, and retain the visible submission
   reference.
2. Export the submissions CSV and import it with `civ intake-tally`. Confirm the row receipt hash
   matches the known bundle, the normalized `received_at` reflects the UTC `Submitted at` export
   value, and `delivery_id` matches the submission reference the confirmation displayed. If the CSV
   path is unavailable, use the provider-neutral `civ intake-form` recovery envelope.
3. Remove connectivity from the intake laptop, copy the same bundle by USB, import it with
   `civ intake-local`, and confirm the same hash and scorer bytes are retained.
4. Restore connectivity only after the local receipt and authoritative selection have been checked.

Current status: **completed on 2026-08-22 and recorded in issue #9**. The online receipt
`kbvZNW6` and disconnected USB receipt `issue9-usb-corrected-001` both retained bundle SHA-256
`31f4eb3ad1cc3c003e0dc5474dad52d7a08ece183a095b3ef0a50c1e5588ca9c`; the USB rehearsal also
confirmed byte-identical scorer input. The route described in this record is retired.
