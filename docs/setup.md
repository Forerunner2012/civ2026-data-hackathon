# Set up the participant CLI

Prepare your laptop before the workshop. Install `civ`, open your supplied kit, then follow the [QuickStart](quickstart.md). Use [runtime requirements](runtime-requirements.md) for intended platforms, optional tools and the limits of completed qualification.

## Before installation

Have Git and uv available for connected installation. Use CPython 3.10, 3.11 or 3.12; the commands below select 3.12. uv can obtain Python while connected and installs the package dependencies. Follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) if uv is missing. Git is needed for the Git source, not local wheel recovery.

The intended native routes are Windows AMD64 PowerShell and Linux AMD64. WSL2 is an optional Linux route on Windows. ARM64 execution on a Pi was checked in its existing container; it does not establish native Linux AMD64 or bare-host support. The core pure-MCAP workflow requires no ROS, viewer, Docker, Hyper-V or administrator access.

## Install while connected

Run this in PowerShell or a Linux shell. You can run installation outside the kit:

```text
uv tool install --python 3.12 "git+https://github.com/Forerunner2012/civ2026-data-hackathon.git@main#subdirectory=participant"
uv tool update-shell
```

Restart your shell, then run:

```text
civ --help
```

Expect the eight participant commands: `doctor`, `inspect`, `sample`, `detect`, `clip`, `score`, `report` and `submission-init`. No project activation or `uv run` is needed. The `participant` subdirectory is the install target; the repository root installs organizer tooling and is not the participant route.

Repository access is required while it is private. If your existing access uses SSH, use this source instead, then perform the same PATH setup and shell restart:

```text
uv tool install --python 3.12 "git+ssh://git@github.com/Forerunner2012/civ2026-data-hackathon.git@main#subdirectory=participant"
```

If `civ` is not found, inspect `uv tool dir --bin`, rerun `uv tool update-shell`, and restart the shell. If `uv` itself is not found, finish its installation first. If authentication fails, ask for repository access or use your supplied matching wheel backup. Do not place credentials in commands or use an organizer-root install.

## Open the local kit

Run the analysis commands from the root of the unpacked kit. Keep the recording, examples, schemas and supplied practice labels read-only. Let `civ submission-init` create a new `working/` directory, or choose another new participant-owned output directory. Doctor uses an existing writable directory. The QuickStart names the Kashiwa warm-up inputs; use the matching Reims inputs from the same source for a Reims session.

The default `civ doctor` checks Python, dependencies, workspace, MCAP and kit layout. ROS and visualization warnings do not block the default pure-MCAP profile. A missing kit is different from an installation failure. Follow the printed `Action:` for a required failure. Only the optional historical `release-target` profile adds its ROS/visualization/platform requirements.

For visual inspection, open the kit's `viewer/README.md`. A viewer failure does not prevent `civ sample`. `site/index.html` is a static participant page; room instructions and live state come from the organizers, not that offline page.

## Update while connected

For a main-following installation:

```text
uv tool upgrade civ-workshop
```

Main can advance; frozen wheel backups retain their own source and dependency versions. uv handles an existing installation. Use `uv tool install` with a different desired source to replace it; no default `--force` is needed.

If organizers supplied reviewed dependency constraints, editing the file alone does not refresh saved constraints. Re-read the new file explicitly:

```text
uv tool install --python 3.12 --reinstall --upgrade --constraint participant-constraints.txt "git+https://github.com/Forerunner2012/civ2026-data-hackathon.git@main#subdirectory=participant"
```

The constraints file is optional. Use an actual reviewed file, not a guessed pin set.

## Recover from matching local wheels

Have uv and compatible Python available before going offline. Use the supplied participant wheel and matching dependency wheels for your OS, architecture and Python. Check their supplied hashes. A participant wheel alone does not include Python, uv or its dependencies; a copied raw cache is not a universal backup.

Change to the backup directory and run:

```text
uv tool install --offline --no-index --no-python-downloads --python 3.12 --find-links . ./civ_workshop-0.1.0-py3-none-any.whl
```

Use your backup's actual wheel filename if its version differs. Then perform PATH setup if needed, restart the shell and run `civ --help`. Return to the kit root for analysis. A missing dependency wheel or interpreter is a backup failure, not a reason to fetch undeclared inputs offline. Ask a coach for the matching complete backup.

These resolver controls prevent uv fetching packages; they do not prove external network isolation. For optional container recovery, follow the supplied kit README's exact image and prerequisite instructions. Docker is required only for that route; do not treat an AMD64 image as an ARM64 image.

## Continue the workshop

Follow the [QuickStart](quickstart.md) for the eight commands and immediate diagnostics. Scoring needs the practice labels matched to the source announced for your kit. Do not use organizer-only truth or an incomplete answer key as a complete evaluation reference. Recordings, clips and labels stay local; submit only the validated metadata bundle.

When connected, the canonical [participant contracts](https://github.com/Forerunner2012/civ2026-data-hackathon/blob/develop/docs/reference/participant-contracts.md) and [scoring reference](https://github.com/Forerunner2012/civ2026-data-hackathon/blob/develop/docs/reference/scoring.md) provide detail. These online references are optional for the local command sequence. The supplied schemas remain local in the kit. See the [uv command reference](https://docs.astral.sh/uv/reference/cli/) for installer and tool-management options.
