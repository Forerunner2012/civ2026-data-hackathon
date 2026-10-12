# Phase 4 viewer asset acceptance

> **Historical CIV 2026 record.** The dates, commands, artifact identities and acceptance
> below describe the original event and its recorded scope. Start a current session with the
> [QuickStart](../quickstart.md), [organizer guide](../organizers/README.md) and
> [participant contracts](../reference/participant-contracts.md). See the
> [Phase 1–5 history index](../history/civ-2026.md) for later changes. This record does not grant
> new data rights, platform qualification or public-release approval.

Status: **accepted for attendee-kit asset selection**

Recorded: 2026-08-29

This gate selects the participant viewer assets and proves the two reference layouts against
participant-safe Phase 3 products. It does not qualify a release candidate: fresh-machine,
multi-host, multi-architecture, source-archive, SBOM, notices, and final legal checks remain in
Phase 5.

## Selected PlotJuggler release

The first pinned viewer is the official **PlotJuggler 4 beta2** release, tag `3.999.3`, commit
`4dc16a13439010e9d101923886b21571e8c85d97`. The tag resolves directly to that immutable commit.
The release and binaries are published by the upstream PlotJuggler repository:

- release: `https://github.com/PlotJuggler/PlotJuggler/releases/tag/3.999.3`;
- licence: MPL-2.0 for PlotJuggler, with bundled third-party components retaining their own terms.

The kit inventory pins both upstream platform assets. Phase 4 exercised the Windows asset; Phase 5
must exercise the AppImage on the release host.

| Platform asset | Bytes | SHA-256 | Offline launch path |
| --- | ---: | --- | --- |
| `PlotJuggler-3.999.3-Windows-x64.exe` | 117,766,332 | `7b4674f10b48eadd43c195319f0aa5148324ad36464f870a14eb90253fdf4222` | install to a kit-selected directory, then run `bin/PlotJuggler4.exe` with the bundled plugin directory |
| `PlotJuggler-3.999.3-x86_64.AppImage` | 134,646,264 | `f6aa1a4019e8b7a4f730c4771b9d3b1df58db4e745a93cdda43b425692b626c2` | mark executable, then run the AppImage directly |

The Windows installer works without a package repository. A clean offline installation uses its
Qt Installer Framework CLI, an explicit root and cache path, accepted bundled licences, and the
`install` command. The attendee instructions must tell users to verify the asset hash before this
step. The AppImage likewise needs no installer; its hash is checked before execution.

No installer, executable, extracted viewer tree, cache, runtime layout, participant product, or
viewer state is stored in git.

## Windows smoke test

The test host was Windows 11 AMD64. It already contained PlotJuggler `3.999.9`, so using the
machine-wide installation would not have tested the frozen asset. The official `3.999.3` Windows
installer was instead downloaded into ignored runtime storage. Its locally computed hash and byte
size matched the upstream release metadata exactly.

The first isolated command-line install attempt could not use the global Qt installer cache. An
explicit ignored cache path corrected that. Extraction then completed, but shortcut creation
collided with the existing later installation. The existing installation and shortcuts were left
untouched; the fully extracted beta2 runtime was used only for this smoke test. A clean-host
installer run remains a Phase 5 rehearsal item.

The beta2 executable loaded all 17 bundled, manifest-whitelisted plugins and exited successfully.
That set included `mcap-loader=1.0.0` and `ros-parser=1.0.0`. No unlisted plugin loaded.

Two hidden offline launches then used the beta2 executable, its explicit bundled plugin directory,
and runtime-only copies of the public layouts with one relative participant-product source added.
Each process remained responsive after 12 seconds and was stopped by the test harness. The Kashiwa
launch used about 274 MB working set and the Reims launch about 273 MB. Neither stderr stream
reported a layout, MCAP, schema, topic, or field failure. Both reported only the expected denied
online update check, so viewer startup and local source loading did not depend on network access.

Desktop accessibility automation was unavailable on this host, so this record does not claim new
screenshot evidence. The visible-layout evidence is instead the earlier manual viewer acceptance
in `docs/phase2/integrated-gate-acceptance.md`, combined here with exact-product inspection and the
deterministic reference-layout assertions below.

## Layout and product evidence

The runtime layouts preserved the tracked participant panels, curves, ranges, colours, and titles.
Their only runtime additions were the v4 root marker and a temporary relative data-source element
needed for startup reload. They used these public Phase 3 product identities:

| Tracked layout | SHA-256 |
| --- | --- |
| `layouts/kashiwa-right-turn.pj4.xml` | `1fde2907b5bfe8630aa55f89b5d1a5420aaf6672f66c1d8c75589715b5b725c0` |
| `layouts/reims-left-turn.pj4.xml` | `c79bcf876b0df1f2d72aeb34d2a929e809d054255d329518d3235c74db288716` |

| Dataset | Product role | Product bytes | Product SHA-256 |
| --- | --- | ---: | --- |
| Kashiwa | warm-up | 11,161,467 | `942a12299a80500ea780a1cfae5e59d0f3ef5b481ed7741db8d07968a4d82803` |
| Reims | development chunk 0 | 45,207,253 | `9e37b7ee7a754707d15154b83ed797f3fa248cc6569f43e509cff5b2b642b110` |

`civ inspect` reopened both copied MCAPs. It found every referenced topic and field:

- Kashiwa: steering angle, vehicle speed, vehicle error code, and object-detected flag;
- Reims: IMU yaw rate and all three linear-velocity components.

The eight deterministic reference-kit tests passed. They parse each layout, require at least one
curve, resolve each curve to a topic named by the matching public EventSpec, require detector-topic
curves to bind an EventSpec field, verify every referenced file exists, reject URLs from the
offline quickstart/layout surface, and preserve the participant-only command boundary.

The layout XML, acceptance note, public quickstart, public examples, and runtime stderr/stdout were
scanned for organizer paths, truth and label-pack markers, sealed intervals, answer keys, private
routes, and organizer commands. No participant-surface leak was found. The runtime products and
logs remain ignored and are not distribution inputs.

## Lichtblick packaging amendment

Ticket #45 superseded the earlier exclusion after exact Lichtblick inputs became available. The
assembled kit now carries both PlotJuggler and **Lichtblick 1.28.0**; the inventory refuses a
one-viewer-only payload. The staged Windows Lichtblick artifact is exactly 266,309,046 bytes with
SHA-256 `94420a37b3f9520091501842ee491966665090cfd23f40115f36f7ecf58ea2ec`.

The reference layouts are tracked as `layouts/lichtblick-kashiwa-right-turn.json` and
`layouts/lichtblick-reims-left-turn.json`. The organizer visually inspected each supplied layout
with one matching participant MCAP and approved both rendered launches. This human evidence closes
the visual-open question that process responsiveness alone could not answer.

On connected machines, the participant instructions recommend the upstream no-install web app at
`https://lichtblick-suite.github.io/lichtblick/`. This is the computer-independent and preferred
security route because it avoids executing a binary carried beside the data. The exact desktop
artifact remains in the kit for a disconnected room, with checksum verification required first.

## Remaining Phase 5 checks

Phase 5 must run the Windows installers and Linux viewer assets on fresh target machines, verify
event hardware and graphics behaviour, freeze the final copied bytes, archive the exact
corresponding source, produce SBOM and third-party notices, confirm all bundled licences, and
rehearse recovery media. Any change to a selected version or asset hash reopens this gate.
