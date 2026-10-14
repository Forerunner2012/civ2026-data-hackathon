# Submission fields and bundle contract

## Collection fields

The historical participant form is retired from the current participant flow. This repository
publishes no active collection route or intended recipient. Do not send participant information or
a bundle through the old form.

Under the existing intake contract, a future authorized collection form would require a stable
participant or team identity, the exact SHA-256 printed by `civ report`, and the unchanged
`submission.zip`.
These collection values are outside the ZIP and are not part of the bundle schema. This guide does
not create or authorize a collection form.

## Metadata-only bundle

The v2 bundle contract is defined by
[`civ.submission-bundle.v2.schema.json`](../schemas/civ.submission-bundle.v2.schema.json),
[`civ.reproduction.v1.schema.json`](../schemas/civ.reproduction.v1.schema.json),
`civ report`, and the intake validator. A successful `civ report` ZIP contains these seven required
entries. It also includes any resources declared by the EventSpec.

- exactly one EventSpec YAML file under `detector/`;
  - any resources declared by that EventSpec;
- `events.jsonl`;
- `run-manifest.json`;
- `metrics.json`;
- `report.md`;
- one top-level figure referenced by `report.md`;
- exactly one `reproduce.ps1` or `reproduce.sh`.

An extension is optional. When used, its manifest and only its declared, bounded metadata payloads
are included. Bundle limits are 12 MiB compressed, 8 MiB per artifact, 10 MiB total uncompressed,
and 16 artifacts maximum.

Source recordings, evidence clips, sealed truth, credentials, organizer-only artifacts, caches, and
runtime state are not bundle files. The scaffold creates an incomplete workspace; `civ report`
validates and emits the unchanged ZIP. Participant identity and consent are not bundle fields.
