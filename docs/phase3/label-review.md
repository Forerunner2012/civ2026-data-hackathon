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
## Check evidence outside proposals

Use the Whole recording panel to inspect exact start and end nanoseconds anywhere within the displayed source bounds. Previous window and Next window move by the current window width. Inspect whole source provides a sampled overview. Inspect smaller windows for signal detail; a sampled trace can omit short changes.

The source overview marks proposals, approved events, rejected proposals, data gaps, and locally checked windows separately. A source with zero proposals still provides evidence navigation. Signal samples and approved camera frames share an integer-safe cursor. Missing context remains explicit.

Mark displayed window checked records a local reviewer note for the window whose evidence was loaded. Notes save and reload with the same bound progress, and interval geometry edits clear them. These notes do not approve an event or provide completeness signoff. Use the displayed window to prefill missed-event boundaries, then refine the boundaries, supply a reason, and review through the existing actions. Sign off whole-recording completeness only after your contextual review.

The window endpoint remains loopback-only and token-protected. It rechecks bound source/spec/resources/run/context identities before reading evidence. Its responses and local checked-window records never enter practice packs or private consumer truth.
## Review a reduced signal product with approved context

When the scored source is a reduced warm-up or development product, also pass
--signal-product-manifest SIGNAL_PRODUCT.mcap.manifest.json with the approved camera-context
manifest. The adapter verifies the physical product, its exact sidecar hash named by the camera
manifest, original parent, source ID, dataset, split and identity timestamp mapping. It never
substitutes a same-name recording.

Progress includes that sidecar identity. Changes invalidate reuse, actions and export. Reviews
against original recordings keep their existing identity and do not need this option. The sealed
label-pack builder remains sealed-only. This option supplies an exact technical binding; it grants
no new imagery rights or human coverage approval.


Explicitly bound warm-up/development signal products support practice export and local review audit,
but the current organizer-private truth contract is sealed-only. The private button is disabled with
an explanation, and direct private export fails before writing a file. Original-recording private
review retains its existing behavior. A prior private output mislabeled as sealed must remain local
and unqualified; do not hand-edit it or feed warm-up/development manifests into the sealed builder.
Existing bound progress and practice packs remain reusable without repeating human decisions.


## Compare independent candidate profiles

For a bound warm-up/development signal product, pass --comparison-inventory LOCAL/profiles.json
alongside the existing source, product-sidecar and approved-context options. The local inventory
names independent EventSpecs and run directories; relative paths resolve beside the inventory:

```json
{"profiles":[{"id":"alternative-v1","spec":"specs/alternative-v1.yaml","run":"runs/alternative-v1"}]}
```

Create each variant as a new EventSpec file, validate it with the existing parser, and run civ detect
into a new directory. Do not reuse an existing output directory: detection can overwrite files.
Keep the baseline, old runs and bound progress unchanged. For a completed review, copy its progress
into a new revision and configure fresh output paths before making new human decisions. Inspection
alone leaves decisions unchanged, but the existing actions save to the configured progress file.
This comparison feature does not scan,
edit profiles, seed approvals or combine events. It refuses sealed or unverified product membership.

The comparison panel shows the declared condition, parsed timing values in nanoseconds, exact
EventSpec text and bound spec/run identities. Alternative proposals occupy a separate timeline row.
Exact interval geometry is paired first, then positive overlaps by descending intersection duration
with deterministic chronological tie breaks. Remaining intervals are added or removed proposals;
paired nonidentical intervals have changed boundaries. This discovery display rule is separate from
the frozen scorer. Counts and agreement do not establish truth or precision/recall/F1.

Select an alternative interval to inspect its evidence and prefill exact missed-event boundaries.
Supply your contextual reason and add it through the existing missed-event action only if confirmed.
The new interval stays pending until reviewed, and geometry changes clear completeness signoff.
The comparison alone does not change any review decision or practice selection.

Inventory, active inputs and every alternative spec/resource/events/manifest identity are frozen
for the session. Changes refuse display and actions before progress is written; reopen with a new
inventory revision or remove the comparison option. Comparison references are not added to progress
identity or consumer exports. To make another profile active, use its own spec/events/manifest and a
new progress/output revision; old progress is rejected by the existing full binding check. Never
tune profiles using sealed labels or sealed feedback.


## Review guidance and required fields

Use `--review-rule "ORGANIZER-APPROVED CONTEXTUAL DEFINITION"` to display the expected event rule
above the review controls. Without it, the panel identifies the existing Kashiwa unprotected-right-turn
or Reims right-or-left-turn scope. The EventSpec proposes candidates; the contextual rule governs
human decisions. A changed target definition requires a new review revision.

Optionally pass `--reviewer "REVIEWER NAME"` to prefill the name. Existing saved reviewer identity
takes precedence. Check the name before recording decisions; the launch hint alone does not
create reviewer audit or approvals. Without a prefill, the required name field receives initial
focus. Missing required names, reasons, boundaries or uncertainty input receive a visible border
and focus, with reduced-motion support.

Candidate buttons keep their decision visible beside an abbreviated ID; the full ID remains
available in the tooltip and accessible name. Pending, approved and rejected states have distinct
colors as well as text. Adjusting an interval still clears its approval and completeness signoff,
but the reason stays editable in the field. Reload restores the last adjustment reason from the
local audit. Reasons remain local and are not added to participant output.

## Organizer-private sealed camera

For local sealed review, `--organizer-camera-manifest` accepts a private `civ.organizer-camera-context/v1` authorization. Also pass `--signal-product-manifest`. This path reads the original recording in place. It checks its hash against the sealed product's parent hash and checks the dataset, source ID, product bytes and manifest. It uses the original camera log timestamps for synchronization and indexed frame access.

```json
{
  "contract": "civ.organizer-camera-context/v1",
  "dataset": "reims",
  "source_id": "SOURCE_ID",
  "source": {"path": "ABSOLUTE_ORIGINAL_RECORDING_PATH", "sha256": "EXPECTED_PARENT_SHA256"},
  "image_topic": "/zed/zed_node/rgb/image_rect_color/compressed",
  "authorization": {
    "authority": "NAMED_AUTHORIZING_ORGANIZER",
    "scope": "organizer-local-review",
    "statement": "Recorded permission for this local review"
  }
}
```

This authorization records organizer access. It does not assert frame-by-frame privacy inspection, permission to distribute imagery or human label approval. Keep the authorization, recording and progress private. Participant camera manifests retain their existing restrictions. The two camera options are mutually exclusive, and organizer-camera sessions refuse participant practice output.

Adding a camera changes review identity. Preserve earlier progress and use a separate progress revision. Human decisions and completeness signoff remain required. Private truth from this sealed path records the verified parent hash and original log timestamps, so the existing label-pack builder can bind it to the historical product manifest. No timestamp conversion or manual truth editing is needed.