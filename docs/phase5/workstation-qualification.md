# Phase 5 workstation qualification

Status: **in progress — deterministic contract ready; fresh-machine and human graphics evidence pending**

Recorded: 2026-09-01

This record tracks issue #49. It qualifies the exact release accepted by #48 without changing or
copying generated qualification payloads into git. Machine declarations, command logs, screenshots,
viewer state, private development labels, copied release trees, and generated manifests remain in
organizer-controlled external storage. The repository retains only this redacted procedure, the
closed contract/schema, and final aggregate evidence.

## Frozen input

The qualification tooling accepts the historical Phase 4 release and the extension-aware universal
release as two exact, non-mixable profiles:

| Input | SHA-256 or identity |
|---|---|
| Phase 5 release manifest | `2003cc25fc24d57a56e84a50ff8a3d06ec6a7ab16cd95b78e2933dd27b91bf0f` |
| Phase 4 assembly manifest | `b661d18791f6d6a640ae35c595fc9b8a5ecccba94a451122977df831c6c2f097` |
| Container archive | `ff983defaa02671982ee78dbf13026d0d007c5c16082cd898658228875f289db` |
| Loaded image | `sha256:47f4017351802e878ff138c9e3aead0161de660914e79c252554968a91657560` |
| Private development authority | `08a7bce5b2e3029ad5e8c12da395118443fd62850e99a8f7c4a329b5f3f2da02` |
| Universal release manifest | `e7cbc09abcbfd2b1b0ac3c07cfbf5e6995f9c4d35e197edb33d441b11e5ce7c8` |
| Universal assembly manifest | `64c55f32a0b1898b8eadc4540a97e6d1b9c44f2b404abcb13df99326e9203bef` |

Any changed release byte reopens #48. The private development set remains organizer-only and is
mounted read-only only for the `score` qualification step; it never enters release media, a
participant output, the generated qualification manifest, or git.

## Platform decision

The #48 event-owner decision advertises **Windows-amd64 hosts and viewers with the pinned
linux-amd64 container through WSL2**. Ticket #49 also asks for an Ubuntu event-workstation runtime
check. Ubuntu therefore qualifies the same linux-amd64 container as a compatibility/runtime host;
the universal release also carries the Linux viewer binaries. macOS remains viewer-only and does
not enter the container-runtime qualification matrix.

The universal declaration template was generated from the accepted freeze and exact assembly on
2026-09-02 with SHA-256 `09bc573a88dfee6d742cb9660eecb41df627f802ce9b666b21c9a9f80fd4f6cc`.
It remains deliberately `pending-human`: the event-owner go decision does not fabricate fresh-host
command, viewer, screenshot, recovery, or connected-route evidence.

The command rehearsal uses one exact authorized pair per dataset:

| Dataset | Participant product SHA-256 | Private label-pack SHA-256 |
|---|---|---|
| Kashiwa | `0188d748c0b49151e5af3f0c644e59e7cd1dda6ad7b41f8f5e64ada21b27056e` | `5361ba59d734c22493ad5bc2f6d81eae5c17e399d7aa8a1b33753c60332ecb6a` |
| Reims | `9e37b7ee7a754707d15154b83ed797f3fa248cc6569f43e509cff5b2b642b110` | `ad5d1b5525eeaa7fa35dd1ae4a457f903dc60d50deffe9bcb1f3887a60f8c204` |

The products are frozen participant bytes. The label packs are separately controlled organizer
inputs covered by the approved aggregate authority; their paths and contents remain private.

The matrix is fixed:

| Fresh machine | Container path | Human desktop-viewer matrix |
|---|---|---|
| Windows-amd64 + WSL2 | Kashiwa and Reims, twice each | PlotJuggler and Lichtblick × Kashiwa and Reims |
| Ubuntu linux-amd64 | Kashiwa and Reims, twice each | None; no Linux viewer is carried in the frozen release |

The official connected Lichtblick route is checked separately at
`https://lichtblick-suite.github.io/lichtblick/`. That connected check must not be confused with
the isolated offline runs.

## Fresh-host procedure

Use one newly installed machine of each class. Start with documented OS/container prerequisites,
copied frozen release media, and the separately controlled private development input only. Do not
use a repository checkout, developer cache, previous viewer profile, or network fetch after
isolation.

1. Hash the release manifest, assembly manifest, container archive, both viewer installers, and
   four layouts before execution. Audit the complete assembly and load the exact container archive.
   Record the resulting image ID.
2. Record an opaque machine ID, OS/version, amd64 architecture, CPU, logical CPU count, RAM,
   graphics adapter, display resolution, scaling, and container-runtime identity. Do not record a
   username or organizer path.
3. Disable networking. Run without a GPU request. Mount the copied kit read-only and only a fresh
   participant-owned output directory writable. Confirm the container cannot write the release
   mount.
4. For Kashiwa and Reims, exercise `doctor -> inspect -> sample -> detect -> clip -> score ->
   report -> submission-init`. Use a fresh output directory for each attempt and run the chain
   exactly twice. Fill the participant-authored report/figure/reproduction placeholders with
   neutral qualification content before `report`; do not import an earlier participant profile.
5. For each attempt record all eight exit codes, aggregate wall time, peak RSS, output bytes, disk
   bytes, the exact source-product and private label-pack hashes above, and the canonical hash of
   sorted output-relative-path/file-hash pairs. The two output-set hashes for the same
   machine/dataset must match.
6. On fresh Windows, checksum, install, and launch both exact desktop viewers offline. A human opens
   each frozen Kashiwa/Reims layout with the matching participant product and approves scaling,
   fonts, graphics, file association, permissions, and offline failure messaging. Hash the evidence
   bundle; keep the bundle outside git.
7. While connected, separately open the official Lichtblick web route and record human approval
   plus an evidence hash. Then return to isolation before any offline test.
8. Uninstall and reinstall one pinned viewer from the same verified bytes. Execute the documented
   participant recovery path in one profile and verify that a second participant profile remains
   uncontaminated.
9. Record every failure and intervention. An unresolved intervention, reused state, network fetch,
   GPU request, changed release byte, missing human approval, or nondeterministic output blocks the
   qualification.

## Deterministic organizer contract

`civ_workshop.workstation_qualification` builds and audits
`civ.workstation-qualification/v1`. The matching closed schema is
`schemas/civ.workstation-qualification.v1.schema.json`.

The builder derives the accepted release identity rather than trusting caller-supplied hashes. It
rehashes the freeze and complete assembly, requires exactly one fresh Windows/WSL2 and one fresh
Ubuntu machine, checks both datasets and two deterministic attempts per machine, pins the four
viewer/layout combinations, requires explicit `human-*` approvals, rejects absolute host paths,
and refuses unresolved interventions or release-byte changes.

Generate the external, deliberately unapproved declaration template from the exact frozen inputs:

```text
uv run -m civ_workshop.workstation_qualification template RELEASE_FREEZE ASSEMBLY_MANIFEST DECLARATION
```

The template pins the machine/dataset/viewer matrix and fixed hashes, but fills evidence, telemetry,
isolation, and approval fields with failing values. It cannot accidentally build an accepted
qualification before the fresh hosts and human reviewers replace every placeholder.

The external build command is:

```text
uv run -m civ_workshop.workstation_qualification build RELEASE_FREEZE ASSEMBLY_MANIFEST DECLARATION QUALIFICATION
```

The final external audit command is:

```text
uv run -m civ_workshop.workstation_qualification audit QUALIFICATION RELEASE_FREEZE ASSEMBLY_MANIFEST
```

The audit reconstructs canonical bytes from the recorded declaration and current frozen inputs.
It leaves no temporary audit files behind.

## Current evidence and human gate

The exact frozen assembly was rehashed while generating the external declaration template. The
template is deliberately unapproved, has SHA-256
`09bc573a88dfee6d742cb9660eecb41df627f802ce9b666b21c9a9f80fd4f6cc`, and a real build correctly
stops at the first unproved fresh-host prerequisite without producing a qualification manifest.

The current organizer workstation is recorded only as a non-acceptance baseline. Docker client
29.7.2 is installed but its daemon is stopped. WSL2 is installed with stopped Ubuntu 26.04 and
24.04 distributions. The machine is not fresh, so starting those runtimes would not satisfy #49.

The contract has 12 focused passing tests. The complete repository has 255 passing Python tests;
repository-wide Ruff, strict mypy across 48 source files, schema JSON parsing, and
`git diff --check` also pass.
No fresh Windows/WSL2 or Ubuntu machine has yet supplied a declaration, and no new human visual,
connected-web, or recovery approval is asserted by this record. Issue #49 must remain open until
those external records build and audit successfully.
