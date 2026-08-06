# Kashiwa Phase 1 acceptance record

Status: **partial — three organizer observations are covered; two additional steering candidates
still need visual classification**

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
runtime outputs remained outside the repository. The corrected exact-container outputs were written
to `%LOCALAPPDATA%\Temp\civ-phase1-kashiwa-steering-humble-v2`.

## Inspection and selected signals

`civ inspect` decoded the real MCAP deterministically. Embedded `ros2msg` schemas now expose nested
field paths. Five `ros2idl` schemas remain explicitly unsupported for field discovery; none is on
the candidate detector path.

| Topic | Schema | Count | Rate | Selected field or evidence role |
|---|---|---:|---:|---|
| `/pix_hooke/v2a_steerstafb` | `pix_hooke_driver_msgs/msg/V2aSteerStaFb` | 5,219 | 48.611703 Hz | `vcu_chassis_steer_angle_fb` detector signal, degrees |
| `/pix_hooke/v2a_drivestafb` | `pix_hooke_driver_msgs/msg/V2aDriveStaFb` | 5,219 | 48.611703 Hz | `vcu_chassis_speed_fb` evidence, m/s |
| `/pix_hooke/v2a_vehiclestafb` | `pix_hooke_driver_msgs/msg/V2aVehicleStaFb` | 5,214 | 48.565131 Hz | indicator evidence |
| `/localization/kinematic_state` | `nav_msgs/msg/Odometry` | 4,204 | 39.157617 Hz | yaw-rate evidence |
| `/perception/object_recognition/is_object_detected` | `std_msgs/msg/Bool` | 1,049 | 9.770775 Hz | `data` |
| `/sensing/camera/traffic_light/image_raw/compressed` | `sensor_msgs/msg/CompressedImage` | 228 | 2.123677 Hz | visual evidence |

The candidate EventSpec is [`examples/kashiwa/right_turn.yaml`](../../examples/kashiwa/right_turn.yaml).
It uses a real Pix Hooke CDR field, CEL, timing, and evidence declarations. The mandatory evidence
set contains only topics present in every candidate window. Sparse `detected_object` markers remain
available in the full bag for optional conflict-geometry work but are not required in every clip.

## Detector observation

The first candidate incorrectly ANDed yaw rate with object presence. Organizer review showed why that
proxy is unsuitable for the scored manoeuvre interval:

- The first accepted turn is a long episode, approximately 23.5–44 s. A vehicle in the intersection
  interrupts it, the steering remains held while the ego vehicle waits, and a pedestrian jaywalks at
  the end. The yaw-only candidate covered only 39.358–41.225 s.
- A turn at approximately 60–65 s was missing. Every inspected yaw source records it, but
  `object_detected` is false for the entire window, so the context gate suppressed it.
- The previously detected interval near 96 s is also visually accepted.

Yaw-only diagnostic intervals achieved approximate best IoUs of 0.328 and 0.201 against the first
two organizer windows. A Pix Hooke steering threshold of 10 degrees, 2-second debounce, and
30-second maximum produced approximate best IoUs of 0.771 and 0.519. Adding yaw direction did not
materially alter those boundaries. The steering baseline therefore replaces the yaw-and-object
condition; yaw, speed, indicator state, object presence, and camera remain evidence.

The corrected candidate emits five intervals:

| Event | Relative interval | Duration | Initial steering | Review status |
|---|---:|---:|---:|---|
| `7266f77d…715f228` | 3.000915–5.220780 s | 2.219866 s | 18° | pending |
| `a960a16f…15c0ed1` | 19.000892–45.600922 s | 26.600030 s | 16° | covers reviewed 23.5–44 s episode |
| `71d3490d…eee6340` | 55.640932–65.281312 s | 9.640381 s | 13° | covers reviewed missing 60–65 s turn |
| `9502b726…24447ed7` | 91.740873–100.960918 s | 9.220045 s | 12° | contains previously accepted ~96 s turn |
| `a5d2609e…0cb86e9` | 103.980911–104.780927 s | 0.800016 s | 10° | pending |

- Byte-stable `events.jsonl` SHA-256 across Windows and the exact Humble container:
  `798d05a6ebc46536d0aa32b0f03911f47e2b72ffd41bb11224a61c895e3490a9`.

This is a detector candidate, not ground truth. The external label pack used below mirrors the
five provisional intervals solely to exercise the sealed-label scoring interface. It must not be treated
as a reviewed Kashiwa label.

## Clip, score, and report results

- All five evidence clips reopen as valid MCAP and contain exactly the six declared dense topics.
- Clip sizes are 4,663,801; 35,292,537; 16,161,201; 16,978,226; and 6,990,215 bytes.
- Total clip size is 80,085,980 bytes, down from five copies of the 7,875,976,476-byte input.
- Scoring-interface result with the external mirror pack: TP 5, FP 0, FN 0, F1 1.0. This validates
  only the sealed-label interface; it is not an accuracy claim.
- Exact-container metadata-only bundle size: 10,410 bytes; SHA-256 stable across fresh
  network-disabled builds:
  `8ea429d6ec9547f3efcfee232907044b4bd222c35209528201d176d0143c7173`.
- Bundle entries: EventSpec, `events.jsonl`, figure, `metrics.json`, `report.md`, reproduction entry,
  and `run-manifest.json`. It contains no bag, clip, or label pack.
- External working-directory disk use after the complete run: 80,110,724 bytes across 22 files.

## Host and offline telemetry

Windows proof host: Microsoft Windows 11 Pro 64-bit, version 10.0.26200, build 26200. The corrected
detector ran in 15.1 seconds and produced byte-identical events to the Humble container; inspection
had already succeeded against the same bag and schemas.

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
| `civ detect` | 97.35 s | 116,564 KB | 27,626,824 | 0 |
| `civ clip` | 92.30 s | 80,352 KB | 24,145,546 | 0 |
| `civ score` | 0.73 s | 29,428 KB | 44,060 | 0 |
| `civ report` | 1.39 s | 30,576 KB | 156,573 | 0 |

Inspection plus the corrected detector-to-report measurements total approximately 281.96 seconds.
The run is dominated by reading a 7.9 GB file through a Docker Desktop bind mount and is not
representative of a native Linux disk.

## Platform, version, and deferred-schema decisions

- Humble on Ubuntu 22.04 remains a proven compatibility floor for the supplied Kashiwa recording.
  The forward participant/release target is ROS 2 Lyrical Luth on Ubuntu 26.04, the latest stable OSS
  LTS, subject to a dedicated rehearsal rather than silently changing this acceptance environment.
- Submitted metadata will carry deterministic minimum supported tool-version floors. Actual command
  timings, peak memory, and host/container identity remain in this organizer acceptance sidecar so
  local measurements do not make the metadata bundle nondeterministic.
- Five `ros2idl` topics include Tier IV/Autoware vehicle-status types that may later be useful. The
  organizer has external Lyrical setup notes with pinned source hashes. IDL decoding and those notes
  will be investigated in a later phase; the current Pix Hooke `ros2msg` steering/speed path does not
  depend on them.

## Open gates

1. Review the 3.001–5.221 s and 103.981–104.781 s steering candidates in PlotJuggler and classify
   each as a labelled right-turn manoeuvre, a duplicate fragment, or a false positive.
2. Convert the three confirmed observations and those two classifications into the sealed Kashiwa
   label pack; do not use the external mirror pack as ground truth.
3. Rehearse the same public contracts on ROS 2 Lyrical/Ubuntu 26.04 and record minimum supported tool
   versions before the attendee release is frozen.
