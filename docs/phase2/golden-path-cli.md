# Phase 2 golden-path CLI

Status: **candidate behavior complete for issue #18**

Recorded: 2026-08-26

## Environment diagnosis

`civ doctor` is a read-only, offline preflight. It performs no downloads, installation, network
access, viewer control, or filesystem writes. A participant identifies the local assets that the
golden path will use:

```text
civ doctor --workspace work --bag data/route.mcap --layout layouts/signals.xml
```

`--offline-kit` defaults to the current directory and must contain `pyproject.toml`, `uv.lock`,
`examples/`, and `schemas/`. `--workspace` also defaults to the current directory. The bag and
PlotJuggler layout are explicit because Phase 2 does not invent a data-package directory contract
before the reference kit is frozen.

Required checks are reported in a fixed order: supported CPython, pinned project dependencies, ROS
2 Lyrical, writable workspace, bag, layout, offline-kit contents, and PlotJuggler on `PATH`. Any
failed required check exits with status 2 and prints a corrective action. Host platform and the
optional Lichtblick viewer are reported afterward but do not block readiness. `--json` emits the
same ordered checks as compact, key-sorted JSON for rehearsal automation.

The platform check is intentionally informational. Ubuntu 26.04 linux-amd64 remains the forward
release target, while the Phase 1 evidence also established a Windows development path and a Humble
compatibility floor. ROS Lyrical itself remains required for the pinned participant-kit readiness
result.

## Deterministic signal sampling

`civ sample` reads one field from one discoverable topic without requiring participants to write ROS
code:

```text
civ sample data/route.mcap --topic /fix_velocity --field twist.twist.linear.x \
  --start-ns 1000000000 --end-ns 5000000000 --limit 20 --json
```

`--start-ns` and `--end-ns` are optional inclusive MCAP log-time bounds. `--limit` defaults to 20
and is always enforced, so an unbounded timestamp request is still count-bounded. Results retain
MCAP iteration order and contain only the bag basename, requested topic and field, effective bounds,
and timestamp/value pairs. Compact key-sorted JSON is stable for the same input bytes and request;
the default rendering is a short terminal table.

Sampling uses the inspection module's schema discovery and shared JSON/CDR decoder. Nested
`jsonschema` and `ros2msg` fields use dotted paths. Missing topics, unknown fields, invalid or empty
windows, absent/invalid schemas, and unsupported message encodings fail with an actionable status-2
diagnostic. `ros2idl` retains the explicit field-discovery warning and does not introduce dynamic
IDL generation or decoding.

## Compatibility

The new commands only print terminal output and create no participant artifacts. Existing command
arguments, successful output bytes, EventSpec evaluation, and artifact serialization are unchanged.
The detector now consumes the same message decoder as sampling, concentrating JSON and ROS 2 CDR
behavior in one module without adding a new participant-facing interface.
