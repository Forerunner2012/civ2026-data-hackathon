# Tier IV `ros2idl` decoding decision

Status: **complete — retain explicit warnings; do not add IDL decoding to the attendee contract**

Recorded: 2026-08-26

## Decision

Keep the current `civ inspect` warning for embedded `ros2idl` schemas and keep `civ detect`
limited to fields the inspector can discover through its accepted `ros2msg` path. The five Tier IV
vehicle-status topics are useful organizer evidence, but none is required by the accepted Kashiwa
detector. Dynamic decoding would add a second type system and a measured 52.6 MB Python dependency
target; generated messages would add a source-build and ROS workspace contract. Neither cost is
justified for the participant baseline.

This decision adds no interface change to the Phase 2, contracts/data/evaluation, or
attendee/release specifications. A later extension may reconsider dynamic IDL decoding if a scored
detector actually requires one of these fields.

## Trace inventory and value

The authorized `final_route_02` trace is the same external Kashiwa input used by the
[sealed acceptance](../../phase1/kashiwa-acceptance.md). Each of these five channels contains
5,237 CDR messages at 48.779362 Hz. The ranges and value counts below came from one offline pass
with `rosbags==0.11.5`; they are measurements of this trace, not general Autoware guarantees.

| Topic | Embedded schema SHA-256 | Observed value | Detector or evidence value |
|---|---|---|---|
| `/vehicle/status/control_mode` | `cff319ad2f179f67d16b5af191cc7911cb41baebbe18aa46c1e85f39c1f8397d` | autonomous 4,826; disengaged 387; not-ready 24 | Useful state context or a veto, but not turn evidence. |
| `/vehicle/status/gear_status` | `b3245f9edfd9124545875530eb9990b07ba624f2f12496a963e6de2c4e092a41` | drive 4,831; neutral 382; reverse 24 | Useful motion-state evidence or a parking/reverse veto. |
| `/vehicle/status/steering_status` | `361db974a235bbea265b702ee4a2790f66a86743227b06fbefde4115e9567b87` | steering tire angle -0.412800014019 to 0.0501333326101 rad | Strongest detector candidate: a normalized analogue of the accepted Pix Hooke steering signal. The embedded definition declares left positive and right negative. |
| `/vehicle/status/turn_indicators_status` | `9c2c00cf92a6134f1154441a5c25b44c71fc1344a6af61504c40f32c116dc129` | disabled 4,850; right 387 | Useful intent/corroborating evidence, but too dependent on indicator use to be a sole detector. |
| `/vehicle/status/velocity_status` | `e60f36d3f2bfe01f31a3ffe8a33602f8f508a09729e5dc348d7d16bd52a9a47b` | longitudinal -0.08 to 3.21 m/s; lateral and heading rate always 0 | Longitudinal speed can gate motion. Lateral velocity and heading rate add no evidence in this recording. |

All five embedded root definitions are byte-compatible with the corresponding files at Tier IV
`autoware_auto_msgs` commit
[`624aae9feb142eb2a4e16069ed06bf4050ccc3ea`](https://github.com/tier4/autoware_auto_msgs/commit/624aae9feb142eb2a4e16069ed06bf4050ccc3ea):
[`ControlModeReport.idl`](https://github.com/tier4/autoware_auto_msgs/blob/624aae9feb142eb2a4e16069ed06bf4050ccc3ea/autoware_auto_vehicle_msgs/msg/ControlModeReport.idl),
[`GearReport.idl`](https://github.com/tier4/autoware_auto_msgs/blob/624aae9feb142eb2a4e16069ed06bf4050ccc3ea/autoware_auto_vehicle_msgs/msg/GearReport.idl),
[`SteeringReport.idl`](https://github.com/tier4/autoware_auto_msgs/blob/624aae9feb142eb2a4e16069ed06bf4050ccc3ea/autoware_auto_vehicle_msgs/msg/SteeringReport.idl),
[`TurnIndicatorsReport.idl`](https://github.com/tier4/autoware_auto_msgs/blob/624aae9feb142eb2a4e16069ed06bf4050ccc3ea/autoware_auto_vehicle_msgs/msg/TurnIndicatorsReport.idl), and
[`VelocityReport.idl`](https://github.com/tier4/autoware_auto_msgs/blob/624aae9feb142eb2a4e16069ed06bf4050ccc3ea/autoware_auto_vehicle_msgs/msg/VelocityReport.idl).

The MCAP summary also contains an unreferenced `HazardLightsReport` `ros2idl` schema. It has no
channel in this trace, so it is not one of the five topic contracts and produces no inspector
warning.

## Organizer pin and licence review

The external organizer note dated 2025-09-16 describes a much broader Jazzy custom-message replay
workspace. Only its repository metadata is recorded here; the private note, generated workspace,
and source trees remain outside this repository. GitHub resolved every recorded ref to the exact
40-character commit below. The licence file at each pin is Apache-2.0.

| Repository | Verified pin | Licence at the pin |
|---|---|---|
| [`autowarefoundation/autoware_adapi_msgs`](https://github.com/autowarefoundation/autoware_adapi_msgs) | [`a961390a6b9373757481cb6be25353b0ccd5d273`](https://github.com/autowarefoundation/autoware_adapi_msgs/commit/a961390a6b9373757481cb6be25353b0ccd5d273) | [Apache-2.0](https://github.com/autowarefoundation/autoware_adapi_msgs/blob/a961390a6b9373757481cb6be25353b0ccd5d273/LICENSE) |
| [`tier4/autoware_auto_msgs`](https://github.com/tier4/autoware_auto_msgs) | [`624aae9feb142eb2a4e16069ed06bf4050ccc3ea`](https://github.com/tier4/autoware_auto_msgs/commit/624aae9feb142eb2a4e16069ed06bf4050ccc3ea) | [Apache-2.0](https://github.com/tier4/autoware_auto_msgs/blob/624aae9feb142eb2a4e16069ed06bf4050ccc3ea/LICENSE) |
| [`autowarefoundation/autoware_cmake`](https://github.com/autowarefoundation/autoware_cmake) | [`fa3dc172fb6f24ec6103b00c41320d722a994136`](https://github.com/autowarefoundation/autoware_cmake/commit/fa3dc172fb6f24ec6103b00c41320d722a994136) | [Apache-2.0](https://github.com/autowarefoundation/autoware_cmake/blob/fa3dc172fb6f24ec6103b00c41320d722a994136/LICENSE) |
| [`autowarefoundation/autoware_msgs`](https://github.com/autowarefoundation/autoware_msgs) | [`f49c35c7a7b0110ad7bf5d91f67967833fd1c0d9`](https://github.com/autowarefoundation/autoware_msgs/commit/f49c35c7a7b0110ad7bf5d91f67967833fd1c0d9) | [Apache-2.0](https://github.com/autowarefoundation/autoware_msgs/blob/f49c35c7a7b0110ad7bf5d91f67967833fd1c0d9/LICENSE) |
| [`autowarefoundation/autoware.universe`](https://github.com/autowarefoundation/autoware.universe) | [`961950c714ec3bde43c8c814a7de9150a45e85b5`](https://github.com/autowarefoundation/autoware.universe/commit/961950c714ec3bde43c8c814a7de9150a45e85b5) | [Apache-2.0](https://github.com/autowarefoundation/autoware.universe/blob/961950c714ec3bde43c8c814a7de9150a45e85b5/LICENSE) |
| [`pixmoving-moveit/pix_driver`](https://github.com/pixmoving-moveit/pix_driver) | [`9feb55bd14f7bdf9c2e84acd05e0aced79e11df1`](https://github.com/pixmoving-moveit/pix_driver/commit/9feb55bd14f7bdf9c2e84acd05e0aced79e11df1) | [Apache-2.0](https://github.com/pixmoving-moveit/pix_driver/blob/9feb55bd14f7bdf9c2e84acd05e0aced79e11df1/LICENSE) |
| [`LRMPUT/pixkit_launch`](https://github.com/LRMPUT/pixkit_launch) | [`28a509eed8270a6b4d5b1793f5ed2c720d3b952d`](https://github.com/LRMPUT/pixkit_launch/commit/28a509eed8270a6b4d5b1793f5ed2c720d3b952d) | [Apache-2.0](https://github.com/LRMPUT/pixkit_launch/blob/28a509eed8270a6b4d5b1793f5ed2c720d3b952d/LICENSE); nested `pixkit_description` carries the same licence |
| [`autowarefoundation/ros2_socketcan`](https://github.com/autowarefoundation/ros2_socketcan) | [`822ca033c8ce934dc5a622d7bb80adb575522b33`](https://github.com/autowarefoundation/ros2_socketcan/commit/822ca033c8ce934dc5a622d7bb80adb575522b33) | Apache-2.0 in both [`ros2_socketcan`](https://github.com/autowarefoundation/ros2_socketcan/blob/822ca033c8ce934dc5a622d7bb80adb575522b33/ros2_socketcan/LICENSE) and [`ros2_socketcan_msgs`](https://github.com/autowarefoundation/ros2_socketcan/blob/822ca033c8ce934dc5a622d7bb80adb575522b33/ros2_socketcan_msgs/LICENSE) |
| [`tier4/tier4_autoware_msgs`](https://github.com/tier4/tier4_autoware_msgs) | [`0d9ad1f5bc784d5e210801b2e5e8111e284252f2`](https://github.com/tier4/tier4_autoware_msgs/commit/0d9ad1f5bc784d5e210801b2e5e8111e284252f2) | [Apache-2.0](https://github.com/tier4/tier4_autoware_msgs/blob/0d9ad1f5bc784d5e210801b2e5e8111e284252f2/LICENSE) |

The five channel definitions require only `tier4/autoware_auto_msgs`; the other eight repositories
belong to the organizer note's full replay workspace and would be excess attendee scope.

## Options measured

### Dynamic IDL decoding

MCAP's [ROS 2 profile](https://github.com/foxglove/mcap/blob/b13eb43cec62fd812689759a54eadcb6a0c64bfd/docs/specification/profiles/ros2.md)
permits `ros2idl` schemas, but the accepted
[`mcap-ros2-support` 0.5.7 decoder](https://github.com/foxglove/mcap/blob/releases/python/mcap-ros2-support/v0.5.7/python/mcap-ros2-support/mcap_ros2/decoder.py)
only constructs a decoder for `ros2msg`.
[`rosbags==0.11.5`](https://pypi.org/project/rosbags/0.11.5/) successfully parsed the
embedded IDL and decoded all 26,185 selected messages without ROS or generated packages. That proves feasibility,
but not suitability for the baseline: a clean research target containing `rosbags==0.11.5` and
`mcap==1.4.0` installed eight packages, 1,202 files and 52,590,012 bytes. It adds NumPy, APSW,
compression libraries, a second ROS type system, and a new compatibility surface to `civ`.

### Generated ROS messages

ROS Lyrical's
[distribution metadata](https://github.com/ros/rosdistro/blob/9fd379e939eafc9d58b5691c9ffd2f733d09d8ef/lyrical/distribution.yaml)
declares `autoware_auto_msgs` 1.0.0-8, but the
[official build-farm status](https://repo.ros2.org/status_page/ros_lyrical_default.html?q=autoware_auto_msgs)
shows no successful source or binary artifacts and `apt` could not locate
`ros-lyrical-autoware-auto-vehicle-msgs`. Building the exact Tier IV pin in the accepted Lyrical
container required `autoware_auto_geometry_msgs`, `autoware_auto_mapping_msgs`, and
`autoware_auto_planning_msgs` before `autoware_auto_vehicle_msgs`. The dependency-complete build
took 39.70 seconds, peaked at 189,448 KB RSS, produced 65,400,640 build bytes and 22,256,959 install
bytes across 1,505 installed files. This route is offline only after source and build dependencies
have been prepared, and it makes ROS workspace sourcing part of attendee setup.

### Explicit warnings

The selected approach adds zero packages, zero generated files, and no new runtime seam. The
warning is deterministic and honest: topic/schema metadata is available, field discovery is not.
The accepted Pix Hooke `ros2msg` fields continue to provide steering and speed for the scored path.

## Minimal external proof

A 13,068-byte MCAP excerpt containing one message from each of the five channels remains outside
Git at `<temporary-directory>/civ-issue13/kashiwa-five-topic-minimal.mcap`; its SHA-256 is
`191fda7c5ab351b1c1a51e69e75efbfafd5f5772d0d404f1a7385bd2037355b8`. The source trace and excerpt
were read-only, and no dataset or generated message artifact was committed.

`civ inspect` ran through `uv --offline` and returned all five topics with empty field lists plus
the five exact `field discovery unsupported for ros2idl` warnings. This proves the selected contract
on the smallest representative trace and proves that its runtime path needs no network.

## Acceptance against issue #13

| Criterion | Result |
|---|---|
| Inventory topics, schema hashes, and concrete value | PASS — inventory and measured values above |
| Review organizer pins and licences | PASS — all nine commits resolve; pinned licence files are Apache-2.0 |
| Select the smallest honest contract | PASS — retain explicit warnings |
| Prove it on a minimal external trace | PASS — five-message offline proof above |
| Record size, offline feasibility, and attendee complexity | PASS — option measurements above |
| Route accepted interface changes | PASS — none accepted; no downstream spec change |
