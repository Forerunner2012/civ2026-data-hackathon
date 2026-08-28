# Phase 3 doctor readiness policy

Status: **accepted for the Phase 3 gate**

Recorded: 2026-08-28

`civ doctor` is one read-only preflight with two explicit readiness profiles. Both profiles report
the same capabilities in the same order, but they enforce different requirements. The selected
profile is present in terminal and JSON output so a pure-MCAP result cannot be mistaken for release
qualification.

## Pure-MCAP participant profile

`pure-mcap` is the default because `inspect`, `sample`, `detect`, `clip`, `score`, and `report` use
the Python MCAP path and do not require a sourced ROS environment or a viewer executable:

```text
civ doctor --workspace work --bag data/route.mcap --offline-kit .
```

The required capabilities are supported CPython, pinned project dependencies, a writable
workspace, a readable bag with valid opening and closing MCAP magic, and a complete offline kit. A
missing or unusable required capability fails with exit status 2 and one corrective action.

ROS, host platform, and visualization are still reported. Missing ROS or visualization produces a
warning rather than a false readiness failure. When available, visualization passes through either
Lichtblick or PlotJuggler with an existing `--layout`; neither adapter is silently required for the
pure-MCAP workflow.

## Pinned release-target profile

Release qualification must opt into the stricter profile:

```text
civ doctor --profile release-target \
  --workspace work --bag data/route.mcap --offline-kit .
```

It enforces every pure-MCAP capability plus all of the following:

- Ubuntu 26.04 on AMD64 (`x86_64`), identified from the host and freedesktop OS release metadata;
- `ROS_DISTRO=lyrical`; and
- one usable visualization route: Lichtblick, or PlotJuggler together with an existing
  `--layout`.

Lichtblick is a complete alternative visualization adapter for this preflight. The release-target
profile does not require a PlotJuggler layout when Lichtblick is available. If neither route is
usable, the visualization capability fails and gives a corrective action.

## Report contract

Text output begins with `Doctor: READY|FAILED` and `Profile: <name>`. JSON output is compact and
key-sorted, with top-level `profile`, `ok`, and ordered `checks`. Each check records `name`,
`status`, `required`, `detail`, and `action`. `ok` is true only when every check required by the
selected profile passes.

The check order is Python, dependencies, ROS, workspace, bag, offline kit, platform, and
visualization. The command remains offline and does not install software, control a viewer, or
write participant or organizer artifacts.

## Deferred diagnostics

The structural bag check does not validate whether the bag contains the topics required by a
particular EventSpec. This policy also does not diagnose chunked rosbag2 sessions or pin/audit final
viewer assets. Those remain outside this ticket's readiness-policy scope.
