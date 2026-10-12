# Participant runtime requirements

Install `civ`, then run the [QuickStart](quickstart.md) with supplied local recordings, EventSpecs and practice labels matched to the source. Participant machine preparation happens before the workshop. Test infrastructure is separate from these runtime requirements.

| Workflow | Participant needs |
| --- | --- |
| Core CLI on native Windows AMD64 or native Linux AMD64 | CPython >=3.10,<3.13, with 3.12 recommended; uv for the documented installation; writable local workspace and supplied MCAP/EventSpec inputs |
| Connected Git installation and updates | Git, network access and authorized repository access while private; the participant subdirectory, not organizer-root metadata |
| Scoring and submission | Matching practice labels for scoring; report, figure and reproduction script for the metadata-only bundle |
| Wheel installation without downloads | uv and compatible Python already available, participant wheel and matching dependency wheels for the OS/architecture/Python version |
| Optional visual review | Lichtblick, or PlotJuggler with a compatible layout; `civ sample` remains available without a viewer |
| Optional Linux route on Windows | An existing WSL2 Linux environment; use the Linux installation inside it |
| Optional container recovery | A compatible container engine and the supplied image, with its own workflow-specific requirements |
| Historical release-target doctor profile | ROS 2 Lyrical and the profile's visual/runtime assets; these do not apply to default pure-MCAP analysis |

The participant metadata installs `cel-python==0.5.0`, `mcap>=1.4.0,<2`, `mcap-ros2-support>=0.5.7,<0.6` and `pyyaml>=6.0.2,<7`, plus their resolved transitive dependencies. No separate ROS installation is needed to decode supported embedded ROS 2 schemas. Unsupported encodings still fail explicitly.

Hyper-V, VMs, WSL2, Docker and administrator access are not general CLI prerequisites. Follow the [executable setup and update commands](../participant/README.md). The default `civ doctor` profile is `pure-mcap`; it also checks the supplied source/kit layout and workspace. An empty directory is not a workshop kit.

## Intended support and execution evidence

The intended native matrix is Windows AMD64 and Linux AMD64. WSL2 is optional. Intended support does not establish complete platform qualification.

| Platform / route | Execution on 2026-10-12 | Remaining limits |
| --- | --- | --- |
| Native Windows 11 AMD64 | CPython 3.12.13, uv 0.11.2; exact-main participant Git installation via existing authorized SSH; all eight public commands; deterministic repeated synthetic workflow; metadata-only bundle; current-main and disposable two-commit updates; constraint refresh/source replacement; relocated matching wheel installation with fresh cache and uv offline mode | Existing developer host, process-local PATH, doctor checks against synthetic source-directory inputs; actual supplied kit, persistent fresh-shell PATH and externally enforced network-isolation acceptance remain separate |
| Native Linux AMD64 | Not executed in this run | An accessible native AMD64 environment is still needed; previous ARM64 execution is preserved but does not qualify AMD64 |
| Optional WSL2 Linux AMD64 | Existing Ubuntu 26.04 LTS x86_64, CPython 3.12.13 and uv 0.11.2; isolated tools/caches; all eight commands from an exact-main export and relocated Linux wheels; repeated artifacts, disposable Git updates and constraint/source replacement passed | Exact-main export/local Git probe, not authenticated GitHub install/update qualification; process-local PATH and doctor checks against the source directory; not native Linux or a clean physical host |
| Additional Pi ARM64 test environment | Existing Debian 13.7 container on Raspberry Pi 5, CPython 3.12.13 and uv 0.12.1; GitHub-main participant install, updates/constraints, relocated wheel recovery and source replacement passed; 166 expected checks, with identical JSON/ROS2-CDR repeat artifacts | ARM64 container execution only; no bare-host, actual-kit, persistent PATH or external network denial; does not qualify Windows or native Linux AMD64 |

Windows Git evidence used main commit `37b05439f73376ccc9131697a472ad0ee0fe3c36`. The HTTPS attempt failed on private-repository authentication; the existing SSH transport succeeded without credential changes. Frozen backups have separate wheel/dependency hashes. Private raw receipts and synthetic outputs stay outside Git.

## Qualification plan

1. Use existing native Windows and native Linux environments first. Record OS/architecture, Python patch, uv/Git, source commit and resolved dependencies. Use fresh tool directories and isolated caches; run outside the checkout through the installed `civ` executable.
2. Exercise `doctor`, `inspect`, `sample`, `submission-init`, `detect`, `clip`, `score` and `report` with synthetic inputs. Check source-matching labels, deterministic artifacts, packaged templates and exclusion of organizer modules. Record actual-kit checks separately.
3. Exercise already-installed handling, main-following updates and constraint refresh. Use a disposable source for two-commit updates; do not change production main for a test.
4. Prepare matching wheel sets while connected, record hashes, relocate them, then install with `--offline --no-index --no-python-downloads` and a fresh cache. Existing compatible Python must be available. Resolver-offline evidence does not prove external network denial.
5. Track optional WSL2 and container checks separately. Provision a dedicated machine only for a specific acceptance check that needs it, with concrete approval of resources and controls. Never disrupt the host network or existing distros to manufacture a pass.

Issues #87, #88 and #121-#124 retain completed evidence and remain open until their remaining acceptance is demonstrated. Missing Hyper-V metadata does not block native checks. Optional WSL2/container checks are tracked in #142. Historical Phase 5 workstation/kit declarations keep their original, narrower scope.
