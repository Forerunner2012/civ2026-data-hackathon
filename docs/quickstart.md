# Quickstart: unpacked kit to first evidence clip

Five offline commands, run from the unpacked kit. Swap `data/route.mcap` for your dataset and
`examples/kashiwa/right_turn.yaml` for your path's reference detector (on the French data, use
`examples/french/left_turn.yaml` with `layouts/french-left-turn.xml`). Outputs are from a short demo
bag; your counts and hashes will differ.

## 1. Check the environment

```text
civ doctor --workspace work --bag data/route.mcap --layout layouts/kashiwa-right-turn.xml
```

```text
Doctor: READY
[PASS] python: CPython 3.12.7 (required >=3.10,<3.13)
...
```

A failure exits 2 and prints an `Action:` line under the failing check. Do that one thing and rerun.
Nothing is downloaded, installed, or written.

## 2. See what is in the bag

```text
civ inspect data/route.mcap
```

```text
Bag: route.mcap
Duration: 36.000s (0..36000000000 ns)
Topics:
  /pix_hooke/v2a_steerstafb  37 messages  1.02778 Hz  ...  fields: vcu_chassis_steer_angle_fb
  ...
```

A missing topic means it is not in the bag — check the dataset you unpacked, not the detector. A
`Warning:` about an embedded schema means this is not the pinned kit bag.

## 3. Look at one signal

```text
civ sample data/route.mcap --topic /pix_hooke/v2a_steerstafb --field vcu_chassis_steer_angle_fb --limit 4
```

```text
Bag: route.mcap
Signal: /pix_hooke/v2a_steerstafb.vcu_chassis_steer_angle_fb
Window: all timestamps, first 4 samples
Samples:
  0 ns  0
  1000000000 ns  15
```

Copy the topic and field exactly from step 2; nested fields use dotted paths. `--limit` defaults to
20; `--start-ns` / `--end-ns` bound the window. Open `layouts/kashiwa-right-turn.xml` in PlotJuggler
to see the same signal against its evidence context.

## 4. Detect intervals

```text
civ detect examples/kashiwa/right_turn.yaml data/route.mcap --output work
```

```text
{"dry_run":false,"event_count":2}
```

Add `--dry-run` to re-run without writing anything while you adjust `condition` or `timing` in your
own copy of the EventSpec. Your inputs are never rewritten.

## 5. Extract evidence

```text
civ clip work/events.jsonl data/route.mcap
```

```text
{"clip_count":2}
```

A failure names the missing topic or the empty window: every `evidence.topics` entry must exist in
the same bag you detected against.

## Working directory vs submitted bundle

`work/` keeps the heavy evidence on your machine:

```text
work/detector/right_turn.yaml   your EventSpec, copied byte-for-byte and hashed
work/events.jsonl               one normalized interval per line
work/evidence/<event_id>.mcap   the extracted clips — reopen these in PlotJuggler
work/run-manifest.json          hashes, counts, evidence window, clip facts
```

`civ report` writes `work/submission.zip` with exactly seven **metadata** entries: the EventSpec,
`events.jsonl`, one figure, `metrics.json`, `report.md`, your `reproduce.ps1` or `reproduce.sh`, and
`run-manifest.json`. No bag and no clip is ever bundled — the manifest carries the clip hashes, so
the run stays checkable without shipping the bytes.

## Next

With a label pack for your dataset, `civ score work --labels <labels.json>` writes `metrics.json`;
`civ report work` then validates the whole working set and assembles the bundle.
