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

Hyper-V, VMs, WSL2, Docker and administrator access are not general CLI prerequisites. Follow the [executable setup and update commands](setup.md). The default `civ doctor` profile is `pure-mcap`; it also checks the supplied source/kit layout and workspace. An empty directory is not a workshop kit.

## Intended support and execution evidence

The intended native participant support remains Windows AMD64 and Linux AMD64. The accepted Linux AMD64 assessment used the approved WSL2 route. Bare-host Linux AMD64 was not executed.

| Platform / route | Accepted execution evidence | Remaining limits |
| --- | --- | --- |
| Native Windows AMD64 | Accepted on the existing Windows host with CPython 3.12.13 and uv 0.11.2. Authenticated participant installation, fresh-shell command resolution, actual-kit doctor and warm-up, the eight-command workflow, matching and mismatched source checks, updates, constraint refresh, source replacement, and matching-wheel resolver-offline recovery are recorded in #107, #123, the post-158 report, and that wave's fresh-validated results. | Existing-host evidence only. This does not establish a clean-machine result or externally enforced network denial. Fresh-shell checks used the existing persisted PATH; no PATH or profile changes were made. |
| Native Linux AMD64 | Intended support target. Bare-host execution was not performed. | The accepted Linux AMD64 assessment route is WSL2 and is not evidence of bare-host Linux execution. |
| Approved WSL2 Linux AMD64 assessment route | Ubuntu 26.04 LTS x86_64, CPython 3.12.13, uv 0.11.2 and Git 2.53.0. Authenticated GitHub HTTPS installation of the exact participant source, direct commands, actual-kit doctor, synthetic workflow, and matching-wheel resolver-offline recovery are recorded in #122 and #124. | Existing WSL2 host. Fresh-shell command resolution used process-local PATH. This does not establish bare-host Linux, anonymous GitHub access, or externally enforced network denial. |
| Optional route #142 | Completed separately with bounded receipts for the approved WSL2 participant workflow and the preloaded historical container image. | The historical container source differs from the qualified participant source. These receipts do not establish general container support or bare-host Linux qualification. |
| Additional Pi ARM64 test environment | Existing Debian 13.7 container on Raspberry Pi 5, CPython 3.12.13 and uv 0.12.1; GitHub-main participant install, updates/constraints, relocated wheel recovery and source replacement passed; 166 expected checks, with identical JSON/ROS2-CDR repeat artifacts. | ARM64 container execution only; no bare-host, actual-kit, persistent PATH or external network denial; does not qualify Windows or native Linux AMD64. |

The accepted participant source pin remains main commit `37b05439f73376ccc9131697a472ad0ee0fe3c36`. Authenticated GitHub access was exercised using existing authorized credentials: SSH for #107 and HTTPS through the existing GitHub credential helper for #122. Anonymous access was not tested. Private raw receipts and synthetic outputs stay outside Git.

## Qualification plan

1. Use existing native Windows and native Linux environments first. Record OS/architecture, Python patch, uv/Git, source commit and resolved dependencies. Use fresh tool directories and isolated caches; run outside the checkout through the installed `civ` executable.
2. Exercise `doctor`, `inspect`, `sample`, `submission-init`, `detect`, `clip`, `score` and `report` with synthetic inputs. Check source-matching labels, deterministic artifacts, packaged templates and exclusion of organizer modules. Record actual-kit checks separately.
3. Exercise already-installed handling, main-following updates and constraint refresh. Use a disposable source for two-commit updates; do not change production main for a test.
4. Prepare matching wheel sets while connected, record hashes, relocate them, then install with `--offline --no-index --no-python-downloads` and a fresh cache. Existing compatible Python must be available. Resolver-offline evidence does not prove external network denial.
5. Track optional WSL2 and container checks separately. Provision a dedicated machine only for a specific acceptance check that needs it, with concrete approval of resources and controls. Never disrupt the host network or existing distros to manufacture a pass.

Issues #87, #88 and #122-#124 are complete under the accepted Windows and approved WSL2 assessment scope. #121's environment-selection and control record is complete. Issue #142 is complete separately for its bounded optional WSL2 and historical-container receipts. Issue #107 records the accepted authenticated installation; anonymous access is outside that result. Bare-host Linux and externally enforced network denial remain unverified. Missing Hyper-V metadata does not block the accepted checks. Historical Phase 5 workstation/kit declarations keep their original, narrower scope.
