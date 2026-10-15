# Participant-kit third-party notices

This index maps identified participant-kit inputs to full notice assets copied by the existing assembler; paths in code are assembly-relative references, not source-tree links.

## Sites build plugin

`handoff-site/build/sites-vite-plugin.ts` adapts the [OpenAI Sites plugin](https://github.com/openai/sites/blob/ec4dbd0b7818b59cb45fa7a39751709ae9036096/packages/sites-vite-plugin/src/index.ts); local changes make the hosting-config copy conditional and adjust formatting and comments. Copyright (c) 2023 OpenAI; full MIT text is included at `LICENSES/OpenAI-Sites-2023-MIT.txt`.

## ROS message schemas

The source fixtures include definitions from [ROS 2 common interfaces](https://github.com/ros2/common_interfaces/tree/0ecd0f70791fe200f057b12bfc626beb21bad639) and [ROS 2 interfaces](https://github.com/ros2/rcl_interfaces/blob/82776fc9068d1e0cd4af11c2e2700195994b2eb1/builtin_interfaces/msg/Time.msg), with modified comments; the full Apache License 2.0 text is included at `LICENSES/ROS-Apache-2.0.txt`.

## CIV and MCAP Python packages

The unchanged `civ-workshop 0.1.0` Linux and Windows wheels and assembled `runtime/source/` subset map to the captured CIV MIT text at `LICENSES/CIV-MIT.txt`.

Direct dependencies `mcap 1.5.0` and `mcap-ros2-support 0.5.7` map to the full MIT text at `LICENSES/MCAP-MIT.txt`; the matching license bytes fetched from both official version-pinned sources were 1,077 bytes with SHA-256 `da11235665c17d4c1634072dae92b8ba1b38d6fdde2ccf19a6bbede33253f58d`.

The official `mcap` tag `releases/python/mcap/v1.5.0` resolves to commit `3b19a3805548be7a90450ed7fb8da6748a4c08b0` and its [LICENSE file](https://raw.githubusercontent.com/foxglove/mcap/releases/python/mcap/v1.5.0/LICENSE).

The official `mcap-ros2-support` tag `releases/python/mcap-ros2-support/v0.5.7` resolves to commit `b13eb43cec62fd812689759a54eadcb6a0c64bfd` and its [LICENSE file](https://raw.githubusercontent.com/foxglove/mcap/releases/python/mcap-ros2-support/v0.5.7/LICENSE).

## Self-hosted Geist fonts

The 11 self-hosted Geist and Geist Mono WOFF2 files under `site/assets/_vinext_fonts/` map to the captured OFL-1.1 text at `site/LICENSES/Geist-OFL-1.1.txt`, sourced from [Geist](https://raw.githubusercontent.com/google/fonts/main/ofl/geist/OFL.txt) and [Geist Mono](https://raw.githubusercontent.com/google/fonts/main/ofl/geistmono/OFL.txt); one trailing space was removed from the copied text for whitespace cleanliness, and the cached font CSS does not identify an exact upstream font release.

## Viewer packages

The five unchanged viewer packages retain their original bytes and embedded notices; package identities, hashes, selected embedded notice hashes, source references, and read limits are recorded in `viewer/NOTICES.md`, with full Lichtblick and PlotJuggler MPL-2.0 texts at `viewer/LICENSES/Lichtblick-MPL-2.0.txt` and `viewer/LICENSES/PlotJuggler-MPL-2.0.txt`.

## Legacy container archive

The unchanged legacy Linux container archive and selected in-image notice locations are recorded in `container/NOTICES.md`.

This is a bounded notice supplement for identified kit inputs; it is not a full software bill of materials or a statement of legal clearance.
