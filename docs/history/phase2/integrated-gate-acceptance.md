# Integrated Phase 2 gate acceptance record

> **Historical CIV 2026 record.** The dates, commands, artifact identities and acceptance
> below describe the original event and its recorded scope. Start a current session with the
> [QuickStart](../../quickstart.md), [organizer guide](../../organizers/README.md) and
> [participant contracts](../../reference/participant-contracts.md). See the
> [Phase 1–5 history index](../civ-2026.md) for later changes. This record does not grant
> new data rights, platform qualification or public-release approval.

Recorded: 2026-08-27

Repository checkpoint: `3b912f0` (this record and the `work/` ignore rule land on top).

This record covers issue #22 as **rescoped by decision** during the run. Two overrides were taken
and are recorded in full below rather than left as silent gaps:

1. The Windows development path is accepted in place of the pinned ROS 2 Lyrical / Ubuntu 26.04
   target.
2. Phase 2 accepts that no label pack exists, so `score`, `report`, intake, and batch acceptance
   move to Phase 3.

## Preconditions

| Item | State |
| --- | --- |
| Stable contracts and compatibility behaviour | merged, issue #20 |
| `doctor` and `sample` | merged, issue #18 |
| Schema pins | merged, issue #19 |
| Reference detectors, layouts, quickstart | merged, issue #21 |
| Kashiwa inputs | `2025-07-27 Final Data sample Tsukada Labs/hackathon_data`, 12 sessions, one bag each, 4-8 GB per session |
| Reims inputs | `2025-07-30 Recording sessions/rosbag2_2025_07_31-13_24_53`, one session split across nine bags |
| Label packs | **none exist** — see decision 2 |

## Step 1 — Environment

Windows 11 AMD64, CPython 3.12.13. `civ doctor` reports `FAILED` on this host:

```text
Doctor: FAILED
[PASS] python: CPython 3.12.13 (required >=3.10,<3.13)
[PASS] dependencies: cel-python 0.5.0; civ-workshop 0.1.0; mcap 1.4.0; mcap-ros2-support 0.5.7; PyYAML 6.0.3
[FAIL] ros: ROS_DISTRO=unset (required lyrical)
[PASS] workspace / bag / layout / offline-kit
[FAIL] plotjuggler: not found on PATH
[PASS] platform: Windows 11 AMD64; release target is Ubuntu 26.04 linux-amd64
[WARN] lichtblick: not found; optional viewer
```

Both failures are false negatives: PlotJuggler and Lichtblick are installed but not on `PATH`, and
nothing in `inspect`, `sample`, `detect`, or `clip` uses ROS — the MCAP path is pure Python. The
entire golden path ran on this host regardless. Routed to Phase 3 as finding 3.

## Step 2 — Both datasets, twice

| | Kashiwa | Reims |
| --- | --- | --- |
| Bag | `final_route_2_0.mcap_0.mcap` | `rosbag2_2025_07_31-13_24_53_0.mcap` |
| `sha256` | `b9066692c358bb7aac7bfaa4038dc2f54dc63a02eeb245a014af732a5cc59712` | `0a0817b3afc85796182c77c8dd8d9e5b84b0ee12f28b3b3fa881d3166e3035ca` |
| EventSpec | `kashiwa-right-turn-steering-baseline` | `reims-left-turn-transfer-baseline` |
| `detect` run 1 / run 2 | 12.9 s / 13.8 s | 37.0 s / 36.4 s |
| Events | 5 | 1 |
| `clip` run 1 / run 2 | 11.7 s / 12.1 s | 3.4 s / 3.2 s |
| Clip bytes | 80,085,980 | 25,587,790 |

Both datasets produced **byte-identical `events.jsonl`, `run-manifest.json`, and clip `sha256`
across the two runs**. Every artifact carries the stable identifiers: `civ.eventspec/v1`,
`civ.event/v1`, `civ.run-manifest/v1`.

The Kashiwa reruns also reproduced the participant's independent timed run from Step 4: the five
`event_id` values are identical, and since `event_id` is `sha256(bag:spec:start:end)` that fixes the
intervals and provenance byte-for-byte across separate invocations on separate occasions.

The single Reims interval is `1753961237531377273 -> 1753961241534534018` (4.003 s), triggered at
`yaw_rate=0.0831` against the spec's `>= 0.08` and a squared velocity magnitude of ~21.3 against its
`>= 16.0`. Both halves of the condition fired; it is not a degenerate match. Whether one event is
the correct count for this chunk cannot be judged without labels.

## Step 3 — Clips and schema provenance

Every clip from both datasets reopens as valid MCAP, its `sha256` matches the run manifest, and it
contains **exactly** the declared `evidence.topics` — six for Kashiwa, five for Reims — with no
extra topic and none missing.

`civ inspect` reported zero warnings on every bag and every clip, which confirms all three schema
pins from #19 against real recordings for the first time; previously they had only been checked
against fixtures:

| Topic | Pinned `sha256` |
| --- | --- |
| `/pix_hooke/v2a_steerstafb` | `4c3724cf…` |
| `/fix_velocity` | `d2905f17…` |
| `/zed/zed_node/imu/data` | `244d9e95…` |

## Step 4 — Timed fresh-user rehearsal

An experienced user followed only `docs/quickstart.md` on the Windows host and reached a reopenable
first evidence clip on the Kashiwa data in **under 15 minutes**, against a 20-minute budget. The
clip and the full recording were opened in Lichtblick. Both `layouts/kashiwa-right-turn.pj4.xml` and
`layouts/reims-left-turn.pj4.xml` opened in PlotJuggler with their curves resolving, which also
clears the visual check left open on issue #21.

Windows is the harder of the two paths — no ROS, viewers off `PATH`, `doctor` reporting `FAILED`
throughout — so this result is treated as stronger than the same run on the release target, not
weaker.

## Step 5 — Verification

`uv run pytest` 180 passed; `uv run ruff check .` clean; `uv run mypy src tests` clean across 31
files; `git diff --check` clean; `handoff-site` `npm test` and `npm run lint` clean.

Schema conformance and the version-rejection diagnostics required by criterion 6 are covered by
`tests/test_stable_contracts.py`, which pins every compatibility-matrix row through the public CLI
and pins the closed field sets to the published schemas.

## Failure and intervention log

1. **`civ doctor` fails on a working machine.** Two required checks fail as false negatives; the
   whole path then runs. Not fixed here — the required-everywhere vs. platform-conditional question
   is a policy call.
2. **A bag can pass `doctor` and still be unusable.** The `2025-07-30` Reims bag carries only
   `/fix`, `/fix_velocity`, `/tf_static`; the Reims EventSpec binds `/zed/zed_node/imu/data`.
   `doctor` accepts it because the bag check only tests file existence.
3. **Chunked sessions are unaddressed.** The Reims recording is `metadata.yaml` plus nine bags;
   `civ detect` takes one bag file and the quickstart says only "swap `data/route.mcap` for your
   dataset". A participant handed a session directory has to guess which chunk to use.
4. **No label pack exists**, so `score` and `report` could not run, and with no bundle there was
   nothing for intake or `score-batch` to consume.

No failure was fixed and re-run to make this record clean.

## Pass / fail against issue #22, as rescoped

| Criterion | Result |
| --- | --- |
| 1 — under-20-minute fresh-user run | **Pass** on the Windows path, under 15 minutes, per decision 1 |
| 2 — timed path covers `doctor`…`clip`, stumbles on the clock | **Pass** |
| 3, 4 — both datasets twice, byte-identical | **Pass through `clip`**; `score`/`report` routed to Phase 3 |
| 5 — clips reopen with exactly the declared topics | **Pass**; metadata-only bundle half routed to Phase 3 |
| 6 — schemas and version diagnostics | **Pass** |
| 7 — cost and zero-network evidence | **Partial** — wall-clock and clip bytes captured; memory, I/O, and zero-network capture routed to Phase 3 |
| 8 — intake and batch accept the bundles | **Routed to Phase 3** — no bundle without labels |
| 9 — full verification | **Pass** |
| 10 — one acceptance record | **Pass** — this document |

## Routing

**To Phase 3**

1. Label packs for both datasets, then `score` → `report` → intake → `score-batch` against real
   bundles. This is the half of the gate Phase 2 could not reach, because producing labels is
   itself Phase 3 work.
2. The pinned Lyrical / Ubuntu 26.04 rehearsal, capturing peak memory, bytes read and written,
   working disk, bundle size, host identity, and zero-network evidence.
3. Decide whether `doctor`'s `ros` and `plotjuggler` checks stay required off the release target,
   or become platform-conditional with Lichtblick accepted as a viewer.

**To Phase 4**

4. Quickstart guidance for chunked rosbag2 sessions, and a `doctor` or `detect` diagnostic when a
   bag lacks the topics the chosen detector binds.

Nothing here expands Phase 2.
