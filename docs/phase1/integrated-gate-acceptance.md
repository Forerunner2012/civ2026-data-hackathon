# Integrated Phase 1 gate acceptance record

> **Historical CIV 2026 record.** The dates, commands, artifact identities and acceptance
> below describe the original event and its recorded scope. Start a current session with the
> [QuickStart](../quickstart.md), [organizer guide](../organizers/README.md) and
> [participant contracts](../reference/participant-contracts.md). See the
> [Phase 1–5 history index](../history/civ-2026.md) for later changes. This record does not grant
> new data rights, platform qualification or public-release approval.

Status: **complete — all 13 issue #11 acceptance criteria pass**

Recorded: 2026-08-26 · Operator: Codex on the Forerunner2012 organizer workstation

The tables below were filled as each step completed rather than reconstructed afterwards. Every
workaround or retry appears in the intervention log. Do not commit bags, clips, label packs,
generated submissions, ledgers, caches or runtime state; only this record enters the repository.

## Preconditions

- The pinned forward environment from [`lyrical-acceptance.md`](lyrical-acceptance.md): official
  ROS 2 Lyrical / Ubuntu 26.04 linux-amd64 base digest
  `sha256:122a787d0eb7e1b2c18370e35ef394332db5c11d242bea6f05f2b2911e26b04d`, managed CPython
  3.12.11, dependency volume prepared and mounted read-only.
- Both authorized sources mounted read-only: the Kashiwa bag from
  [`kashiwa-acceptance.md`](kashiwa-acceptance.md) and the Reims chunk from
  [`reims-acceptance.md`](reims-acceptance.md).
- The two sealed organizer label packs in one read-only directory, one `.json` per dataset. Their
  `source_sha256` values must be distinct and must match the two bags, or `civ score-batch` refuses
  the run before scoring anything.
- The authored `report.md`, figure and reproduction entry for each dataset, ready to copy into the
  working directory before `civ report`.
- The configured Tally form URL for the intake step ([`intake-acceptance.md`](intake-acceptance.md)).

Every container command runs with `--network none`, no GPU, the repository, bags, label packs and
dependency volume read-only, and only the external output directory writable. Wrap each measured
command in GNU `/usr/bin/time -v` and keep its output; the socket counters are the offline evidence.

Shell variables used below:

```sh
GATE=/out/gate            # the single writable output directory
KASHIWA=/data/kashiwa.mcap
REIMS=/data/reims.mcap
LABELS=/labels            # read-only organizer packs
LEDGER=$GATE/intake
```

## Step 1 — Environment and input provenance

```sh
uname -srm
head -2 /etc/os-release
python -V
python -c "import civ_workshop; print(civ_workshop.__version__)"
python -c "from importlib.metadata import distributions; print('\n'.join(sorted(f'{d.metadata[\"Name\"]}=={d.version}' for d in distributions() if d.metadata[\"Name\"])))"
sha256sum "$KASHIWA" "$REIMS" "$LABELS"/*.json
```

| Item | Recorded value |
|---|---|
| Host and CPU | Windows 11 Pro 10.0.26200; Intel Core i7-13620H, 10 cores / 16 logical processors; Docker Desktop 4.86.0 / Engine 29.7.2 / WSL2 kernel 6.18.33.2 |
| Container base digest | `sha256:122a787d0eb7e1b2c18370e35ef394332db5c11d242bea6f05f2b2911e26b04d` |
| Prepared image ID | `sha256:abf90cdd46b446a185f24bc2a7097a49b34b57c415ff227e02ae55c17c7cd423` |
| OS / ROS distribution / architecture | Ubuntu 26.04 LTS / Lyrical / linux-amd64 CPU; 16 container-visible logical processors |
| CPython | 3.12.11 |
| `civ-workshop` | 0.1.0 |
| `mcap` / `mcap-ros2-support` / `PyYAML` / `cel-python` | 1.4.0 / 0.5.7 / 6.0.3 / 0.5.0 |
| Kashiwa bag bytes and SHA-256 | 7,875,976,476; `b9066692c358bb7aac7bfaa4038dc2f54dc63a02eeb245a014af732a5cc59712` |
| Reims chunk bytes and SHA-256 | 3,221,880,955; `0a0817b3afc85796182c77c8dd8d9e5b84b0ee12f28b3b3fa881d3166e3035ca` |
| Kashiwa label pack SHA-256 | `1ee742010744686c07b552aed2c6192622613f5ff9734ec3160d5286db94f201` |
| Reims label pack SHA-256 | `fd745fad80d4d9a143f262077d34bfec4489b169f045d3e56d382f3ff1bcc9b5` |

## Step 2 — Both datasets through the offline command path, twice

Run this for `kashiwa` and again for `reims`, with `pass` 1 and 2. Copy the authored `report.md`,
figure and reproduction entry into `$out` after `civ score` and before `civ report`.

```sh
out=$GATE/kashiwa-$pass
/usr/bin/time -v civ inspect "$KASHIWA" --json > "$out.inventory.json" 2> "$out.inspect.time"
/usr/bin/time -v civ detect examples/kashiwa/right_turn.yaml "$KASHIWA" --output "$out" 2> "$out.detect.time"
/usr/bin/time -v civ clip "$out/events.jsonl" "$KASHIWA" 2> "$out.clip.time"
/usr/bin/time -v civ score "$out" --labels "$LABELS/kashiwa.json" 2> "$out.score.time"
/usr/bin/time -v civ report "$out" 2> "$out.report.time"
```

Per command, per dataset, from the `time -v` output:

| Dataset | Command | Wall time | Peak RSS | FS input blocks | FS output blocks | Socket msgs sent/received |
|---|---|---:|---:|---:|---:|---:|
| Kashiwa | `civ inspect` | 1:13.66 | 116,168 KB | 15,478,068 | 0 | 0 / 0 |
| Kashiwa | `civ detect` | 1:39.32 | 114,216 KB | 27,608,459 | 0 | 0 / 0 |
| Kashiwa | `civ clip` | 1:29.49 | 87,708 KB | 24,191,533 | 0 | 0 / 0 |
| Kashiwa | `civ score` | 0:00.99 | 40,592 KB | 270 | 0 | 0 / 0 |
| Kashiwa | `civ report` | 0:01.80 | 41,252 KB | 156,736 | 0 | 0 / 0 |
| Reims | `civ inspect` | 0:26.77 | 47,372 KB | 6,290,048 | 0 | 0 / 0 |
| Reims | `civ detect` | 1:05.59 | 49,120 KB | 12,582,788 | 0 | 0 / 0 |
| Reims | `civ clip` | 0:24.49 | 66,844 KB | 6,577,773 | 0 | 0 / 0 |
| Reims | `civ score` | 0:00.80 | 40,868 KB | 261 | 0 | 0 / 0 |
| Reims | `civ report` | 0:00.90 | 41,284 KB | 50,266 | 0 | 0 / 0 |

Every socket cell must read zero. Expected results to confirm against the sealed records: Kashiwa
TP 2, FP 3, FN 1, F1 0.5, mean IoU 0.644663772045; Reims TP 1, FP 0, FN 0, F1 1.0, mean IoU
0.800631349.

```sh
sha256sum "$GATE"/kashiwa-[12]/events.jsonl "$GATE"/kashiwa-[12]/metrics.json "$GATE"/kashiwa-[12]/submission.zip
sha256sum "$GATE"/reims-[12]/events.jsonl "$GATE"/reims-[12]/metrics.json "$GATE"/reims-[12]/submission.zip
du -sb "$GATE"/kashiwa-1 "$GATE"/reims-1
find "$GATE"/kashiwa-1 -type f | wc -l
```

| Dataset | `events.jsonl` | `metrics.json` | `submission.zip` | Pass 1 vs pass 2 | Working-dir bytes / files | Bundle bytes |
|---|---|---|---|---|---|---|
| Kashiwa | `798d05a6ebc46536d0aa32b0f03911f47e2b72ffd41bb11224a61c895e3490a9` | `846411d0b811930083076f1167b0e573f40074dad84aa6954ff10327364aa22b` | `9fa94542b1c7b6414e233c9775e72d399baa88a7816e6022be750d05a315ac90` | byte-identical | 80,176,612 / 24 | 10,580 |
| Reims | `c6d9279151eb46aaed42d71ef835606b8d95e7287379ad2e3a1b16b4cf86f69d` | `8313a56024091c8aa31a48019867b8888dc858ea2478eb6cab14e7372055b0b2` | `c88e13a109d3dcf5fdfc5487e52ccf47a93b24a147e6a28b21824f384825f43b` | byte-identical | 25,607,643 / 20 | 6,032 |

## Step 3 — Attendee page traversal

On the organizer laptop, not in the container. Follow `handoff-site/README.md`: put
`LIVE_COACH_TOKEN`, `SUBMISSION_FORM_URL` and `LIVE_ALLOW_CONTROLLED_CLOCK=true` in the ignored
`handoff-site/.env`, then walk `/live` with an ISO-8601 `now` query per scheduled state, and advance
once from `/live/coach`.

Serve `/live` from the exact process you will use on the day. `SUBMISSION_FORM_URL` is read at
runtime from that process, not baked into the build, so a page served from the wrong shell or
directory silently degrades to the USB-only wording with no error.

| Check | Observed | Pass |
|---|---|---|
| `/live` renders the configured Tally form action, not the "not configured" fallback | `https://tally.so/r/81Yy1x` rendered | PASS |
| Every scheduled state renders in order | Opening, B1-B7 and close matched at all nine exact boundaries | PASS |
| Countdown and report prompts display | Countdown/closed state and B3/B6/B7 prompts rendered | PASS |
| Coach advance moves the room one state early | Opening advanced once to B1; repeated request id was `already-applied` | PASS |
| No hold, relock or reversal is reachable | PUT/PATCH/DELETE returned 405; only next-only POST is exposed | PASS |
| No in-session solution path is exposed | Rendered and leakage automation passed | PASS |

## Step 4 — Online form, then the disconnected USB fallback

**Complete:** the configured public action rendered, Tally response `1WRWplp` imported through its
row-specific signed upload URL, and the same fresh Kashiwa bundle then passed the local adapter in a
`--network none` container at identical stored bytes and SHA-256. The signed URL remains only in the
organizer's private CSV export and is not copied into this record.

1. From a device on public Internet, open `/live`, follow the form action, upload one known
   `submission.zip`, paste the SHA-256 that `civ report` printed, submit, and keep the visible
   response identifier. The server receipt timestamp comes from the subsequent CSV export.
2. Export the completed Tally responses as CSV. Keep the export and its signed upload URLs on the
   connected intake laptop, then import the CSV through the row-specific adapter:

```sh
civ intake-tally "$GATE/tally-submissions.csv" --ledger "$LEDGER"
```

The adapter treats Tally's timezone-naive `Submitted at` value as UTC, downloads each row's own
upload URL, and records one terminal outcome per CSV row. Do not use Tally's aggregate batch-download
ZIP as the row-to-upload mapping. If a CSV export is unavailable, use the provider-neutral
`civ intake-form` envelope as the documented recovery path.

3. Remove connectivity from the intake laptop. Copy the identical bundle by USB and import it:

```sh
civ intake-local "$GATE/usb/submission.zip" --ledger "$LEDGER" \
  --identity gate-transport --received-at 2026-09-03T12:21:00+09:00 \
  --sha256 "$(sha256sum "$GATE/usb/submission.zip" | cut -d' ' -f1)" --delivery-id gate-usb-001
```

4. Restore connectivity only after the local receipt has been checked.

| Item | Online receipt | USB receipt |
|---|---|---|
| Identity | `gate-transport` | `gate-transport` |
| Delivery / response id | `1WRWplp` | `issue11-tally-usb` |
| `received_at_original` | `2026-08-26T16:35:33Z` | `2026-09-03T12:21:00+09:00` (controlled event clock) |
| `received_at_utc` | `2026-08-26T16:35:33+00:00` | `2026-09-03T03:21:00+00:00` |
| `bundle_sha256` | `9fa94542b1c7b6414e233c9775e72d399baa88a7816e6022be750d05a315ac90` | same |
| Status | PASS — Tally import, on time | PASS — disconnected local import, on time |

The Tally ledger's stored scorer input and the fresh source bundle independently hash to the same
value. The USB container had no network interface from launch and returned its accepted receipt in
7.6 seconds wall clock including container startup.

## Step 5 — The cohort, the cutoff and quarantine

Twenty-nine ordinary scoreable identities, one exact-cutoff scoreable identity, two late-only
identities and one resubmission, built from the real submissions by varying only the
participant-authored `report.md`. This measures throughput and terminal-state coverage on genuine
bundles; detector-quality diversity is proven by `tests/test_batch.py`, not by this gate.

```sh
cp "$GATE/kashiwa-1/report.md" "$GATE/kashiwa-report.md.orig"
for i in $(seq 1 15); do
  identity=$(printf 'gate-kashiwa-%02d' "$i")
  cp "$GATE/kashiwa-report.md.orig" "$GATE/kashiwa-1/report.md"
  printf '\nEntry: %s\n' "$identity" >> "$GATE/kashiwa-1/report.md"
  civ report "$GATE/kashiwa-1" > /dev/null
  digest=$(sha256sum "$GATE/kashiwa-1/submission.zip" | cut -d' ' -f1)
  civ intake-local "$GATE/kashiwa-1/submission.zip" --ledger "$LEDGER" \
    --identity "$identity" --received-at 2026-09-03T12:20:00+09:00 \
    --sha256 "$digest" --delivery-id "$identity-usb"
done
```

Repeat for `reims-1` with `gate-reims-%02d`, using `seq 1 14`; the exact-cutoff identity below is
the thirtieth scoreable identity. Then add the boundary cases, each with a distinct delivery id and
a fresh bundle built the same way:

| Identity | `--received-at` | Expected |
|---|---|---|
| `gate-kashiwa-01` | `2026-09-03T12:29:59+09:00` | replaces its earlier on-time bundle |
| `gate-cutoff` | `2026-09-03T12:30:00+09:00` | on time, inclusive |
| `gate-late-01` | `2026-09-03T12:30:01+09:00` | quarantined |
| `gate-late-02` | `2026-09-03T12:45:00+09:00` | quarantined |

## Step 6 — Unattended lunch scoring

```sh
/usr/bin/time -v civ score-batch --ledger "$LEDGER" --labels "$LABELS" --output "$GATE/results" \
  2> "$GATE/score-batch.time"
cat "$GATE/results/summary.json"
cat "$GATE/results/performance.json"
```

| Item | Recorded value |
|---|---|
| `entries` / `counts` | 32 terminal entries; 30 scored, 2 quarantined, 0 invalid, 0 failed |
| Scored per dataset | Kashiwa 15; Reims 15 |
| `receipts` totals | 33 total; 31 on-time including the resubmission; 2 late |
| Wall time and peak RSS from `time -v` | 3.43 s; 42,808 KB |
| Socket messages sent / received | 0 / 0 |
| `total_elapsed_seconds` vs the 2,700 s budget | 2.458905 s; within budget |
| Slowest entry | `gate-kashiwa-11`, 0.153825 s, scored |
| Manual interventions required | none during batch scoring |

Expected accounting is 33 receipts (`on_time` 31, including the resubmission; `late` 2) and 32
terminal entries (`scored` 30; `quarantined` 2).

Then confirm the intake contract from the results, without a second tool:

```sh
python - <<'PY'
import json, pathlib
records = {r["identity"]: r for r in map(json.loads, pathlib.Path("results.jsonl").read_text().splitlines())}
print(records["gate-kashiwa-01"]["bundle_sha256"], records["gate-kashiwa-01"]["status"])
print(records["gate-cutoff"]["status"], records["gate-late-01"]["status"], records["gate-late-02"]["status"])
PY
```

`gate-kashiwa-01` must carry the resubmitted bundle hash and be `scored`; `gate-cutoff` must be
`scored`; both `gate-late-*` must be `quarantined` with no datasets.

## Step 7 — Nothing organizer-only escapes

```sh
unzip -l "$GATE/kashiwa-1/submission.zip"
grep -c evidence/ <(unzip -l "$GATE/kashiwa-1/submission.zip") || echo "no clips in bundle"
grep -o '<a label_id from the sealed pack>' "$GATE"/results/*.json* || echo "no label leakage"
```

| Check | Observed | Pass |
|---|---|---|
| Bundle holds exactly the seven metadata artifacts | Both fresh bundles contain the exact expected seven names | PASS |
| No bag, clip or label pack in any bundle | Structural archive check passed | PASS |
| No label id, interval or pack path in `results.jsonl`, `summary.json`, `performance.json` | Structured key/path check passed | PASS |
| Form storage holds only identity, hash and bundle, plus provider receipt metadata | Response `1WRWplp` imported from the six-column organizer export; no bag, clip or label field exists | PASS |

## Failure and intervention log

Every failure, retry, manual repair and discrepancy, with the step it occurred in. An empty log is a
claim that nothing went wrong; leave it empty only if that is true.

| # | Step | What happened | Resolution | Recorded consequence |
|---|---|---|---|---|
| 1 | Preconditions | The uv-prepared environment has no `pip` module, so `python -m pip freeze` failed. | Replaced the read-only version inventory with `importlib.metadata`; reran successfully. | This runbook now uses the compatible probe. |
| 2 | Input inventory | An earlier working note understated the Kashiwa inventory. | Verified the supplied root and received organizer confirmation that it contains 16 sessions, one MCAP per session. | The record and downstream routing now use 16; no data-freeze discrepancy remains. |
| 3 | Attendee page | Vinext loaded worker secrets from `.env`; setting controlled-clock and coach values only in the parent PowerShell process left both unavailable. | Put the ephemeral values in ignored `.env`, restarted, passed, then removed them. | README and this runbook now name the actual worker configuration seam. |
| 4 | Attendee-page verifier | The first close assertion expected the phrase `SESSION CLOSED`; the accepted UI renders `SESSION STATE` with `CLOSED`. | Corrected the verifier to the exact rendered contract and restarted the in-memory coach state. | No product change. |
| 5 | Disconnected USB verifier | The first Docker invocation quoted Windows `--mount` values in a form Docker rejected before starting a container. | Reissued the same command with PowerShell-compatible single-quoted mount specifications. | The corrected `--network none` run passed; no product change. |

## Pass / fail against issue #11

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Host, container identity, dependency versions, input provenance recorded | PASS | Step 1 |
| 2 | Kashiwa completes the offline command path | PASS | Step 2 |
| 3 | Reims completes the unchanged path with permitted differences only | PASS | Step 2 |
| 4 | Repeats are byte-identical with stable submission hashes | PASS | Step 2 |
| 5 | Both runs record time, memory, I/O, disk use and bundle size | PASS | Step 2 |
| 6 | Page traverses every state, accepts a coach advance, exposes no relock or solution | PASS | Step 3 |
| 7 | Online form then USB accept the identical bundle at the same hash | PASS | Step 4 |
| 8 | Resubmission, inclusive cutoff, last-on-time and late quarantine demonstrated | PASS | Steps 5–6 |
| 9 | Thirty authoritative submissions reach terminal results within 45 minutes | PASS | Step 6 |
| 10 | Bags, clips and labels never enter participant bundles or form storage | PASS | Steps 4 and 7 |
| 11 | Every failure and intervention recorded | PASS | Failure log |
| 12 | Consequences routed to the later specs | PASS | Routing |
| 13 | This record states pass/fail per criterion with linked evidence | PASS | This table; external gate directory below |

Machine evidence remains outside Git at
`%LOCALAPPDATA%\Temp\civ-phase1-integrated-gate-20260826\output`.

## Routing

Record each consequence against exactly one destination, or state that none arose.

- **Phase 2 interface freeze** — candidate-contract consequences: none.
- **Contracts, data and evaluation spec** — none; the organizer confirmed 16 Kashiwa sessions, one
  MCAP per session, matching the supplied root.
- **Attendee kit, rehearsal and release spec** — Vinext's accepted worker reads the controlled-clock
  and coach values from ignored `.env`; setting only parent-process variables did not configure the
  live routes. The real Tally-to-USB transport gate passes.
- **Issue #13** — inspection again reported five explicit `ros2idl` field-discovery warnings for
  control mode, gear, steering, turn indicators and velocity status; the accepted detector still
  requires none of them.
