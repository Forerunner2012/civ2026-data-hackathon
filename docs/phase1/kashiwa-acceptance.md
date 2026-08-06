# Kashiwa Phase 1 acceptance record

Status: **partial — organizer visual confirmation and the telemetry-contract decision remain open**

Recorded: 2026-08-06

## Authorized source

- Organizer-local path: `D:\Bags\Data Hackathon\2025-07-27 Final Data sample Tsukada Labs\hackathon_data\final_route_02\final_route_2_0.mcap_0.mcap`
- Adjacent descriptor: `metadata.yaml`, rosbag2 metadata version 5, MCAP storage, CDR serialization
- Size: 7,875,976,476 bytes
- SHA-256: `b9066692c358bb7aac7bfaa4038dc2f54dc63a02eeb245a014af732a5cc59712`
- Duration: 107,360,977,739 ns
- Start time: 1,756,268,534,308,303,149 ns
- Descriptor message count: 560,611
- File modified: 2025-08-31 19:50:08 UTC

The bag, descriptor, provisional organizer labels, evidence clip, caches, submission bundle, and all
runtime outputs remained outside the repository. The external working directory used on Windows was
`%LOCALAPPDATA%\Temp\civ-phase1-kashiwa-20260806-yaw`; exact-container outputs were written to
`%LOCALAPPDATA%\Temp\civ-phase1-kashiwa-humble`.

## Inspection and selected signals

`civ inspect` decoded the real MCAP deterministically. Embedded `ros2msg` schemas now expose nested
field paths. Five `ros2idl` schemas remain explicitly unsupported for field discovery; none is on
the candidate detector path.

| Topic | Schema | Count | Rate | Selected field or evidence role |
|---|---|---:|---:|---|
| `/localization/kinematic_state` | `nav_msgs/msg/Odometry` | 4,204 | 39.157617 Hz | `twist.twist.angular.z` |
| `/perception/object_recognition/is_object_detected` | `std_msgs/msg/Bool` | 1,049 | 9.770775 Hz | `data` |
| `/perception/object_recognition/detected_object` | `visualization_msgs/msg/Marker` | 136 | 1.266754 Hz | object-context evidence |
| `/sensing/camera/traffic_light/image_raw/compressed` | `sensor_msgs/msg/CompressedImage` | 228 | 2.123677 Hz | visual evidence |

The candidate EventSpec is [`examples/kashiwa/right_turn.yaml`](../../examples/kashiwa/right_turn.yaml).
It uses real CDR fields, CEL, timing, and evidence declarations. No derivation is required for these
already-normalized signals.

## Detector observation

The localization field is angular velocity in rad/s, not angular acceleration. Its observed range is
`-0.3659635624258629` to `0.12175168003023576`. The historical instantaneous threshold
`yaw_rate <= -0.5 rad/s` therefore cannot fire on this route. At `-0.25`, the real timing and object
context produce two provisional intervals; PlotJuggler review must confirm whether the sign and both
intervals correspond to the intended right-turn manoeuvre.

That candidate emits two intervals:

- `ee7df0ff5795408a8a51759a0a6dcdb4b170925b5c6202fef552584e1e762d40`:
  1,756,268,573,666,554,460–1,756,268,575,533,441,579 ns, or
  39.358251–41.225138 s after bag start; duration 1,866,887,119 ns; trigger
  `yaw_rate=-0.26279298084794533`, `object_detected=true`.
- `7da224524fa6b5d1cd21205d90ef2238eb803c36d9a0ba0aafd925177543a9da`:
  1,756,268,630,748,779,481–1,756,268,631,384,602,075 ns, or
  96.440476–97.076299 s after bag start; duration 635,822,594 ns; trigger
  `yaw_rate=-0.30079431928938716`, `object_detected=true`.
- Byte-stable `events.jsonl` SHA-256 across fresh Windows directories and the exact Humble container:
  `93ea2a3d84e586fade0c171378175ec8dfc01d50a4af810f29cc0ca71853a451`.

This is a detector candidate, not ground truth. The external label pack used below mirrors the
provisional intervals solely to exercise the sealed-label scoring interface. It must not be treated
as a reviewed Kashiwa label.

## Clip, score, and report results

- Both evidence clips reopen as valid MCAP and contain exactly the four declared topics.
- First requested window: 37.358251–43.225138 s relative to bag start; actual message window:
  37.361915–43.217063 s; boundary differences +3.664 ms and -8.075 ms; size 5,283,242 bytes.
- Second requested window: 94.440476–99.076299 s; actual message window:
  94.454350–99.060243 s; boundary differences +13.874 ms and -16.056 ms; size 5,594,000 bytes.
- Scoring interface result with the external provisional pack: TP 2, FP 0, FN 0, F1 1.0.
- Metadata-only bundle size: 6,825 bytes.
- Bundle SHA-256, stable across repeated Windows builds:
  `21bf82946adf9162426885d31a680eec150e8124c0cd4bd685a4646a67dcf5f6`
- Exact-container bundle size: 6,816 bytes; SHA-256 stable across fresh network-disabled container
  builds: `e37783f6c531b298438a602bb1538c436424d4fa92fc8dd9177bedf44d5d44a1`.
- Bundle entries: EventSpec, `events.jsonl`, figure, `metrics.json`, `report.md`, reproduction entry,
  and `run-manifest.json`. It contains no bag, clip, or label pack.
- External working-directory disk use after the complete run: 10,890,492 bytes across 11 files.

## Host and offline telemetry

Windows proof host: Microsoft Windows 11 Pro 64-bit, version 10.0.26200, build 26200. The corrected
detect-to-report path ran successfully there in approximately 26.5 seconds from observed command
wall times; inspection had already succeeded against the same bag and schemas.

The exact target run used Ubuntu 22.04.5 LTS, ROS distribution `humble`, CPython 3.10.12, and
Linux amd64. The prepared acceptance image was `civ-phase1:humble-jammy` with image ID
`sha256:7b436200ca124a8bfc42d5ccedba66d35af6e3bcc44f68b3e1cf7c30ad3444f3`, derived from
`ros:humble-ros-base-jammy` digest
`sha256:7bea3d9aa2483d3ca34c8e30d921b79273b0913bd7dc64bebf51d082b5d107e4`.

Dependencies were prepared before acceptance. The complete acceptance path then ran in a fresh
container with `--network none`, no GPU access, the repository and bag mounted read-only, and only
the external output directory writable. GNU `time -v` reported zero socket messages sent or received
for every command.

| Command | Wall time | Peak RSS | File-system input blocks | File-system output blocks |
|---|---:|---:|---:|---:|
| `civ inspect` | 90.19 s | 105,668 KB | 15,362,066 | 2,712 |
| `civ detect` | 95.42 s | 74,908 KB | 24,373,124 | 0 |
| `civ clip` | 62.79 s | 67,212 KB | 16,368,928 | 0 |
| `civ score` | 0.45 s | 29,836 KB | 101 | 0 |
| `civ report` | 0.73 s | 31,000 KB | 21,377 | 0 |

The measured command total is approximately 249.58 seconds; the complete container invocation took
251.5 seconds. It is dominated by reading a 7.9 GB file through a Docker Desktop bind mount and is
not representative of a native Linux disk.

## Open gates and candidate-contract consequences

1. An organizer must open the route and extracted evidence in PlotJuggler, inspect the
   39.358–41.225 s and 96.440–97.076 s intervals, identify the actual manoeuvres, and record whether
   the negative yaw rate plus object and camera context support the right-turn definition.
2. `run-manifest.json` still lacks operation timings, peak memory, tool versions, and host/container
   identity. Adding nondeterministic telemetry directly would conflict with the current byte-stable
   bundle contract. Phase 2 must decide whether to normalize/exclude local measurements in the
   submitted manifest or keep this organizer acceptance record as the authoritative telemetry sidecar.
3. The five `ros2idl` inspection warnings are actionable and bounded. The candidate avoids those
   topics; supporting IDL schemas can remain a separate contract decision unless later routes require
   them.
