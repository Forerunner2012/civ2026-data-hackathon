# ROS 2 Lyrical Phase 1 acceptance record

Status: **complete — Lyrical is the forward participant and integrated-acceptance target**

Recorded: 2026-08-06

## Selected environment

The forward CPU environment is the official linux-amd64 ROS 2 Lyrical Luth base on Ubuntu 26.04
LTS. The mutable tag used for discovery was `ros:lyrical-ros-base-resolute`; acceptance pins the
base as:

`docker.io/library/ros@sha256:122a787d0eb7e1b2c18370e35ef394332db5c11d242bea6f05f2b2911e26b04d`

The prepared organizer image was `civ-phase1:lyrical-resolute`, local image ID
`sha256:abf90cdd46b446a185f24bc2a7097a49b34b57c415ff227e02ae55c17c7cd423`. It is derived from the
pinned official image and is local runtime state, not a release artifact. The retained Humble image
remains the compatibility floor recorded in [the Kashiwa acceptance](kashiwa-acceptance.md); it is
not the forward release target.

The official image provides Ubuntu 26.04 LTS, ROS distribution `lyrical`, Linux x86-64,
`ros-lyrical-ros-base` package `0.13.0-3resolute.20260606.042427`, and `ros-lyrical-ros2cli`
package `0.40.7-1resolute.20260606.033717`. Its system interpreter is CPython 3.14.4. The project
contract deliberately remains Python 3.10–3.12, so acceptance uses a separately prepared, pinned
CPython 3.12.11 environment rather than silently widening supported Python.

## Deterministic floors and resolved sidecar

The participant-facing minimums come from `pyproject.toml`; `uv.lock` fixes the accepted resolution.
Environment preparation additionally pins `uv` and the managed acceptance interpreter exactly.

| Component | Supported floor or preparation pin | Resolved in this run |
|---|---|---|
| ROS / OS / architecture | Lyrical / Ubuntu 26.04 / linux-amd64 CPU; base digest above | Lyrical / Ubuntu 26.04 / x86-64 |
| Python | `>=3.10,<3.13`; acceptance pin `==3.12.11` | CPython 3.12.11 |
| `civ-workshop` | `>=0.1.0` and the current `v1alpha1` artifact contracts | 0.1.0 |
| `uv` preparation tool | `==0.11.2` | 0.11.2 |
| `mcap` | `>=1.4.0,<2` | 1.4.0 |
| `mcap-ros2-support` | `>=0.5.7,<0.6` | 0.5.7 |
| `PyYAML` | `>=6.0.2,<7` | 6.0.3 |
| `cel-python` | `==0.5.0` | 0.5.0 |

Dependencies and the managed interpreter were downloaded before acceptance. The acceptance
container then mounted that dependency volume read-only. No dependency, cache, virtual environment,
container state, source bag, label pack, clip, submission bundle, or runtime output is committed.

## Offline Kashiwa replay

The corrected steering workflow ran unchanged against the authorized Kashiwa source from
[the sealed acceptance](kashiwa-acceptance.md). The container used `--network none`; the repository
and 7,875,976,476-byte source bag were read-only; only
`%LOCALAPPDATA%\Temp\civ-phase1-kashiwa-steering-lyrical` was writable. No GPU was exposed.

The public path completed `inspect -> detect -> clip -> score -> report`. The authoritative result
remained TP 2, FP 3, FN 1; precision 0.4, recall 0.666666666667, F1 0.5, and mean matched temporal
IoU 0.644663772045. All five evidence clips reopened as valid MCAP.

| Artifact | Lyrical SHA-256 | Comparison with sealed Humble output |
|---|---|---|
| `events.jsonl` | `798d05a6ebc46536d0aa32b0f03911f47e2b72ffd41bb11224a61c895e3490a9` | byte-identical |
| `metrics.json` | `846411d0b811930083076f1167b0e573f40074dad84aa6954ff10327364aa22b` | byte-identical |
| `run-manifest.json` | `3f42f69ac4df9b1c78141a78140da01e8c76c3b532357048f62fcb0216750a96` | byte-identical |
| `submission.zip` | `31f4eb3ad1cc3c003e0dc5474dad52d7a08ece183a095b3ef0a50c1e5588ca9c` | byte-identical |

The 10,596-byte metadata-only bundle was rebuilt in a second fresh, network-disabled container and
retained the same SHA-256. The external working directory contained 24 files totalling 80,176,817
bytes, including 80,085,980 bytes of evidence clips and local telemetry.

GNU `time -v` recorded zero socket messages sent or received for every command:

| Command | Wall time | Peak RSS | File-system input blocks | File-system output blocks |
|---|---:|---:|---:|---:|
| `civ inspect` | 80.93 s | 107,904 KB | 15,362,103 | 0 |
| `civ detect` | 100.06 s | 109,824 KB | 27,589,765 | 0 |
| `civ clip` | 101.04 s | 83,652 KB | 24,143,303 | 0 |
| `civ score` | 0.58 s | 38,120 KB | 145 | 0 |
| `civ report` | 1.34 s | 38,760 KB | 156,611 | 0 |

The measured path totalled approximately 283.95 seconds. As with the Humble proof, Docker Desktop's
Windows bind-mount I/O dominates the three bag-reading commands and is not a native-Linux benchmark.

## Compatibility correction and routed work

The replay exposed one Python 3.12 path-normalization defect at the existing public seam:
`civ report .` resolved the report figure to an absolute path but kept the submission root relative.
A public-CLI regression test now locks this invocation, and the report boundary normalizes the root
once before validation and bundling. The fix changes no command, artifact contract, or bundle bytes.

French transfer issue #7 and the integrated Phase 1 gate in issue #11 must use this pinned Lyrical
environment and the same prepared dependency floor. Tier IV `ros2idl` decoding remains explicitly
out of scope and deferred to issue #13, including the organizer's external notes and pinned source
hashes.
