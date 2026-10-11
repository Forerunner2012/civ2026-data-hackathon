# Third-party notices

These notices cover the identified copied material below. They do not license datasets,
historical slide imagery, trademarks, or other material whose origin remains unresolved.
The maintainer's intended MIT grant for original contributions is separate.

## Sites build plugin

`handoff-site/build/sites-vite-plugin.ts` is an adaptation of
[`openai/sites` at `ec4dbd0b7818b59cb45fa7a39751709ae9036096`](https://github.com/openai/sites/blob/ec4dbd0b7818b59cb45fa7a39751709ae9036096/packages/sites-vite-plugin/src/index.ts).
The upstream source blob is `cffadd1a7bed9acc604cfd1d40bb6dabd0f6dfa6`.

The local copy changes formatting, adds an explanatory comment, and makes the hosting-config
copy conditional. Its upstream MIT copyright and permission notice is retained verbatim in
[OpenAI Sites 2023 MIT license](LICENSES/OpenAI-Sites-2023-MIT.txt).
The plugin remains at its existing path and retains its behavior.

## ROS message-schema fixture

`tests/fixtures/schemas/reims-imu.ros2msg.b64` was historically named
`tests/fixtures/schemas/french-imu.ros2msg.b64`. Its decoded SHA-256 is
`244d9e9566de33e36bf560d79a41a17d1a1b44c49bdaf2bd809aa7efb1389334`.
It contains schema definitions, rather than recorded sensor messages.

Four complete message definitions match the pinned
[`ros2/common_interfaces` sources](https://github.com/ros2/common_interfaces/tree/0ecd0f70791fe200f057b12bfc626beb21bad639):
`sensor_msgs/Imu`, `geometry_msgs/Quaternion`, `geometry_msgs/Vector3`, and `std_msgs/Header`.
Their packages declare Apache-2.0. The pinned upstream license copy is retained verbatim in
[ROS Apache-2.0 license](LICENSES/ROS-Apache-2.0.txt).

The transitive `builtin_interfaces/Time` definition has matching fields but different comments
from both inspected
[`ros2/rcl_interfaces` revisions](https://github.com/ros2/rcl_interfaces/blob/82776fc9068d1e0cd4af11c2e2700195994b2eb1/builtin_interfaces/msg/Time.msg).
The recorded fixture says `[0, 10e9)` where that upstream text says `[0, 1e9)`.
The exact producer revision and assembly transformation remain unresolved. This record does
not claim exact upstream text identity for `Time`, completed attribution obligations, or a
changed schema contract. Fixture bytes remain unchanged.

## Distribution boundary

These root files are source notices. Their presence does not prove that a built wheel,
standalone source archive, website, or offline kit contains the required notices.
Each distribution needs an inventory of its actual bytes and applicable obligations.
Datasets and external viewer downloads retain their own terms. Historical event risk
acceptance is not public-release clearance.
