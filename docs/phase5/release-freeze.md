# Phase 5 release freeze

> Universal-viewer addendum (2026-09-02): the extension-aware participant bytes and five-viewer
> kit use attendee-kit identity `civ-2026-phase5-camera-context-attendee-kit-v2` and release-freeze
> identity `civ-2026-phase5-camera-context-release-freeze-v2`. The v1 evidence below remains an
> immutable historical acceptance record; it is not relabelled as the universal release.

Status: **accepted — deterministic global-risk release freeze verified offline**

Recorded: 2026-08-30 · Operator: Codex on the organizer workstation

This record tracks issue #48, the first Phase 5 gate. It freezes the accepted Phase 4 identities,
prepares deterministic SBOM and source evidence, and records the exact decisions still required
before an attendee release can be declared. Generated SBOMs, source archives, binaries, datasets,
approval documents, and release payloads remain outside git. This record contains only hashes,
aggregate counts, upstream identities, and redacted consequences.

The release freeze was accepted on 2026-09-01. The event owner approved the architecture and exact private
development-scoring authority on 2026-08-30. After reviewing the package inventory, the event owner
accepted the exact frozen SBOM set globally on 2026-09-01 because the event date is close. This is
recorded as risk acceptance, not as 2,135 package-level legal conclusions: every unresolved and
`NOASSERTION` fact remains visible in `civ.release-freeze/v1`.

## Accepted Phase 4 boundary

| Input | Frozen identity |
|---|---|
| Tool source | `bc0cb9cfb98b92665626a5b64c9a65571e80aaf2` |
| Participant inventory | `aee496467d4537acca417d3481e8cec81c0e8db4e945fd10b3aac7dfb56c27bf` |
| Exact assembly | `b661d18791f6d6a640ae35c595fc9b8a5ecccba94a451122977df831c6c2f097` |
| Candidate image | `sha256:47f4017351802e878ff138c9e3aead0161de660914e79c252554968a91657560` |
| Image archive | 464,562,688 bytes; `ff983defaa02671982ee78dbf13026d0d007c5c16082cd898658228875f289db` |

The release contract pins these values rather than accepting caller-supplied replacements. The
Phase 3 recovery caveat also remains mandatory: two Kashiwa products are structurally readable,
but recovery cannot prove that truncation lost no records. Corrupt-parent locations remain private.

The stricter Phase 5 path reopened and hashed both independently assembled copies of the real
accepted 3,225-file candidate on 2026-08-30. Each audit returned 1,307,178,032 required bytes and
manifest SHA-256 `b661d18791f6d6a640ae35c595fc9b8a5ecccba94a451122977df831c6c2f097`.
The release tooling derives a canonical set identity from each component's sorted file SHA-256 and
relative target, rather than trusting only the aggregate component byte count:

| Component | Role / platform | Files | Bytes | Canonical set SHA-256 |
|---|---|---:|---:|---|
| `container` | participant runtime image / linux-amd64 | 1 | 464,562,688 | `968c100177c466f77af46682ab91aec3f8e5b5dd3e26a882708dbfa1c25e444c` |
| `participant-kit.json` | participant inventory / all | 1 | 11,312 | `28be9fc4dcd7eda1b719db01a9574240f692eafba317cbc304884a54ac146dce` |
| `viewer` | offline viewers / windows-amd64 | 2 | 384,075,378 | `9cdc76148c8df7e42a0198950b0869010015f2b5ec1bd3d3af66c066b64e68e0` |
| `layouts` | viewer layouts / all | 4 | 12,256 | `b7cb2af3c606db84b895bc3ee7eb2eae3aaca6afe51dad0d2c9bd6b940943669` |
| `site` | public static site / all | 24 | 523,146 | `315896941d53bb3ac5323ce1712a88052dbe7153cfdc73bee0ac3e5650412d5c` |
| `fallback` | offline fallback / all | 22 | 39,133,570 | `615413c48e1117b868c56ae5ca17eeeedcfb030ee5d657cc2d42858fe6cc5127` |
| `templates` | submission templates / all | 6 | 3,887 | `47253d6f4338e8bce002ac711dda496e6f5ad3631b219db553e05f175b53f169` |
| `offline` | offline dependencies / windows-amd64 | 3,092 | 83,416,684 | `c266e6ca77fba720ab7ef71edf0830e2f788a6d15dbd12b2d136a58bd2e1326a` |
| `runtime` | participant runtime source / all | 26 | 223,055 | `2c0ef8d81e6a863c3e22a6f04f0eb87dcb1e95d32896ef205136ca743562591c` |

The release manifest also records the remaining attribution, instructions, integrity, data,
documentation, examples, and schema components. Every component provenance points to the accepted
Phase 4 assembly hash.

## Deterministic release tooling

`civ_workshop.release_freeze` provides seven organizer-only operations:

- `normalize-spdx` replaces scanner time, namespace, document-name, and ordering variation with a
  canonical SPDX 2.3 representation tied to the exact subject hash;
- `legal-template` joins the two normalized SBOM package sets into a closed, package-by-package
  review template and matching notice draft;
- `accept-global-risk` applies one explicit human authority identity to the exact frozen inventory,
  marks records `risk-accepted`, and preserves unresolved and `NOASSERTION` counts;
- `render-notices` regenerates notices only from a completed review and rejects pending or
  structurally inconsistent records;
- `legal-approval` derives a concise approval bound to the exact review, notices, licence evidence,
  source archives, reviewer authority, date, and decision source;
- `build` derives role/platform/provenance identities for all 16 participant components, requires
  exact Phase 4 inputs, frozen artifact bytes, and explicit human approvals. Strict mode still
  requires zero unresolved packages and corresponding source for every detected copyleft-family
  entry; global-risk mode preserves those uncertainties and binds the aggregate acceptance;
  and
- `audit` rehashes every artifact and approval, revalidates the legal review and exact Phase 4
  assembly identity, rejects absolute host paths, and checks the deterministic `SHA256SUMS` file.

The participant-runtime boundary explicitly excludes this module. The stable manifest schema is
`schemas/civ.release-freeze.v1.schema.json`; the contract has no compatibility path or permissive
unknown fields.

## Accepted final freeze

The organizer-only declaration is 3,994 bytes with SHA-256
`29567f16ece5228d4c2a1bf51bda911e4cf883fd7d3947e21ec514d8fecb0757`. Two independent real
builds used the two accepted Phase 4 assembly copies and produced byte-identical manifests and
checksum files:

| Output | Accepted identity |
|---|---|
| `release-freeze.json` | `2003cc25fc24d57a56e84a50ff8a3d06ec6a7ab16cd95b78e2933dd27b91bf0f` |
| `SHA256SUMS` | `44d5db903aea6b59db60c0b943e19ce7da1d2f6cda2ebf8b3d95bd4e2c1644ce` |
| Frozen artifacts | 19 |
| Frozen packages | 2,135 |
| Required disk bytes | 1,365,132,227 |

A fresh `uv --offline` audit rehashed the accepted assembly and every declared approval, review,
notice, licence, SBOM, and source artifact and returned `valid: true` with the same manifest hash.

The tests prove that two scanner outputs with different timestamps, namespaces, input document
names, and package order normalize to identical bytes. They also prove byte-identical independent
release builds, closed top-level fields, mutation detection, rejection of an unfrozen approval,
rejection of any pending legal package, rejection of missing participant components, rejection of
a legal approval that binds a different review, and preservation of unresolved scanner facts under
explicit global risk acceptance.

## Machine evidence prepared outside git

Docker Scout scanned the previously verified exact local image and emitted SPDX 2.3. npm generated
the public site's complete lockfile SPDX set. The repository normalizer then made both outputs
deterministic using the accepted source commit time.

| Subject | Packages | Bytes | Normalized SHA-256 |
|---|---:|---:|---|
| linux-amd64 container | 1,517 | 5,380,878 | `9db0682a5b1a1d741c017260c2f358b7f131a62ac05831ca52d67af8f1114f6d` |
| Public static site | 618 | 589,168 | `92568845ad31558a427274b8863767c828c82ec92546872fb1ffbea55f238207` |

The complete static-site subject contains 24 files and has canonical set hash
`8ec1b4c2c1179da48528b10e337c9e6968b3300f245bbc7ee05fdfb0bd958fea`.
The conservative full lockfile SBOM is authoritative because npm's `--omit=dev` result contained
only two packages and omitted shipped framework dependencies.

The generated review covers 2,135 package records. Of those, 1,098 have scanner licence value
`NOASSERTION`, and 322 expressions contain a detected copyleft-family identifier. These remain
inventory facts, not package-level legal conclusions. The active 1,520,170-byte review is in
`global-risk-acceptance` mode with SHA-256
`e8d7ecd92dd405b72e281fcb3722fd4f2d8d60dde8d11eef1ed6688eac94cb5e`.
Its 973,810-byte notices have SHA-256
`adc2b9654dd4dcdeff3a68de04e74533659fd97b158f2dc467edc170071a5c15`.
The original pending review and notice draft remain archived under their previous exact hashes.

Both Windows viewer installers were also opened as archives without executing them. Docker Scout
found one package in the extracted PlotJuggler tree and none in the extracted Lichtblick tree, so
these viewer scans are retained only as evidence of scanner limits; they are not complete SBOMs for
native DLLs or Electron's packed application.

## Exact source and licence evidence prepared outside git

| Subject | Exact upstream revision | Archive SHA-256 |
|---|---|---|
| Workshop repository | `bc0cb9cfb98b92665626a5b64c9a65571e80aaf2` | `ca5484cea9596fca966aaef8ed5e49713674954bbada53492f85b48c3c5c8a16` |
| PlotJuggler 3.999.3 | `4dc16a13439010e9d101923886b21571e8c85d97` | `30a6d590ec42d5bf2f82449a18e6e7c78255ae8c47e61549a360875ce78da0e4` |
| Lichtblick 1.28.0 | `ffc9b201db62f6a651128b4faf4e9f5112a2d34c` | `3246cc96976d1e0b606d680b81cd356e3d78fec3da6308a8e288bc8fb418ffcf` |
| uv 0.11.2 | `02036a8ba599677fa4c5e2f24dad1c516735fbad` | `cb9cd91203ef85486f4875092c0a4e35970628d44b8c6b94c146a768b38d2e88` |

The exact upstream PlotJuggler, Lichtblick, and uv licence texts are archived by hash. Lichtblick's
bundled Electron and Chromium notice files were extracted directly from the exact Windows binary;
their hashes are `5154e165bd6c2cc0cfbcd8916498c7abab0497923bafcd5cb07673fe8480087d`
and `2a01c08497036d18d7e21e6735f3bf019b63fcc47e09208cee43b41df65f5868`.
The PlotJuggler binary exposed only pip 24.2's licence and vendor list, with hashes
`634300a669d49aeae65b12c6c48c924c51a4cdf3d1ff086dc3456dc8bcaa2104` and
`3f135ac71924a416b0e73393b03a47118fb311a1e38240e0cab4b13aec60f27c`;
no general bundled Qt, FFmpeg, Python, or PlotJuggler notice was found by filename inspection.
Upstream tool pages remain the computer-agnostic, recommended connected route; the
checksum-pinned desktop binaries remain offline recovery artifacts:

- PlotJuggler source and licence: <https://github.com/PlotJuggler/PlotJuggler>
- Lichtblick source and licence: <https://github.com/lichtblick-suite/lichtblick>
- Lichtblick 1.28.0 release: <https://github.com/lichtblick-suite/lichtblick/releases/tag/v1.28.0>
- Lichtblick no-install web application: <https://lichtblick-suite.github.io/lichtblick/>
- uv source and licences: <https://github.com/astral-sh/uv>
- Docker Scout SBOM command: <https://docs.docker.com/reference/cli/docker/scout/sbom/>

These archives are evidence for human review, not an agent-issued legal approval or assurance that
every binary redistribution obligation is complete.

## Human legal completion procedure

Two explicit modes are supported. `package-reviewed` remains the strict route: every package is
concluded, every `NOASSERTION` is replaced, source obligations are attached, and
`unresolved_count` reaches zero. For this time-bounded event release, the event owner selected
`global-risk-acceptance` instead:

1. bind the exact two normalized SBOMs and all 2,135 package identities without changing scanner
   facts;
2. mark every record `risk-accepted`, preserve all 2,135 unresolved records and 1,098
   `NOASSERTION` values, and retain the four available exact source archives;
3. regenerate notices from that exact review;
4. generate a separate `civ.release-legal-approval/v1` document identifying the event owner,
   approval date, decision source, accepted unresolved count, and exact review/notices/licence/source
   hashes; and
5. declare that approval target, then run two independent `build` operations and a fresh `audit`.

The approval is deliberately separate and created last. This avoids a circular hash in which the
review refers to the approval document while that document tries to approve the review.

## Private development-scoring candidate

The final Phase 3 calibration profile identifies an organizer-only development set with these
redacted properties:

| Property | Value |
|---|---|
| Files | 12: 7 Kashiwa and 5 Reims |
| Labels | 24: 18 Kashiwa and 6 Reims |
| Recorded data gaps | 1 |
| Canonical private set SHA-256 | `08a7bce5b2e3029ad5e8c12da395118443fd62850e99a8f7c4a329b5f3f2da02` |

The release declaration fixes `participant_distribution` and `sealed_authority_included` to
`false`. No interval, organizer path, sealed identity, or scoring operation appears here or in the
participant assembly. The event owner approved this exact identity for development scoring on
2026-08-30. The frozen approval document is 662 bytes with SHA-256
`7ab22e3ce3b54f8714c5449241614bb4935f6bacc9d555da8077d5d30012bbd6`.

## Decision status

| Gate | Current evidence | Required decision |
|---|---|---|
| Event architecture | APPROVED: Windows-amd64 participant hosts/viewers with the pinned linux-amd64 container under a WSL2-compatible runtime. Linux remains a potential upstream-link route, not advertised offline support. | Approval document: 1,021 bytes; `98041dc50f796e33c560ffb2d9b2d99b0f0274fb137445e42effc52e46c6ca12`. |
| Development authority | APPROVED: exact 24-label private set; participant distribution and sealed authority remain excluded. | Approval document: 662 bytes; `7ab22e3ce3b54f8714c5449241614bb4935f6bacc9d555da8077d5d30012bbd6`. |
| Legal package review | RISK ACCEPTED: Matthieu Carré, event owner, formally accepted the exact 2,135-package SBOM inventory globally while preserving 2,135 unresolved records and 1,098 `NOASSERTION` values. | Approval document: 2,624 bytes; `07068b0924c89558b4e90b4faade5241ca8b54bfebbe7c618b9788e4b1af5468`. |
| PlotJuggler bundled notices | RISK ACCEPTED: exact upstream source/licence plus the installer-exposed pip evidence are archived; broader bundled native notice coverage remains uncertain and recorded. | Included in the global event-owner risk statement; no package-level legal conclusion is asserted. |

The approved architecture matches the accepted physical candidate: a Windows-amd64 host,
Windows-amd64 viewers, and the pinned linux-amd64 container runtime. Official upstream links remain
the recommended connected/security route. Because the accepted offline assembly already contains
the two desktop binaries, replacing them with links would change attendee bytes and reopen Phase 4;
their hashes and redistribution review therefore remain part of this freeze.

## Failure and intervention log

| # | Step | What happened | Resolution and consequence |
|---|---|---|---|
| 1 | Container SBOM | Docker Scout indexed the Windows archive path but could not parse that archive URL. | Scanned the previously verified local image with the exact accepted image ID; SPDX output completed. |
| 2 | Container SBOM cleanup | Docker Scout warned that one temporary file remained in use after a successful scan. | Preserved and normalized the complete SPDX output; no release payload depended on the temporary path. |
| 3 | Site SBOM | npm `--omit=dev` reported only two packages and omitted shipped framework packages. | Selected the conservative full 618-package lockfile SPDX set. |
| 4 | SPDX determinism | Raw scanner timestamps, namespaces, and document names differed between runs. | Added normalization; the first test also caught an input-dependent document name, which was then fixed. |
| 5 | Source archive | The first PowerShell `git archive` invocation passed an output expression literally. | Repeated with an explicit target; two independent repository archives were byte-identical. |
| 6 | Development aggregate | The first diagnostic read an obsolete interval field. | Recomputed from the label records: 24 labels across 12 files with one declared data gap. |
| 7 | Viewer notices | A request to execute the PlotJuggler installer with `--help` was rejected because installer side effects were not bounded. | No execution occurred. Both viewer installers were instead read as archives; Lichtblick notices were recovered, but PlotJuggler's broader bundled dependency notices remain unresolved. |
| 8 | Repository gates | The user uv cache was malformed; the first local fallback cache was also unreadable, and sandboxed uv could not read its managed interpreter. | Used a fresh repository cache with approved managed-Python access; the focused and full Python gates passed. |
| 9 | Site gate | The first sandboxed site test could not write Vite's temporary config under `node_modules`. | Reran with approved host access; the 11 internal, 8 no-form, and 17 public/accessibility tests plus ESLint passed without a product change. |
| 10 | Component provenance | The first release shape pinned only the aggregate Phase 4 assembly identity. | Added and tested 16 derived component identities with role, platform, files, bytes, canonical set hash, and exact assembly provenance; the real assembly passed the stricter audit. |
| 11 | Legal approval identity | The first draft made the review contain the approval-document hash, creating a circular identity for any approval that also bound the review. | Split the approval into a final separate artifact that binds the completed review, notices, licences, and sources without a cycle; regenerated the unapproved drafts. |
| 12 | Resumed integrity gate | The compacted session began after the real-assembly audit was interrupted by a prior tool usage limit; the sandbox also could not see uv's managed interpreter. | Re-ran read-only audits with approved interpreter access against both accepted assembly copies; both returned the exact accepted 3,225-file, 1,307,178,032-byte identity. |
| 13 | Package-review scale | Manual approval of 2,135 low-level SBOM records was not proportionate to the remaining event schedule. | Added an explicit global-risk mode selected by the event owner. It preserves every unresolved scanner fact, binds all exact evidence, and does not misstate aggregate acceptance as package-level legal conclusions. |
| 14 | Final verification scope | The original criterion requested another full repository/site run after the legal-mode change, while the event date is close. | The event owner explicitly selected minimum verification: the earlier full gates remain recorded, and the final change passed 8 focused Phase 5 tests, Ruff, strict mypy, `git diff --check`, two real builds, and the offline audit. |

No retry silently relaxed an acceptance criterion or changed participant bytes. The legal criterion
change is an explicit, attributable event-owner risk decision.

## Current criterion table

| # | Criterion | Result | Evidence or blocker |
|---|---|---|---|
| 1 | Deterministic closed release manifest and schema pin the complete release boundary | ACCEPTED | Exact identities, all 16 participant components, 19 evidence artifacts, and the final manifest are frozen. |
| 2 | Accepted assembly/image reopen; two builds match; mutation and missing/extra bytes fail | ACCEPTED | Both accepted assemblies reopened; two real manifests and checksum files are byte-identical; mutation tests pass. |
| 3 | Runtime/site SBOMs and complete notice/source obligations | RISK ACCEPTED | Exact machine evidence, eight licence artifacts, four source archives, and regenerated notices are bound; package-level uncertainty remains explicit. |
| 4 | Explicit human legal/notices/source approval | READY | Event-owner global risk approval is exact and attributable; it accepts 2,135 unresolved records rather than falsely concluding them. |
| 5 | Architecture tied to actual event hardware | READY | Event owner approved Windows-amd64 hosts/viewers plus the pinned linux-amd64 container; native Linux remains unadvertised. |
| 6 | Private development-scoring input frozen without sealed leakage | READY | Event owner approved the exact set; sealed authority and participant distribution remain false. |
| 7 | Fresh offline real-candidate audit and redacted aggregate | ACCEPTED | Explicitly offline audit returned `valid: true` for 19 artifacts and the accepted manifest. |
| 8 | Repository/site/leakage gates and accepted record | ACCEPTED WITH RECORDED SCOPE | Earlier full gates pass; final minimum verification passed 8 focused tests, Ruff, strict mypy, diff checks, deterministic builds, and offline audit. |

Issue #48 is ready to close. Downstream issue #49 can be unblocked using the accepted manifest and
the explicit global-risk and minimum-verification consequences recorded above.

## Camera-context release profile (v2)

The camera-context companion kits (issue tracked separately from #48) add a 27-file, 5,424,077,234-byte
`context` participant component — 13 camera-context MCAPs, 13 sidecar manifests, and one
`context/camera-context-products.json` set manifest — to a new attendee-kit assembly,
`civ-2026-phase5-camera-context-attendee-kit-v1` at source commit
`4d4983fe0be65473f6a89e8b5bf51263ebdd1cff`. This assembly is not a superset the v1 tooling can
freeze: `civ.release-freeze/v1` hard-pins the accepted Phase 4 assembly, inventory, source commit,
and exactly 16 participant components, so it fails closed on any additional component by design.

Rather than relaxing those pins, `release_freeze.py` now selects between two **release profiles**
by the assembly manifest's own `release_id` — never from a CLI flag or a declaration claim, so an
unrecognized `release_id` fails closed immediately:

| Profile | Assembly `release_id` | Contract | Components |
|---|---|---|---|
| Phase 4 | `civ-2026-phase4-attendee-kit-v1` | `civ.release-freeze/v1` | 16 |
| Camera-context | `civ-2026-phase5-camera-context-attendee-kit-v1` | `civ.release-freeze/v2` | 17 (adds `context`) |

`civ.release-freeze/v2` (`schemas/civ.release-freeze.v2.schema.json`) has the same top-level shape as
v1. The only structural addition lives inside `assembly`: a `camera_context` record binding the
product-set target and hash, the accepted product count and byte total, and a human privacy/rights
approval:

```json
"camera_context": {
  "set_target": "context/camera-context-products.json",
  "set_sha256": "4250737318af51edec62bb4bd39d4c19444b97152b2885a3b40e0df68c770542",
  "product_count": 13,
  "required_disk_bytes": 5424077234,
  "approval": {"id": "human-...", "document_sha256": "..."}
}
```

`build` derives the `context` component's file count, byte total, and canonical set hash the same
way as every other component, then checks that derived identity against the accepted camera-context
constants before trusting it — this is what makes a missing, replaced, or extra companion file, or a
changed product-set manifest, fail closed even if an assembly manifest's own aggregate hash were
somehow reproduced. The camera_context approval is declared the same way the architecture and
development-authority approvals are (organizer evidence, structurally validated, and required to
appear among the frozen artifacts with role `approval`) — it is not hard-coded, since it is a
per-release human decision rather than a fixed identity. The camera-context provenance string is
`assembly:civ-2026-phase5-camera-context-attendee-kit-v1:<manifest sha256>`, distinct from the
Phase 4 profile's `phase4-assembly:<manifest sha256>`, so component provenance never implies the
wrong assembly. No build-1/build-2/original-bag/organizer filesystem path is ever recorded; `_target`
and the existing `ABSOLUTE_PATH_PATTERN` check reject any such path exactly as they do for the Phase 4
profile.

`build freeze-1` and `build freeze-2` should be run independently against `assembly-1` and
`assembly-2` with the same declaration and evidence root; both are expected to produce byte-identical
`release-freeze.json`/`SHA256SUMS`, and each is then auditable against its own assembly copy. One
becomes the accepted freeze; the other remains reproducibility evidence, matching the pattern already
established for `build-1`/`build-2` and `assembly-1`/`assembly-2`. Acceptance status, real hashes, and
the failure/intervention log for this profile are recorded once freeze-1/freeze-2 are actually built
and audited — this section documents the mechanism, not (yet) a completed acceptance.
