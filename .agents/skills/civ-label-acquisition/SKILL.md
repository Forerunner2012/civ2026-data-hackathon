---
name: civ-label-acquisition
description: Use when organizers need to review CIV event candidates from authorized local recordings and export selected practice labels or private truth.
---

# CIV label acquisition

Use this skill for local organizer review of recordings whose permitted use covers the work. EventSpec scans propose candidates. A human reviewer decides what each interval means.

## Required inputs

Before scanning or reopening review, confirm the authorized recording path, its expected SHA-256, the permitted-use statement, the dataset key and source ID, the EventSpec, each referenced resource, and any viewer layout used to interpret evidence. Confirm the human reviewer and the local progress and output paths. Choose participant practice output, organizer-private full truth, or both with separate paths.

Recompute the recording hash before reuse, detection, review, and export. Compare it with the authorized expected SHA-256. Bind review to the exact source, EventSpec, resources, detected events, run manifest, and approved camera-context manifest and product. If any identity is missing or differs, stop and rebuild the run from the authorized source. The review adapter rejects stale progress and input changes.

A label pack does not record EventSpec identity and cannot seed review by itself. Reuse prior review only through progress whose complete bound identity matches. Treat any other reviewed labels as a separate reference, then review the current candidates yourself. Never invent provenance.

## Review and export

From the repository root, run `uv sync` before the project commands. Validate the EventSpec and run its scan against the authorized recording. Then open the local review interface with distinct progress and output paths:

```sh
uv sync
uv run civ detect "EVENTSPEC.yaml" "SOURCE.mcap" --output "RUN"
uv run civ labels review --source "SOURCE.mcap" --spec "EVENTSPEC.yaml" --events "RUN/events.jsonl" --manifest "RUN/run-manifest.json" --dataset kashiwa --source-id SOURCE_ID --progress "LOCAL/review-progress.json" --practice-output "LOCAL/practice-label-pack.json" --organizer-output "LOCAL/source-relative-truth.json"
```

When a permitted camera-context manifest and product match this source and dataset, also pass `--camera-context-manifest APPROVED_CONTEXT.manifest.json`. If no matching context is available, leave the option out and record the explicit missing-context disposition during review.

Use the current dataset key `kashiwa` or `reims` required by the adapter. A key in a synthetic fixture does not identify a real recording or grant permission to use that dataset.

Review every proposal against synchronized signals and any available rights-approved images. Missing context stays explicit. Record an uncertainty disposition and reason when context is missing or the interval remains uncertain. Approve, adjust, reject, or add missed events based on the evidence. Explain each adjustment, rejection, or supported scoring-data-gap exclusion. The adapter clears approval after an interval edit, supports undo, and requires a fresh missed-event signoff after geometry changes. It rejects unsupported exclusion kinds.

Select each practice interval explicitly. Export after the review gate is clear and missed-event review is signed off. Keep organizer-private truth and the full review progress separate from participant output. Export only through `civ labels review`; do not construct or edit consumer documents by hand. Keep reviewer identity and adjustment, rejection, and uncertainty explanations in the local audit when consumer contracts omit them. Keep the progress file and audit out of participant bundles.

The adapter validates practice output against the existing scoring and label-pack contracts. Build and audit organizer-private label packs with the existing consumer:

```sh
uv run -m civ_workshop.label_packs build --truth "LOCAL/source-relative-truth.json" --manifests "SEALED_PRODUCT_MANIFESTS" --output "ORGANIZER_LABEL_PACKS"
uv run -m civ_workshop.label_packs audit ORGANIZER_LABEL_PACKS/label-pack-set.json
```

Stop when an exclusion cannot be represented by the receiving contract. Do not silently omit it or add a new field. Never fetch recordings or labels, use credentials, assign truth automatically, or publish any input, progress, or output.

## Synthetic validation

From the repository root, run:

```sh
uv sync
uv run python .agents/skills/civ-label-acquisition/scripts/synthetic_demo.py
```

The helper creates only synthetic inputs under the operating system temporary directory. It drives the local review service with explicit fixed fixture decisions by `Synthetic reviewer (fixture only)`, checks mismatch and incomplete-review refusals, verifies exact nanoseconds and deterministic practice and private output bytes, and runs the existing practice and private-label consumers. It accepts no recording or label paths, and its fixture decisions are never a production approval path. The output includes a command for opening the generated fixture in a separate human review session.
