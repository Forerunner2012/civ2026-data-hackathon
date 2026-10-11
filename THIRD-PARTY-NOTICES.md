# Third-party notices

## Sites build plugin

`handoff-site/build/sites-vite-plugin.ts` adapts the
[OpenAI Sites plugin](https://github.com/openai/sites/blob/ec4dbd0b7818b59cb45fa7a39751709ae9036096/packages/sites-vite-plugin/src/index.ts).
Local changes make the hosting-config copy conditional and adjust formatting and comments.

Copyright (c) 2023 OpenAI. Licensed under the
[MIT license](LICENSES/OpenAI-Sites-2023-MIT.txt).

## ROS message schemas

`tests/fixtures/schemas/reims-imu.ros2msg.b64` contains definitions of
`sensor_msgs/Imu`, `geometry_msgs/Quaternion`, `geometry_msgs/Vector3`, and `std_msgs/Header`
from [ROS 2 common interfaces](https://github.com/ros2/common_interfaces/tree/0ecd0f70791fe200f057b12bfc626beb21bad639).
It also includes `builtin_interfaces/Time` from
[ROS 2 interfaces](https://github.com/ros2/rcl_interfaces/blob/82776fc9068d1e0cd4af11c2e2700195994b2eb1/builtin_interfaces/msg/Time.msg),
with modified comments.

Licensed under [Apache License 2.0](LICENSES/ROS-Apache-2.0.txt).

## External materials

Datasets and external viewer downloads have their own terms.
Include the applicable notices when redistributing these components.
