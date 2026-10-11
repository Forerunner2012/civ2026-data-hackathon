# Local organizer label review

civ labels review opens a loopback-only browser review for one stable civ detect run. It reads the
source, EventSpec, event records, and run manifest as a bound set. It can show EventSpec signal
samples and camera frames only when an approved camera-context manifest matches the same source.

```sh
uv run civ labels review \
  --source SOURCE.mcap \
  --spec EVENTSPEC.yaml \
  --events RUN/events.jsonl \
  --manifest RUN/run-manifest.json \
  --dataset kashiwa \
  --source-id SOURCE_ID \
  --progress LOCAL/review-progress.json \
  --practice-output LOCAL/practice-label-pack.json \
  --organizer-output LOCAL/source-relative-truth.json \
  --camera-context-manifest APPROVED_CONTEXT.manifest.json
```

The camera-context option is optional. Keep progress and outputs in organizer-controlled local
storage outside participant bundles. Press Ctrl+C in the terminal to stop the local server.

Review every detected proposal, adjust exact integer nanosecond boundaries, reject non-events, and
add missed events. Adjustments, rejections, and scoring data-gap exclusions require reasons. A
missing signal or camera context is shown explicitly and needs a human uncertainty disposition.
Only an explicitly selected scoring data gap can be excluded; other exclusion kinds fail. Any
interval edit or missed-event addition clears the full-recording signoff.

Progress autosaves locally and can be reloaded. A progress file is reusable only with the same
source, EventSpec, referenced resources, detected events, run manifest, and camera-context
identities. On initial load, reload, each action (including edits and undo), gate checks, and
export, interval context is refreshed from evidence bound to the source, EventSpec, and approved
camera context; stored context fields cannot authorize a review decision. Label packs do not record
an EventSpec hash, so they cannot safely seed a review on their own.

Practice and organizer-private exports are separate buttons. Practice export requires explicit
per-interval selection and contains only selected intervals in the existing label-pack contract.
Selected scoring data-gap reasons are included because the contract requires them; reviewer
identity, adjustment and rejection audit details, images, and local paths stay in local progress.
Organizer truth uses the existing source-relative truth input expected by the label-pack builder:

```sh
uv run -m civ_workshop.label_packs build \
  --truth LOCAL/source-relative-truth.json \
  --manifests SEALED_PRODUCT_MANIFESTS \
  --output ORGANIZER_LABEL_PACKS
uv run -m civ_workshop.label_packs audit ORGANIZER_LABEL_PACKS/label-pack-set.json
```

Practice packs contain only explicitly selected intervals, and the label-pack contract has no
partial-coverage field. The scorer evaluates every prediction except those overlapping a genuine
supported data gap, so a valid event omitted from a pack can score as a false positive. Practice
self-evaluation uses complete reviewed event coverage for its designated source or chunk: review and
include all relevant events for that exact scoring input before treating precision, recall, or F1 as
complete-reference results. A small illustrative subset cannot substantiate full-run performance.
Data-gap exclusions represent genuine supported gaps and must not be used to suppress omitted valid
events.

The local progress file is the complete review audit. Never put it in a participant bundle or
submit it as participant work.

## Catalog historical inputs

Before reopening a review, declare each local artifact and its expected SHA-256 in an organizer-only inventory:

```json
{"artifacts":[{"id":"development-reference","kind":"consumer-pack","path":"reference.json","sha256":"EXPECTED_SHA256"}]}
```

Run `uv run civ labels catalog --inventory LOCAL/inventory.json`. Relative artifact paths resolve beside the inventory. The command reads only declared files and prints a deterministic local report. Save the report outside Git and participant bundles; it includes organizer paths.

Supported kinds are `recording`, `product-manifest`, `eventspec`, `run-manifest`, `consumer-pack`, `review-progress`, and `approval`. Approval currently means the historical private development-authority contract. Unsupported approval formats fail explicitly. Missing files, byte mismatches and wrong artifact types appear as errors, and the command exits unsuccessfully. Duplicate bytes are reported without inventing a new artifact identity.

Identity verification proves matching bytes and the declared artifact type. It does not qualify product semantics or full review bindings. A consumer pack remains a reference. Progress must pass the existing review adapter's complete source/spec/resources/run/context check. Historical development approval remains private and excludes sealed authority. Its approved aggregate digest stays unverified until its original canonicalization procedure is recovered and applied separately. The catalog never seeds approvals or writes truth.
