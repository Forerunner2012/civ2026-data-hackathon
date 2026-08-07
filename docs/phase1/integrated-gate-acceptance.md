# Integrated Phase 1 gate acceptance record

Status: **not yet run — this document is the pre-authored record to fill while the gate executes**

Recorded: _(date of the run)_ · Operator: _(name)_

Every table below has blanks because an unrecorded workaround is a failed gate, not an accepted
success. Fill each value as the step completes rather than reconstructing it afterwards. Do not
commit bags, clips, label packs, generated submissions, ledgers, caches or runtime state; only this
record enters the repository.

## Preconditions

- The pinned forward environment from [`lyrical-acceptance.md`](lyrical-acceptance.md): official
  ROS 2 Lyrical / Ubuntu 26.04 linux-amd64 base digest
  `sha256:122a787d0eb7e1b2c18370e35ef394332db5c11d242bea6f05f2b2911e26b04d`, managed CPython
  3.12.11, dependency volume prepared and mounted read-only.
- Both authorized sources mounted read-only: the Kashiwa bag from
  [`kashiwa-acceptance.md`](kashiwa-acceptance.md) and the French chunk from
  [`french-acceptance.md`](french-acceptance.md).
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
FRENCH=/data/french.mcap
LABELS=/labels            # read-only organizer packs
LEDGER=$GATE/intake
```

## Step 1 — Environment and input provenance

```sh
uname -srm
head -2 /etc/os-release
python -V
python -c "import civ_workshop; print(civ_workshop.__version__)"
python -m pip freeze
sha256sum "$KASHIWA" "$FRENCH" "$LABELS"/*.json
```

| Item | Recorded value |
|---|---|
| Host and CPU | |
| Container base digest | |
| Prepared image ID | |
| OS / ROS distribution / architecture | |
| CPython | |
| `civ-workshop` | |
| `mcap` / `mcap-ros2-support` / `PyYAML` / `cel-python` | |
| Kashiwa bag bytes and SHA-256 | |
| French chunk bytes and SHA-256 | |
| Kashiwa label pack SHA-256 | |
| French label pack SHA-256 | |

## Step 2 — Both datasets through the offline command path, twice

Run this for `kashiwa` and again for `french`, with `pass` 1 and 2. Copy the authored `report.md`,
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
| Kashiwa | `civ inspect` | | | | | |
| Kashiwa | `civ detect` | | | | | |
| Kashiwa | `civ clip` | | | | | |
| Kashiwa | `civ score` | | | | | |
| Kashiwa | `civ report` | | | | | |
| French | `civ inspect` | | | | | |
| French | `civ detect` | | | | | |
| French | `civ clip` | | | | | |
| French | `civ score` | | | | | |
| French | `civ report` | | | | | |

Every socket cell must read zero. Expected results to confirm against the sealed records: Kashiwa
TP 2, FP 3, FN 1, F1 0.5, mean IoU 0.644663772045; French TP 1, FP 0, FN 0, F1 1.0, mean IoU
0.800631349.

```sh
sha256sum "$GATE"/kashiwa-[12]/events.jsonl "$GATE"/kashiwa-[12]/metrics.json "$GATE"/kashiwa-[12]/submission.zip
sha256sum "$GATE"/french-[12]/events.jsonl "$GATE"/french-[12]/metrics.json "$GATE"/french-[12]/submission.zip
du -sb "$GATE"/kashiwa-1 "$GATE"/french-1
find "$GATE"/kashiwa-1 -type f | wc -l
```

| Dataset | `events.jsonl` | `metrics.json` | `submission.zip` | Pass 1 vs pass 2 | Working-dir bytes / files | Bundle bytes |
|---|---|---|---|---|---|---|
| Kashiwa | | | | | | |
| French | | | | | | |

## Step 3 — Attendee page traversal

On the organizer laptop, not in the container. Follow `handoff-site/README.md`: set
`LIVE_COACH_TOKEN`, `SUBMISSION_FORM_URL` and `LIVE_ALLOW_CONTROLLED_CLOCK=true`, then walk `/live`
with an ISO-8601 `now` query per scheduled state, and advance once from `/live/coach`.

| Check | Observed | Pass |
|---|---|---|
| Every scheduled state renders in order | | |
| Countdown and report prompts display | | |
| Coach advance moves the room one state early | | |
| No hold, relock or reversal is reachable | | |
| No in-session solution path is exposed | | |

## Step 4 — Online form, then the disconnected USB fallback

1. From a device on public Internet, open `/live`, follow the form action, upload one known
   `submission.zip`, paste the SHA-256 that `civ report` printed, submit, and keep the visible
   server receipt timestamp and response identifier.
2. Build the envelope from the export using the mapping in `intake-acceptance.md`, then import it
   beside the downloaded bundle:

```sh
civ intake-form "$GATE/form-response.json" --ledger "$LEDGER"
```

3. Remove connectivity from the intake laptop. Copy the identical bundle by USB and import it:

```sh
civ intake-local "$GATE/usb/submission.zip" --ledger "$LEDGER" \
  --identity gate-transport --received-at 2026-09-03T12:21:00+09:00 \
  --sha256 "$(sha256sum "$GATE/usb/submission.zip" | cut -d' ' -f1)" --delivery-id gate-usb-001
```

4. Restore connectivity only after the local receipt has been checked.

| Item | Online receipt | USB receipt |
|---|---|---|
| Identity | | |
| Delivery / response id | | |
| `received_at_original` | | |
| `received_at_utc` | | |
| `bundle_sha256` | | |
| Status | | |

The two `bundle_sha256` values must be identical. Record the wall-clock gap between removing
connectivity and the accepted local receipt.

## Step 5 — The cohort, the cutoff and quarantine

Thirty scoreable identities plus two late-only identities and one resubmission, built from the real
submissions by varying only the participant-authored `report.md`. This measures throughput and
terminal-state coverage on genuine bundles; detector-quality diversity is proven by
`tests/test_batch.py`, not by this gate.

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

Repeat for `french-1` with `gate-french-%02d`. Then add the boundary cases, each with a distinct
delivery id and a fresh bundle built the same way:

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
| `entries` / `counts` | |
| Scored per dataset | |
| `receipts` totals | |
| Wall time and peak RSS from `time -v` | |
| Socket messages sent / received | |
| `total_elapsed_seconds` vs the 2,700 s budget | |
| Slowest entry | |
| Manual interventions required | |

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
| Bundle holds exactly the seven metadata artifacts | | |
| No bag, clip or label pack in any bundle | | |
| No label id, interval or pack path in `results.jsonl`, `summary.json`, `performance.json` | | |
| Form storage holds only identity, hash and bundle | | |

## Failure and intervention log

Every failure, retry, manual repair and discrepancy, with the step it occurred in. An empty log is a
claim that nothing went wrong; leave it empty only if that is true.

| # | Step | What happened | Resolution | Recorded consequence |
|---|---|---|---|---|
| | | | | |

## Pass / fail against issue #11

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Host, container identity, dependency versions, input provenance recorded | | Step 1 |
| 2 | Kashiwa completes the offline command path | | Step 2 |
| 3 | French completes the unchanged path with permitted differences only | | Step 2 |
| 4 | Repeats are byte-identical with stable submission hashes | | Step 2 |
| 5 | Both runs record time, memory, I/O, disk use and bundle size | | Step 2 |
| 6 | Page traverses every state, accepts a coach advance, exposes no relock or solution | | Step 3 |
| 7 | Online form then USB accept the identical bundle at the same hash | | Step 4 |
| 8 | Resubmission, inclusive cutoff, last-on-time and late quarantine demonstrated | | Steps 5–6 |
| 9 | Thirty authoritative submissions reach terminal results within 45 minutes | | Step 6 |
| 10 | Bags, clips and labels never enter participant bundles or form storage | | Step 7 |
| 11 | Every failure and intervention recorded | | Failure log |
| 12 | Consequences routed to the later specs | | Routing |
| 13 | This record states pass/fail per criterion with linked evidence | | This table |

## Routing

Record each consequence against exactly one destination, or state that none arose.

- **Phase 2 interface freeze** — candidate-contract consequences: _(none / …)_
- **Contracts, data and evaluation spec** — data and evaluator consequences: _(none / …)_
- **Attendee kit, rehearsal and release spec** — page, intake and rehearsal consequences:
  _(none / …)_
- **Issue #13** — any Tier IV `ros2idl` finding surfaced by the inspection step: _(none / …)_
