# French Phase 1 transfer acceptance record

Status: **complete — the unchanged Phase 1 contracts transfer to the representative Reims chunk**

Recorded: 2026-08-06

## Authorized source

- Organizer-local path: `D:\Bags\Data Hackathon\2025-07-30 Recording sessions\rosbag2_2025_07_31-13_24_53\rosbag2_2025_07_31-13_24_53_0.mcap`
- Adjacent descriptor: `metadata.yaml`, rosbag2 metadata version 5, MCAP storage, CDR serialization
- Selected chunk: first of nine files in the recording; no other chunk was copied or processed
- Size: 3,221,880,955 bytes
- SHA-256: `0a0817b3afc85796182c77c8dd8d9e5b84b0ee12f28b3b3fa881d3166e3035ca`
- Duration: 261,631,795,777 ns
- Start time: 1,753,961,093,092,125,160 ns
- Descriptor message count: 127,102
- File modified: 2025-07-31 11:29:14 UTC

The source, descriptor, diagnostic frames, organizer label, evidence clip, submission bundle, and
all runtime output remained outside the repository. Final outputs were written to
`%LOCALAPPDATA%\Temp\civ-phase1-french-lyrical-final-v2`.

## Inspection and signal choice

`civ inspect` decoded all eight topics in the selected chunk through the same command and inventory
contract used for Kashiwa. Every schema is embedded `ros2msg`; inspection reported no warnings.

| Topic | Schema | Count | Rate | Selected field or evidence role |
|---|---|---:|---:|---|
| `/zed/zed_node/imu/data` | `sensor_msgs/msg/Imu` | 49,982 | 191.039472 Hz | `angular_velocity.z`, rad/s |
| `/fix_velocity` | `geometry_msgs/msg/TwistWithCovarianceStamped` | 1,046 | 3.997985 Hz | `twist.twist.linear.{x,y,z}`, m/s |
| `/fix` | `sensor_msgs/msg/NavSatFix` | 1,046 | 3.997985 Hz | position evidence |
| `/zed/zed_node/obj_det/objects` | `zed_msgs/msg/ObjectsStamped` | 5,008 | 19.141404 Hz | object evidence |
| `/zed/zed_node/rgb/image_rect_color/compressed` | `sensor_msgs/msg/CompressedImage` | 5,009 | 19.145227 Hz | visual evidence |

The transfer EventSpec is [`examples/french/left_turn.yaml`](../../examples/french/left_turn.yaml).
It binds only real fields and expresses speed as the squared GNSS velocity-vector magnitude in the
existing CEL condition. It introduces no French-specific runner, decoder, command, interval, or
artifact adapter.

## Handedness and representative event

An initial 0.08 rad/s yaw diagnostic produced positive episodes at approximately 144.439–148.442 s
and 177.708–179.444 s. Six negative-yaw episodes were right turns or rightward road bends. Camera
frames before, through, and after the positive episodes showed:

- 144–149 s is the representative left turn into the side street, crossing the opposing lane;
- the 178 s episode is a low-speed lane shift around street furniture, not an intersection turn.

The genuine turn carried approximately 4.57–6.21 m/s in sampled GNSS velocity, while the lane shift
dropped to approximately 0.81–1.93 m/s before accelerating. A positive-yaw condition plus a 4 m/s
speed floor rejects the lane shift while preserving Kashiwa's 0.5-second minimum duration and
2-second merge gap. The public-CLI regression fixture contains a positive left turn, a negative
right turn, a low-speed lane shift, and a sub-minimum positive deflection, and asserts that only the
left-turn interval is emitted.

The final candidate is event `30dcfd78…8a780ad`, interval 144.439252–148.442409 s, with trigger
values yaw rate 0.083081 rad/s and GNSS velocity components (-3.777, -2.650, -0.041) m/s. The
independent external organizer label uses the rounded visual interval 144–149 s rather than the
detector's threshold timestamps. Its label-pack SHA-256 is
`fd745fad80d4d9a143f262077d34bfec4489b169f045d3e56d382f3ff1bcc9b5`.

## Clip, score, and report results

- The evidence clip reopens as valid MCAP and contains exactly the five declared French evidence
  topics.
- Clip size: 25,587,790 bytes; SHA-256:
  `f7906be7ecda84429c76344c94f82e904337e5b1b7666d3bc2fce4bae7e0e3ed`.
- Authoritative result: TP 1, FP 0, FN 0; precision, recall, and F1 are 1.0; mean temporal IoU is
  0.800631349.
- `events.jsonl` SHA-256:
  `c6d9279151eb46aaed42d71ef835606b8d95e7287379ad2e3a1b16b4cf86f69d`.
- `metrics.json` SHA-256:
  `8313a56024091c8aa31a48019867b8888dc858ea2478eb6cab14e7372055b0b2`.
- `run-manifest.json` SHA-256:
  `e7714d1069a254d2b13239ca1d9750048090d02ecc2cb7fc7acab76972e95d19`.
- Metadata-only bundle size: 6,055 bytes; SHA-256:
  `fd9a7e7437c11cc8e8e042fa495b39ffaae6fdb6fe0acd8fbe28eab3218de168`.
- A second fresh, network-disabled container rebuilt the bundle byte-for-byte.
- External final-directory disk use: 25,607,727 bytes across 20 files, including local telemetry.

## Forward environment and offline telemetry

The run used the exact forward environment from
[`lyrical-acceptance.md`](lyrical-acceptance.md): official ROS 2 Lyrical / Ubuntu 26.04 linux-amd64
base digest `sha256:122a787d0eb7e1b2c18370e35ef394332db5c11d242bea6f05f2b2911e26b04d`,
managed CPython 3.12.11, and the frozen production dependency set. Dependencies were prepared before
acceptance. Every command then ran with `--network none`, no GPU, the repository and source bag
read-only, the dependency volume read-only, and only the external output directory writable.

GNU `time -v` reported zero socket messages sent or received for every command:

| Command | Wall time | Peak RSS | File-system input blocks | File-system output blocks |
|---|---:|---:|---:|---:|
| `civ inspect` | 28.54 s | 43,696 KB | 6,345,411 | 0 |
| `civ detect` | 81.32 s | 44,992 KB | 12,694,631 | 0 |
| `civ clip` | 25.18 s | 62,852 KB | 6,577,648 | 0 |
| `civ score` | 0.68 s | 37,912 KB | 136 | 0 |
| `civ report` | 0.93 s | 38,804 KB | 50,141 | 0 |

The complete measured path totalled approximately 136.65 seconds. Docker Desktop bind-mount I/O
dominates the bag-reading commands, so these measurements are acceptance evidence rather than a
native-Linux performance claim.

At the application boundary, inspection reads the 3,221,880,955-byte source once, detection reads it
twice (one provenance hash plus one signal scan), and clipping reads it once. The three bag-reading
commands therefore consume 12,887,523,820 logical source bytes. Retained principal outputs are the
3,421-byte inspection JSON, 410-byte normalized event stream, 25,587,790-byte evidence clip,
707-byte metrics file, and 6,055-byte bundle; the complete external directory occupies 25,607,727
bytes. GNU `time` block counters remain in the table as host-I/O diagnostics, not byte substitutes.

## Side-by-side contract differences

| Concern | Kashiwa | French transfer | External contract |
|---|---|---|---|
| Traffic target | right turn | left turn crossing opposing traffic | unchanged EventSpec candidate |
| Detector source | Pix Hooke steering angle | ZED yaw rate plus GNSS velocity vector | declarative bindings and CEL |
| Direction | steering angle `>= 10` degrees | yaw rate `>= 0.08` rad/s | condition value/sign only |
| Motion floor | none | velocity magnitude squared `>= 16.0` m2/s2 | existing CEL expression |
| Timing | 0.5 s minimum, 2 s merge gap | 0.5 s minimum, 2 s merge gap | unchanged |
| Evidence | Pix Hooke, odometry, object flag, camera | GNSS, ZED IMU, objects, camera | same evidence contract |
| Runner and outputs | `inspect/detect/clip/score/report`, interval, manifest, metrics, bundle | identical | unchanged |

No Phase 1 external contract change was required. Any future multi-chunk dataset abstraction or
Tier IV `ros2idl` support remains later-phase work rather than a hidden French-only seam. GitHub issue
#7 is complete; the pinned Lyrical environment and both accepted datasets now feed the integrated
Phase 1 gate in issue #11.
