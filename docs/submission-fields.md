# Submission fields and bundle contract

## Collection fields

The historical participant form is retired from the current participant flow. This repository
publishes no active collection route or intended recipient. Do not send participant information or
a bundle through the old form. Keep your validated ZIP and hash locally until organizers confirm the session's collection route.

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

| Artifact | Required in ZIP | Purpose |
| --- | --- | --- |
| `detector/<name>.yaml` or `.yml` | Yes, exactly one | Your EventSpec. |
| `events.jsonl` | Yes | Generated normalized intervals. |
| `run-manifest.json` | Yes | Exact input and artifact identities. |
| `metrics.json` | Yes | Practice scores or explicit `not_evaluated` metrics. |
| `report.md` | Yes | Five completed headings with evidence, exact commands, input/resource identities, environment versions, and material reproduction differences. |
| One top-level figure | Yes | The figure referenced by the report. |
| `reproduce.ps1` or `reproduce.sh` | Yes, exactly one | Your repeatable command recipe. Organizers inspect it without executing submitted scripts. |
| `detector/<resource path>` | When declared by EventSpec | The exact resource bytes at their declared relative path. |
| `extension/manifest.json` and declared payloads | When an extension is used | Hash-bound resources, provenance, or optional bonus evidence. |
| `evidence/<event_id>.mcap` | No | Local evidence clips. |
| `submission.zip` | The delivery itself | Keep this generated archive and its printed SHA-256 unchanged. |

Trace and regression-test payloads are optional bonus evidence, not core reproducibility requirements. Follow the [extension guide](extension.md#optional-bonus-evidence) to declare them.

When extension payloads are present, the ZIP includes their manifest and only the declared, bounded files. Bundle limits are 12 MiB compressed, 8 MiB per artifact, 10 MiB total uncompressed,
and 16 artifacts maximum.

Source recordings, evidence clips, sealed truth, credentials, organizer-only artifacts, caches, and
runtime state are not bundle files. The scaffold creates an incomplete workspace; `civ report`
validates and emits the unchanged ZIP. Participant identity and consent are not bundle fields.
