# CIV participant submission workspace

This workspace is deliberately incomplete. It supplies the stable shape, not a detector or answer.

1. Replace every `CIV_TEMPLATE_REPLACE_ME` prompt in `detector/detector.yaml`, `report.md`, and
   `figure.svg` with your own participant-safe work.
2. Run your selected `reproduce.ps1 DATASET` or `./reproduce.sh DATASET` entry point. It invokes
   `civ detect` and rebuilds the normalized `events.jsonl` and `run-manifest.json` in this directory.
3. Run `civ clip events.jsonl DATASET`, then the supplied development `civ score` path. These update
   the manifest and create `metrics.json`; evidence clips remain under `evidence/` on your machine.
4. Complete the five fixed report headings and replace the single figure placeholder.
5. Run `civ report .`. Submit only the unchanged `submission.zip`, the printed SHA-256, and the same
   participant or team identity you used for earlier submissions.

`events.jsonl` is runner output, not a hand-edited label file. Each line is a normalized
`civ.event/v1` interval in nanoseconds with source and spec hashes. Events are sorted
deterministically; matching samples, merged candidates, and emitted events are different things.

The metadata bundle contains exactly one EventSpec, `events.jsonl`, `run-manifest.json`,
`metrics.json`, this report, one top-level figure, and one reproduction entry point. Raw recordings,
MCAP evidence clips, labels, caches, environments, and runtime state stay local.
