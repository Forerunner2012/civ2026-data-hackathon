# Build and audit a participant kit

Build from an organizer checkout after confirming the [session permissions and reviewed inputs](README.md#prepare-the-session). Run commands from the repository root. The examples use a POSIX shell and absolute paths for external inputs and outputs.

## Prepare the inputs

Set these variables to existing, verified inputs. Keep `WORK` outside Git and choose new output directories for the fallback, static export, and assembled kit.

| Variable | Input |
| --- | --- |
| `WORK` | External staging directory for generated files. |
| `DATA` | Directory containing the accepted participant product-set JSON, MCAPs, and public manifests. Use its actual JSON filename below. |
| `VIEWERS` | Directory containing all five pinned files listed in the [viewer guide](../../kit/viewer/README.md). |
| `CACHE` | Prepared uv cache for the source-runtime recovery path. Qualify it on the intended host; copying a cache does not establish offline readiness. |
| `CONTAINER` | Exported archive of the inventory's pinned container image, `civ-phase4:attendee-candidate-558e85c`. |

The builder remains pinned to the [accepted 13-product set and viewer/container identities](../phase4/participant-kit-inventory.md#frozen-scope). Optional session inputs do not add support for arbitrary product sets or platforms. Do not substitute an unqualified recording, viewer, or image.

Install project dependencies with `uv sync --locked`. Prepare and verify the external recovery inputs using the session's qualified runtime route and [setup guide](../setup.md). Keep private truth and review state separate from every participant input.

## Build the inventory and supporting material

Replace `participant-set.json` with the supplied product-set filename. Pass every pinned viewer to both inventory and assembly. The inventory binds the current checkout's tracked assets, source commit, lockfile, and external identities. Rebuild it after changing a tracked asset.

```sh
uv run --locked -m civ_workshop.kit_inventory build "$DATA/participant-set.json" \
  --repository . \
  --viewer "$VIEWERS/PlotJuggler-3.999.3-Windows-x64.exe" \
  --viewer "$VIEWERS/PlotJuggler-3.999.3-x86_64.AppImage" \
  --viewer "$VIEWERS/lichtblick-1.28.0-win.exe" \
  --viewer "$VIEWERS/lichtblick-1.28.0-linux-x64.tar.gz" \
  --viewer "$VIEWERS/lichtblick-1.28.0-mac-universal.dmg" \
  --output "$WORK/inventory/participant-kit.json"
uv run --locked -m civ_workshop.kit_inventory audit "$WORK/inventory/participant-kit.json"
uv run --locked -m civ_workshop.kit_assembly fallback "$DATA/participant-set.json" \
  --data-root "$DATA" --output "$WORK/fallback"
```

Build the participant-only site locally, then export it. This does not deploy a website. The export reads the public build's `dist/server/index.js` and refuses an existing output directory.

```sh
npm --prefix handoff-site ci
npm --prefix handoff-site run build
node handoff-site/scripts/export-public-static.mjs "$WORK/site"
```

## Assemble and verify the kit

```sh
uv run --locked -m civ_workshop.kit_assembly assemble "$WORK/inventory/participant-kit.json" \
  --repository . --data-root "$DATA" \
  --viewer "$VIEWERS/PlotJuggler-3.999.3-Windows-x64.exe" \
  --viewer "$VIEWERS/PlotJuggler-3.999.3-x86_64.AppImage" \
  --viewer "$VIEWERS/lichtblick-1.28.0-win.exe" \
  --viewer "$VIEWERS/lichtblick-1.28.0-linux-x64.tar.gz" \
  --viewer "$VIEWERS/lichtblick-1.28.0-mac-universal.dmg" \
  --site-root "$WORK/site" --fallback-root "$WORK/fallback" \
  --cache-root "$CACHE" --container-archive "$CONTAINER" \
  --output "$WORK/kit"
uv run --locked -m civ_workshop.kit_assembly audit "$WORK/kit/attendee-kit-assembly.json"
```

For approved camera context, build the inventory with `--context-set CONTEXT_SET.json` and assemble with the matching `--context-root CONTEXT_DIRECTORY`. A context-bearing inventory requires its exact approved payload. For reviewed decks, add `--presentations-root DECK_DIRECTORY`, containing `briefing.pptx` and `submission-checklist.pptx`. See the [camera approval record](../phase5/camera-context-candidate.md) and [presentation guide](../presentations/README.md) for their separate evidence and preparation.

Assembly copies and checks the declared files, participant-safe runtime, guide copies, and selected material. It creates `attendee-kit-assembly.json` and `checksums/ASSEMBLY-SHA256SUMS`. The audit must exit successfully and print `"valid": true`. Inspect its file count, byte total, and manifest hash. Keep the manifest and checksum files with the kit.

Open `site/index.html`, follow the kit README and QuickStart on the target machines, and verify local links and recovery inputs. Re-audit the final copied kit. Audit success proves file integrity and the implemented safety checks; permissions, machine qualification, release approval, and publication remain separate organizer decisions.

## Include organizer-selected session materials

Add these optional arguments to `kit_assembly assemble` before its `--output` argument. Select the released files explicitly. It never discovers references from a private
directory or decides what may be disclosed:

```text
--participant-wheel PARTICIPANT_WHEEL.whl
--practice-pack RELEASED_PRACTICE_REFERENCE.json
--session-brief SESSION_BRIEF.md
```

Repeat `--practice-pack` for each authorized complete practice reference. Each pack must validate
against the scoring-reference contract and match a participant product's exact source hash. Any
declared product-manifest hash must match too. Structural validity and a matching recording do not
grant release authority: the organizer must select only references already authorized for the
session. Never pass sealed or unreleased evaluation references. Existing source-bound review and
release checkpoints still apply.

The wheel must contain the public participant runtime and expose
`civ_workshop.participant_cli:main`. An organizer wheel is rejected. Build the participant target
with `uv build participant --wheel --out-dir EXTERNAL_DIST`, then supply that reviewed wheel.
A wheel alone does not establish offline installation readiness. Supply and qualify matching
dependencies separately, following the [setup guide](../setup.md).

Assembly copies the exact wheel to `runtime/wheels/`, practice references to `practice-labels/`,
and the brief to `SESSION-BRIEF.md`. `SESSION-MATERIALS.md` links the selected inputs. The brief
must contain confirmed session instructions without credentials or private paths. Its inline
relative Markdown links must resolve inside the assembled kit. Use `practice-labels/NAME.json`
and the actual wheel path when linking those inputs.

The existing privacy audit, assembly file inventory, component sizes and checksum writer cover
all copies. Do not rewrite the manifest through private helpers. With these inputs omitted, the
existing source-runtime assembly remains available. No new session input creates approval,
publication authority or a release claim.
