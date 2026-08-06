# Kashiwa Phase 1 acceptance record

Status: **complete — the external Kashiwa label pack is sealed and the candidate has been scored
without hiding its boundary errors or false positives**

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

The bag, descriptor, organizer labels, evidence clips, caches, submission bundle, and all
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
| `7266f77d…715f228` | 3.000915–5.220780 s | 2.219866 s | 18° | organizer-classified false positive |
| `a960a16f…15c0ed1` | 19.000892–45.600922 s | 26.600030 s | 16° | covers reviewed 23.5–44 s episode |
| `71d3490d…eee6340` | 55.640932–65.281312 s | 9.640381 s | 13° | covers reviewed missing 60–65 s turn |
| `9502b726…24447ed7` | 91.740873–100.960918 s | 9.220045 s | 12° | contains true ~96 s turn but is too broad for 0.5 IoU |
| `a5d2609e…0cb86e9` | 103.980911–104.780927 s | 0.800016 s | 10° | organizer-classified false positive |

- Byte-stable `events.jsonl` SHA-256 across Windows and the exact Humble container:
  `798d05a6ebc46536d0aa32b0f03911f47e2b72ffd41bb11224a61c895e3490a9`.

The external authoritative label pack contains three organizer-reviewed manoeuvres: 23.5–44 s,
60–65 s, and 96.440476–97.076299 s. Its SHA-256 is
`1ee742010744686c07b552aed2c6192622613f5ff9734ec3160d5286db94f201`. The pack remains outside
the repository and participant artifacts.

## Clip, score, and report results

- All five evidence clips reopen as valid MCAP and contain exactly the six declared dense topics.
- Clip sizes are 4,663,801; 35,292,537; 16,161,201; 16,978,226; and 6,990,215 bytes.
- Total clip size is 80,085,980 bytes, down from five copies of the 7,875,976,476-byte input.
- Authoritative scoring result: TP 2, FP 3, FN 1; precision 0.4, recall 0.666666666667,
  F1 0.5, and mean matched temporal IoU 0.644663772045.
- The false positives include the organizer-rejected 3.001–5.221 s and 103.981–104.781 s clips.
  The remaining FP/FN pair comes from the 91.741–100.961 s candidate containing, but failing the
  0.5-IoU threshold against, the much shorter third label.
- Exact-container metadata-only bundle size: 10,596 bytes; SHA-256:
  `31f4eb3ad1cc3c003e0dc5474dad52d7a08ece183a095b3ef0a50c1e5588ca9c`.
- Bundle entries: EventSpec, `events.jsonl`, figure, `metrics.json`, `report.md`, reproduction entry,
  and `run-manifest.json`. It contains no bag, clip, or label pack.
- External working-directory disk use after the complete run: 80,113,928 bytes across 27 files.

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

## Closure and routed follow-up

- Visual classification is complete and the three-interval external Kashiwa label pack is sealed.
- Candidate quality is intentionally recorded rather than tuned against the sealed labels: false
  positives and the broad third prediction demonstrate why interval boundaries remain a scored
  participant decision. They do not invalidate the public workflow proof.
- GitHub issue #12 owns the ROS 2 Lyrical/Ubuntu 26.04 rehearsal and deterministic minimum-version
  floors before French transfer and attendee release.
- GitHub issue #13 owns the later Tier IV `ros2idl` investigation with the organizer's external,
  pinned-source setup notes.
