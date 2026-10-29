# CIV participant submission workspace

This workspace is deliberately incomplete. It supplies the stable shape, not a detector or answer.

1. Replace every `CIV_TEMPLATE_REPLACE_ME` prompt in `detector/detector.yaml`, `report.md`, and
   `figure.svg` with your own participant-safe work.
2. Complete the five fixed report headings and replace the single figure placeholder.
3. Run `sh reproduce.sh DATASET PRACTICE_LABELS.json NEW_OUTPUT`, or
   `./reproduce.ps1 DATASET PRACTICE_LABELS.json NEW_OUTPUT`, using exact matching practice inputs.
   Use `-` instead of the practice pack when no matching truth is supplied. The script runs
   `civ detect`, `civ clip`, `civ score` and `civ report`, stopping on failure. It copies completed
   authored artifacts and declared extensions into a new output, then rebuilds events, clips,
   metrics, the run manifest and ZIP. An explicit output must not exist. Omitting NEW_OUTPUT
   regenerates this workspace instead. Evidence clips remain local.
4. Compare events, metrics and clip hashes with your original run. Record exact input/resource
   identities, environment versions, the command and any material differences in your report.
   Valid extension declarations are preserved by detection. Finish optional payload declarations
   before this check. Packaging success alone is not proof of reproducibility.
5. Keep the validated `submission.zip` and printed SHA-256 unchanged until organizers confirm
   a collection route. Use the same participant or team identity for any replacement delivery.

A replacement script must include a direct
`civ detect` or `uv run civ detect` line; PowerShell may prefix it with `&`. Static validation
does not recognize wrappers or command variables and does not execute your script.

`events.jsonl` is runner output, not a hand-edited label file. Each line is a normalized
`civ.event/v1` interval in nanoseconds with source and spec hashes. Events are sorted
deterministically; matching samples, merged candidates, and emitted events are different things.

The v2 metadata bundle retains exactly seven core artifacts: one EventSpec, `events.jsonl`,
`run-manifest.json`, `metrics.json`, this report, one top-level figure, and one reproduction entry
point. `civ detect` also stages each EventSpec resource byte-for-byte at its declared contained path.

Optional provenance, grounded agent traces, and participant-authored regression tests go under
`extension/` and must be declared by the sorted `extension/manifest.json`. Intake validates and
stores them but never executes traces or tests. The extension permits at most eight payloads,
1 MiB each and 4 MiB combined. Raw recordings, MCAP evidence clips, frames, labels, caches,
environments, secrets, model weights, and runtime state stay local.
