# Integrated Phase 4 attendee-kit gate

> **Historical CIV 2026 record.** The dates, commands, artifact identities and acceptance
> below describe the original event and its recorded scope. Start a current session with the
> [QuickStart](../quickstart.md), [organizer guide](../organizers/README.md) and
> [participant contracts](../reference/participant-contracts.md). See the
> [Phase 1–5 history index](../history/civ-2026.md) for later changes. This record does not grant
> new data rights, platform qualification or public-release approval.

Status: **accepted — all Phase 4 attendee-kit criteria pass**

Recorded: 2026-08-30 · Operator: Codex on the organizer workstation

This record integrates the human-approved participant experience, public/static audience boundary,
viewer and layout set, signals-only data, submission materials, fallback pack, participant runtime,
offline dependency cache, and pinned CPU container into one deterministic candidate for Phase 5.
External binaries, MCAPs, caches, generated site output, container state, and runtime evidence remain
outside git. Public evidence is limited to participant-safe identities, aggregate measurements,
immutable hashes, approvals, failures, corrections, and redacted consequences.

## Gate inputs

| Input | Accepted evidence |
|---|---|
| Tool source | commit `bc0cb9cfb98b92665626a5b64c9a65571e80aaf2`; `civ-workshop` 0.1.0 |
| Participant product set | 13 products; 1,102,147 messages; 335,177,173 bytes; `d515c0a7cd748f8b2ad0cb41b93d8847b0917c2e6469be2f8be09582fc62ef9b` |
| Participant inventory | 719,423,786 required bytes; `aee496467d4537acca417d3481e8cec81c0e8db4e945fd10b3aac7dfb56c27bf` |
| Candidate image | `civ-phase4:attendee-candidate-558e85c`; `sha256:47f4017351802e878ff138c9e3aead0161de660914e79c252554968a91657560` |
| Image archive | 464,562,688 bytes; `ff983defaa02671982ee78dbf13026d0d007c5c16082cd898658228875f289db` |
| Exact assembly | 3,225 manifest files; 1,307,178,032 required bytes; `b661d18791f6d6a640ae35c595fc9b8a5ecccba94a451122977df831c6c2f097` |
| Physical assembly | 3,227 files; 1,308,252,161 bytes; four 2-TiB drive targets |
| Assembly checksum file | `8a25be00292bfceb55be4f8badd1e5fbab77906aededf2c39cc558366e15ed28` |
| Inventory checksum file | `36ca4e45fa96e4a93ee7634a705b54e88a0780342e53dbc783afbef99c75fbd4` |

The two recovered Kashiwa derivatives retain the Phase 3 caveat: structural recovery made the
recordings readable but cannot prove that truncation lost no records. Corrupt-parent locations are
not participant-visible. The caveat remains in the participant inventory and every assembly.

## Step 1 — One participant experience survives live, public, static, and desk paths

The public start page and quickstart use one stable command vocabulary:
`doctor -> inspect -> sample -> detect -> clip -> score -> report`. The same Kashiwa and Reims
identities, signals, viewer layouts, seven teaching beats, report instalments, six submission
outcomes, form/local/USB recovery authority, extension exemplar, and offline fallback instructions
appear consistently in the participant view and static fallback. Development scoring requires an
explicit separately authorized `DEVELOPMENT_LABELS` input; no organizer or sealed label authority
is silently added to the kit.

The human organizer approved the final participant wording and all seven post-event worked
approaches on 2026-08-29. The desk set remains exactly three materials: one A4 participant brief,
one two-sided A5 help card, and one write-on A4 signal trace. Their four rendered sides were
visually approved at actual size without clipping, overlap, or illegible text. The organizer also
approved the coach escalation boundary, jury anchors, post-event solutions, and
walkthrough/consent wording. Release controls still prevent worked approaches from appearing
before the event.

## Step 2 — Exact viewer, layout, teaching, template, and fallback inputs reproduce

The kit includes the two accepted offline Windows viewer assets:

| Viewer | Bytes | SHA-256 |
|---|---:|---|
| PlotJuggler 4 beta2 `3.999.3` | 117,766,332 | `7b4674f10b48eadd43c195319f0aa5148324ad36464f870a14eb90253fdf4222` |
| Lichtblick `1.28.0` | 266,309,046 | `94420a37b3f9520091501842ee491966665090cfd23f40115f36f7ecf58ea2ec` |

The exact reference layouts are:

| Layout | SHA-256 |
|---|---|
| PlotJuggler Kashiwa | `1fde2907b5bfe8630aa55f89b5d1a5420aaf6672f66c1d8c75589715b5b725c0` |
| PlotJuggler Reims | `c79bcf876b0df1f2d72aeb34d2a929e809d054255d329518d3235c74db288716` |
| Lichtblick Kashiwa | `8a49a1fbe940b896a9fe7dcd95d19b79c09b0d60a733600f46fe4c7ce6903d84` |
| Lichtblick Reims | `8821afc2e9c5bb9ed366305b22065c53dc20cfcedaa3191e32875dfe705e8b62` |

The organizer visually opened one matching participant MCAP with each supplied Lichtblick layout
and approved both rendered launches. This closes the visual-open question that process
responsiveness alone could not answer. On connected machines the instructions recommend the
upstream no-install web application at `https://lichtblick-suite.github.io/lichtblick/`; the pinned
desktop binary remains available for a disconnected room.

Every public example, schema, submission-template file, static-site file, neutral fallback clip,
CSV table, plot, runtime source file, and offline-cache byte is recorded in the assembly manifest.
The fallback manifest is `25abd3419238210d63df72933b3ef1dc7e336afc348057b9fd52cc578f293003`;
the six submission-template files retain their individually pinned inventory hashes. The exact
static export, 39,133,570-byte fallback component, 83,416,684-byte offline cache, 223,055-byte
participant runtime, and all other components are transitively frozen by the assembly hash.

Two independent assemblies were produced from the same closed inputs. Their manifest,
`ASSEMBLY-SHA256SUMS`, inventory checksum file, file count, and byte totals matched exactly. Both
fresh audits reopened and hashed their full payloads successfully.

## Step 3 — The participant boundary remains signals-only and private-free

The inventory fixes `content_profile` to `signals-only` and contains zero context packs. Fresh
audits reopened every MCAP and rechecked exact topic allowlists, schemas, message counts, roles,
hashes, and disk sizes. The default Kashiwa and Reims reference specs were also clipped against the
assembled products; neither requests a camera topic.

The participant assembly contains no organizer route or wording, solution, coach guide, rubric
anchor, private command or module, answer key, held-back product identity, sealed interval, source
path, private form secret, personal data, label pack, context pack, or evidence clip. This boundary
is checked across the public server bundle, client assets, rendered pages, static fallback,
inventory, diagnostics, metadata-only bundles, runtime source, and complete assembly. There is no
top-level repository/tool source copy in the kit; the runtime contains only participant commands.

Optional camera/context data did not receive a Phase 4 privacy-and-rights approval and is therefore
absent. The schema still requires a separate manifest and explicit human approval identity before
such a pack could be added in a later candidate.

## Step 4 — The exact candidate runs offline on CPU without a GPU

The self-contained image was built from `kit/participant-container.Dockerfile` with
`--network none --no-cache`. Its participant CLI exposes only `doctor`, `inspect`, `sample`,
`detect`, `clip`, `score`, `report`, and `submission-init`; private modules and inherited host-path
labels are absent.

| Environment item | Recorded value |
|---|---|
| Base OCI digest | `sha256:122a787d0eb7e1b2c18370e35ef394332db5c11d242bea6f05f2b2911e26b04d` |
| Prepared base image | `sha256:abf90cdd46b446a185f24bc2a7097a49b34b57c415ff227e02ae55c17c7cd423` |
| Candidate image | `sha256:47f4017351802e878ff138c9e3aead0161de660914e79c252554968a91657560` |
| OS / ROS / architecture | Ubuntu 26.04 / Lyrical / linux-amd64 (`x86_64`) |
| Python / tool | CPython 3.12.11 / `civ-workshop` 0.1.0 |
| Runtime dependencies | cel-python 0.5.0; mcap 1.4.0; mcap-ros2-support 0.5.7; PyYAML 6.0.3 |
| Isolation | `--network none`; read-only container and kit; `/tmp` tmpfs; output-only writable mount |
| GPU boundary | no GPU flag; `/dev/nvidia0` absent; `nvidia-smi` absent |

Against the exact assembled kit, one command completed doctor plus Kashiwa
`inspect -> sample -> detect -> clip` and Reims `inspect -> detect -> clip`:

| Measurement | Result |
|---|---:|
| Exit status | 0 |
| Wall time | 32.13 s |
| Peak resident set | 44,056 KiB |
| CPU utilization | 88% |
| Socket messages sent / received | 0 / 0 |
| Filesystem input units | 594,065 |
| Kashiwa events / clips | 4 / 4 |
| Reims events / clips | 1 / 1 |
| Output files / bytes | 19 / 3,357,331 |
| Canonical output-set SHA-256 | `564a70e76d57dee7134ce52a445b354f4e2065bcc69695770b45a8077d483b3b` |

The canonical output hash is SHA-256 over sorted lines of file SHA-256, two spaces, the relative
POSIX path, and LF. Doctor passed every required environment, workspace, bag, dependency, and
offline-kit check. Its sole nonrequired warning states that GUI viewers are external to the
pure-MCAP container. Loading the exact tar copied into the final assembly reproduced image
`sha256:47f4017351802e878ff138c9e3aead0161de660914e79c252554968a91657560` as linux-amd64;
the inspected inherited desktop mount labels remained blank.

## Step 5 — Repository, schema, site, accessibility, and leakage gates

The final gate uses the declared checks rather than an intermediate subset:

- all Python tests, including stable schemas/contracts, participant command boundaries, exact
  inventory/assembly behavior, signals-only reference clipping, leakage rejection, and metadata
  bundle boundaries;
- Ruff over the repository and strict mypy over `src` and `tests`;
- internal configured, internal no-form, public, accessibility, print, production-route, static
  export, release-control, audience-separation, and leakage site tests (11 + 8 + 17 passed);
- ESLint over the site;
- fresh audits of the final inventory and both deterministic assemblies; and
- `git diff --check` plus a final tracked/untracked boundary review.

The accessibility gate verifies semantic heading order, labeled alternatives, monochrome print
structure, live status/progress semantics, reduced motion, and no-script fallback behavior. The
existing visible `YOUR BRIEF` section is an `h2`, so the page no longer skips from `h1` to `h3`.

Generated site output, caches, datasets, binaries, containers, runtime outputs, and this gate's
external evidence remain uncommitted.

## Failure and intervention log

| # | Step | What happened | Resolution and consequence |
|---|---|---|---|
| 1 | Initial #45 assembly | The assembled `tool/source` copied the full repository, including private intake, cohort-score, product, and sealed tooling. | The new participant auditor rejected `tool/source/pyproject.toml`; assembly changed to a participant-only runtime and now rejects private modules and commands. |
| 2 | Runtime design | Removing the source copy exposed that the archived base image contained Ubuntu, ROS, and uv but no runnable `civ` environment. | Added deterministic participant runtime source and then froze it inside the self-contained candidate image. |
| 3 | Accessibility | The first semantic-heading test found an `h1` to `h3` skip. | Converted the existing visible `YOUR BRIEF` element to `h2` without changing its wording or visual role. |
| 4 | Windows offline probe | The ordinary issue cache lacked `zstandard`. | The exact kit cache installed all 14 required runtime packages in frozen/offline mode; no dependency was fetched during acceptance. |
| 5 | Linux loose-cache probe | The staged Windows-oriented cache lacked a Linux `lz4` wheel. | Stopped using the loose cache as Linux runtime authority and selected a self-contained candidate image; the cache remains a Windows recovery input. |
| 6 | Candidate image attempt 1 | uv-managed CPython under `/opt/civ-runtime` expected prepared state at `/opt/civ-state`. | Rebuilt from the checked-in Dockerfile with deterministic runtime state at the required path. |
| 7 | Candidate metadata | The first committed image inherited a Docker Desktop host-mount label. | Rebuilt with the inherited source/target labels blank; final metadata contains no host path. |
| 8 | Signals-only replay | Both tracked reference specs requested an excluded camera topic. | Removed those topic requests and added a regression test requiring default reference clipping to use signals only. |
| 9 | Site gate environment | The first sandboxed npm test failed with `EPERM`. | Reran with the required host execution permission; the complete site suite passed without a product change. |
| 10 | Static-export invocation | A PowerShell npm invocation appended the output argument after the script's hardcoded path and met an existing temporary directory. | Invoked the export script directly with a fresh external destination; the resulting static artifact passed its audit. |
| 11 | Final Python gate launch | Three concurrent uv processes raced while initializing the user cache; the sandbox retry then could not read uv's managed interpreter because the checked-in `.venv` link is stale. | No test code ran in either attempt. Reran the full suite sequentially with the repository cache and approved managed-Python access; pytest, Ruff, and strict mypy all passed. |
| 12 | Archive-load proof | The first `docker load` could not connect because Docker Desktop's Linux daemon was stopped. | Started the existing daemon, loaded the exact assembled tar successfully, and confirmed the pinned image ID, linux-amd64 platform, and blank inherited host-mount labels. |

No acceptance criterion was overridden. Every correction preserved the closed Phase 3 contracts,
dataset membership, evaluator semantics, 15/10 Detection split, metadata-only submission boundary,
and absence of optional context. No retry silently broadened Phase 4.

## Routed consequences

- **Phase 5 release rehearsal:** load this exact image archive and copy this exact assembly onto
  fresh Windows/WSL2 and Ubuntu event hardware; verify physical SSD bytes, event-network behavior,
  viewer graphics, form state, local/USB intake, and recovery media before go/no-go.
- **Release/legal freeze:** produce the SBOM, third-party notices, corresponding source archive,
  final dependency archive, multi-architecture decision, licence adjudication, and post-event
  deletion record. The Phase 4 candidate is not that legal or physical release sign-off.
- **Viewer distribution:** retain the official Lichtblick web link as the recommended connected
  route and both checksum-pinned desktop assets for offline recovery; any version/hash change
  reopens viewer and assembly acceptance.
- **Recovered Kashiwa derivatives:** retain the no-loss-proof caveat beside every copied product and
  keep corrupt-parent provenance organizer-only.
- **Development scoring authority:** freeze the separately authorized development-label delivery
  during Phase 5 rehearsal. It remains outside this signals-only participant candidate; sealed
  labels and scoring stay organizer-only.
- **Contracts and evaluator:** no Phase 5 contract migration is implied. Stable participant `v1`,
  fixed matching semantics, product membership, and dataset-specific scoring authority all pass.

## Final criterion table

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | One public start and stable command path agree across live/static recovery | PASS | Step 1 |
| 2 | Viewer, layout, products, image, templates, teaching, fallback, cache, and manifests reproduce | PASS | Step 2 |
| 3 | Printed/public wording and private organizer materials have human approval | PASS | Steps 1-2 |
| 4 | Server, client, static, inventory, diagnostics, bundles, and kit remain private-free | PASS | Step 3 |
| 5 | Signals-only is the default and unapproved context remains absent | PASS | Step 3 |
| 6 | Exact kit runs offline on pinned CPU with no network or GPU and measured deterministic output | PASS | Step 4 |
| 7 | Full Python, schema, site, audience, leakage, accessibility, lint/type, and diff gates pass | PASS | Step 5 |
| 8 | One redacted record captures every failure, correction, approval, and Phase 5 consequence | PASS | This record |
