# Golden-path schema source research

Status: **bounded provenance research for issue #19**

Recorded: 2026-08-26

## Conclusion

The Kashiwa detector's `pix_hooke_driver_msgs/msg/V2aSteerStaFb` is a custom Pixmoving
interface with a supportable upstream repository, immutable organizer pin, and Apache-2.0
licence. The French detector's `sensor_msgs/msg/Imu` and
`geometry_msgs/msg/TwistWithCovarianceStamped` are standard ROS 2 interfaces from
`ros2/common_interfaces`; they are not ZED-owned custom messages and need no separate ZED
schema pin.

## Verified recording registry

The exact recording identities come from the authorized sources already sealed in the
[Kashiwa](../phase1/kashiwa-acceptance.md) and
[French](../phase1/french-acceptance.md) acceptance records. On 2026-08-26, an index-only MCAP
summary read mapped each selected channel to its embedded schema and hashed the schema bytes
without iterating message payloads. `civ inspect` uses the same byte hash and field discovery.

| Dataset and topic | Embedded schema identity and SHA-256 | Discoverable fields | Source and licence | Verification |
|---|---|---|---|---|
| Kashiwa `/pix_hooke/v2a_steerstafb` | `pix_hooke_driver_msgs/msg/V2aSteerStaFb`, `ros2msg`, `4c3724cf5ee83ef9cbd127585519e80c7828341fcd626d4d588d22d406918eea` | `header.frame_id`, `header.stamp.{nanosec,sec}`, `vcu_chassis_steer_en_sta`, `vcu_chassis_steer_slopover`, `vcu_chassis_steer_work_mode`, `vcu_chassis_steer_mode_fb`, `vcu_chassis_steer_angle_fb`, `vcu_chassis_steer_angle_rear_fb`, `vcu_chassis_steer_angle_speed_fb`; the detector selects `vcu_chassis_steer_angle_fb` | `pixmoving-moveit/pix_driver@9feb55bd14f7bdf9c2e84acd05e0aced79e11df1`, Apache-2.0 | Exact embedded bytes are enforced by topic/name/encoding/hash; root declaration and units agree with the pinned source |
| French `/zed/zed_node/imu/data` | `sensor_msgs/msg/Imu`, `ros2msg`, `244d9e9566de33e36bf560d79a41a17d1a1b44c49bdaf2bd809aa7efb1389334` | `header.frame_id`, `header.stamp.{nanosec,sec}`, `orientation_covariance`, `angular_velocity.{x,y,z}`, `angular_velocity_covariance`, `linear_acceleration.{x,y,z}`, `linear_acceleration_covariance`; the detector selects `angular_velocity.z` | `ros2/common_interfaces@0ecd0f70791fe200f057b12bfc626beb21bad639`, Apache-2.0 | Exact concatenated embedded bytes are enforced; a checked-in base64 fixture proves the accepted public-inspection path |
| French `/fix_velocity` | `geometry_msgs/msg/TwistWithCovarianceStamped`, `ros2msg`, `d2905f17c4de4e92d693447c2d64ce2b70f916cee14318bce69c1969f71121fd` | `header.frame_id`, `header.stamp.{nanosec,sec}`, `twist.covariance`, `twist.twist.angular.{x,y,z}`, `twist.twist.linear.{x,y,z}`; the detector selects all three linear components | `ros2/common_interfaces@0ecd0f70791fe200f057b12bfc626beb21bad639`, Apache-2.0 | Exact embedded bytes are enforced; root and transitive standard definitions agree with the canonical source |

These are the only schemas needed to discover and decode the reference detector signals.
Evidence-only topics remain copied as opaque MCAP records by `civ clip`; they do not add decoder or
source dependencies to the participant baseline. The original bags, generated Python/ROS types,
source checkouts, and build/install trees remain external.

For both recordings, the embedded MCAP `ros2msg` schema bytes are the recording-specific
truth. An upstream source pin documents origin and permits reproducible vendoring, but the type
name and field layout alone do not prove which package revision was installed on the recording
machine.

## Kashiwa: Pix Hooke steering feedback

The owning source repository is
[`pixmoving-moveit/pix_driver`](https://github.com/pixmoving-moveit/pix_driver). Its
[`V2aSteerStaFb.msg`](https://github.com/pixmoving-moveit/pix_driver/blob/54c987b238bb1bdc53ff45d832eeef5267ff9095/pix_hooke_driver_msgs/msg/V2aSteerStaFb.msg)
declares `int32 vcu_chassis_steer_angle_fb`; the adjacent source comment specifies degrees and
the range `[-500, 500]`.

The message path has one upstream history entry: commit
[`54c987b238bb1bdc53ff45d832eeef5267ff9095`](https://github.com/pixmoving-moveit/pix_driver/commit/54c987b238bb1bdc53ff45d832eeef5267ff9095),
dated 2023-03-07. The schema is therefore unchanged between that introduction commit and the
organizer's already-reviewed repository pin
[`9feb55bd14f7bdf9c2e84acd05e0aced79e11df1`](https://github.com/pixmoving-moveit/pix_driver/commit/9feb55bd14f7bdf9c2e84acd05e0aced79e11df1).
The latter should be the kit's repository pin for consistency with the existing organizer
provenance; the former should be retained as `last_schema_change` evidence. The schema at the
organizer pin is available at this
[`V2aSteerStaFb.msg` permalink](https://github.com/pixmoving-moveit/pix_driver/blob/9feb55bd14f7bdf9c2e84acd05e0aced79e11df1/pix_hooke_driver_msgs/msg/V2aSteerStaFb.msg).

The package manifest declares
[`Apache License 2.0`](https://github.com/pixmoving-moveit/pix_driver/blob/54c987b238bb1bdc53ff45d832eeef5267ff9095/pix_hooke_driver_msgs/package.xml)
at the schema-introduction commit. The later organizer pin also contains the repository's
complete [`Apache-2.0 licence text`](https://github.com/pixmoving-moveit/pix_driver/blob/9feb55bd14f7bdf9c2e84acd05e0aced79e11df1/LICENSE).

This provenance establishes an exact, licensed upstream source for the accepted field. It does
not establish that commit `9feb55b...` was checked out on the Kashiwa recorder; the embedded
schema bytes and their recorded SHA-256 remain authoritative for that claim.

## French transfer: standard ROS interfaces

Both detector inputs are owned by the canonical ROS 2
[`ros2/common_interfaces`](https://github.com/ros2/common_interfaces) repository:

- [`sensor_msgs/msg/Imu`](https://github.com/ros2/common_interfaces/blob/0ecd0f70791fe200f057b12bfc626beb21bad639/sensor_msgs/msg/Imu.msg)
  supplies the selected `angular_velocity.z` field through its standard `Vector3` member.
- [`geometry_msgs/msg/TwistWithCovarianceStamped`](https://github.com/ros2/common_interfaces/blob/0ecd0f70791fe200f057b12bfc626beb21bad639/geometry_msgs/msg/TwistWithCovarianceStamped.msg)
  supplies the `twist.twist.linear.{x,y,z}` velocity components through standard nested
  `TwistWithCovariance`, `Twist`, and `Vector3` definitions.

Commit
[`0ecd0f70791fe200f057b12bfc626beb21bad639`](https://github.com/ros2/common_interfaces/commit/0ecd0f70791fe200f057b12bfc626beb21bad639)
is tag `4.9.0`, a reproducible Humble-era source revision from before the 2025-07-31 French
recording. The official ROS release repository also has package-specific Humble release tags for
[`sensor_msgs 4.9.0-1`](https://github.com/ros2-gbp/common_interfaces-release/tree/release/humble/sensor_msgs/4.9.0-1)
and
[`geometry_msgs 4.9.0-1`](https://github.com/ros2-gbp/common_interfaces-release/tree/release/humble/geometry_msgs/4.9.0-1).
These are useful reproducible pins, not evidence that the recorder had version 4.9.0 installed.

The root message files have been unchanged since the common-interface rename commit
[`a24bc1fbaed2fca1ffa916ddb61a2a730f529d95`](https://github.com/ros2/common_interfaces/commit/a24bc1fbaed2fca1ffa916ddb61a2a730f529d95)
in 2015. Their stable wire layout explains why a later canonical Humble pin can document the
recorded standard types without implying a producer version.

Both package manifests declare Apache License 2.0:
[`sensor_msgs/package.xml`](https://github.com/ros2/common_interfaces/blob/0ecd0f70791fe200f057b12bfc626beb21bad639/sensor_msgs/package.xml)
and
[`geometry_msgs/package.xml`](https://github.com/ros2/common_interfaces/blob/0ecd0f70791fe200f057b12bfc626beb21bad639/geometry_msgs/package.xml).
ROS Lyrical continues to source both packages from this same repository; the official
[`lyrical/distribution.yaml`](https://github.com/ros/rosdistro/blob/9fd379e939eafc9d58b5691c9ffd2f733d09d8ef/lyrical/distribution.yaml)
lists `common_interfaces`, including `geometry_msgs` and `sensor_msgs`, from the `lyrical`
branch. A kit registry may therefore describe these as standard ROS sources rather than custom
ZED assets.

There is no evidence in the repository that either French type has a custom schema fork or that
the recording used a particular ZED wrapper commit. In particular, `/fix_velocity` is the GNSS
velocity input in the acceptance record, not a ZED-owned type. A ZED wrapper pin would add
unsupported provenance and should not be placed in the schema registry unless external recording
metadata supplies it.

If the kit vendors complete `ros2msg` schema payloads rather than only root `.msg` files, it must
also retain the exact transitive definitions (`Header`, `Quaternion`, `Vector3`,
`TwistWithCovariance`, `Twist`, and their dependencies). A root-file source permalink is not
byte-equivalent to the concatenated schema payload embedded in MCAP.

## Registry recommendation and limits

| Dataset | Type | Repository pin | Licence | Confidence boundary |
|---|---|---|---|---|
| Kashiwa | `pix_hooke_driver_msgs/msg/V2aSteerStaFb` | `pixmoving-moveit/pix_driver@9feb55bd14f7bdf9c2e84acd05e0aced79e11df1`; last schema change `54c987b238bb1bdc53ff45d832eeef5267ff9095` | Apache-2.0 | Exact upstream schema and organizer pin; producer checkout unproven |
| French | `sensor_msgs/msg/Imu` | `ros2/common_interfaces@0ecd0f70791fe200f057b12bfc626beb21bad639` (`4.9.0`) | Apache-2.0 | Canonical pre-recording Humble source; producer package version unproven |
| French | `geometry_msgs/msg/TwistWithCovarianceStamped` | `ros2/common_interfaces@0ecd0f70791fe200f057b12bfc626beb21bad639` (`4.9.0`) | Apache-2.0 | Canonical pre-recording Humble source; producer package version unproven |

The registry should separately record the embedded schema SHA-256 observed in each authorized
MCAP. That hash answers whether kit bytes match the recording; the repository pin answers where
the licensed source came from.

## Explicit exclusion

The five Tier IV/Autoware Kashiwa topics encoded as `ros2idl` remain outside the attendee schema
registry and decoder contract. They are not required by the accepted Pix Hooke `ros2msg` detector,
and this research does not justify dynamic IDL generation, a generated ROS workspace, or another
runtime type system. The existing deterministic field-discovery warning remains the supported
behavior.
