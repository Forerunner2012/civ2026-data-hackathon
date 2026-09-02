# QuickStart: unpacked kit to accepted bundle

Run these steps from the root of the unpacked attendee kit. Everything required by the core path is
already in that kit; the QuickStart does not depend on an online download. Commands below use the
Kashiwa warm-up. For Reims, use `examples/reims/left_turn.yaml` and
`layouts/reims-left-turn.pj4.xml` with the matching Reims MCAP.

## The route at a glance

```mermaid
flowchart LR
    K[Unpacked attendee kit] --> D[1. civ doctor]
    K --> I[2. civ inspect]
    I --> S[3. civ sample]
    I --> V[Optional viewer]
    S --> E[Edit your EventSpec]
    N[4. civ submission-init] --> W[working templates]
    E --> X[5. civ detect]
    W --> X
    X -->|events.jsonl + run-manifest.json| C[6. civ clip]
    C -->|evidence/*.mcap + updated manifest| Q[7. civ score]
    Q -->|metrics.json + updated manifest| R[8. civ report]
    W --> R
    R --> Z[submission.zip + printed SHA-256]

    classDef local fill:#eef5d4,stroke:#647a18,color:#172117
    class V,C local
```

The viewer and evidence clips help your investigation but stay on your machine. Only the validated
metadata bundle is submitted.

## Before step 1: choose local paths

Use the supplied files; do not rename or edit kit inputs:

```text
BAG=data/KSH-64ac27cd029b-signals.mcap
SPEC=examples/kashiwa/right_turn.yaml
LAYOUT=layouts/kashiwa-right-turn.pj4.xml
WORK=working
```

The examples below spell those paths out so they work in PowerShell and POSIX shells alike.

## 1. Check the environment

```text
civ doctor --workspace working --bag data/KSH-64ac27cd029b-signals.mcap --layout layouts/kashiwa-right-turn.pj4.xml --offline-kit .
```

Expected result: `Doctor: READY`. This command downloads, installs, and writes nothing. If it exits
2, follow the printed `Action:` for the failing check and rerun the same command. Use the viewer
shipped under `viewer/<your-platform>/`; its local instructions are in `viewer/README.md`.

## 2. Inventory topics and fields

```text
civ inspect data/KSH-64ac27cd029b-signals.mcap
```

Expected result: bag duration followed by topics, message counts, rates, and fields. This is read
only. A missing topic is not in this bag; confirm the exact dataset path before changing a detector.

## 3. Sample one signal and look at the recording

```text
civ sample data/KSH-64ac27cd029b-signals.mcap --topic /pix_hooke/v2a_steerstafb --field vcu_chassis_steer_angle_fb --limit 4
```

Expected result: up to four timestamped values printed to the terminal. Nested fields use dotted
paths; `--start-ns` and `--end-ns` narrow the window. This command writes nothing.

For a visual inspection, open the same signal MCAP and `layouts/kashiwa-right-turn.pj4.xml` in the
supplied PlotJuggler. In Lichtblick, open the signal MCAP together with its same-source companion
from `context/kashiwa/`, then load `layouts/lichtblick-kashiwa-right-turn.json`. Do not mix source
IDs. If a viewer does not start, continue with `civ sample` or the supplied `fallback/` material.

## 4. Create your working submission once

```text
civ submission-init working --shell powershell
```

Use `--shell posix` on Linux or macOS. This creates `working/README.md`, an incomplete detector,
report and figure template, plus exactly one reproduction script. It never overwrites an existing
directory. If `working/` already exists, keep it or choose a new empty path.

## 5. Detect intervals

First run the supplied EventSpec without writing:

```text
civ detect examples/kashiwa/right_turn.yaml data/KSH-64ac27cd029b-signals.mcap --output working --dry-run
```

Then copy the relevant logic into `working/detector/detector.yaml`, make one evidence-led change,
and write the run:

```text
civ detect working/detector/detector.yaml data/KSH-64ac27cd029b-signals.mcap --output working
```

Expected result: `working/events.jsonl`, a byte-for-byte EventSpec copy under `working/detector/`,
and `working/run-manifest.json`. Inputs are never rewritten. If zero events appear, loosen one
condition or timing value and rerun `--dry-run` before writing again.

## 6. Extract local evidence

```text
civ clip working/events.jsonl data/KSH-64ac27cd029b-signals.mcap
```

Expected result: one `working/evidence/<event_id>.mcap` per event and clip facts added to the run
manifest. Reopen a clip in a supplied viewer. A failure names the missing topic or empty window;
every `evidence.topics` entry must exist in the same bag used by `civ detect`.

## 7. Score against the supplied development labels

```text
civ score working --labels <supplied-development-labels.json>
```

Use the development-label path announced by the organizers and present in the attendee kit; do not
substitute an organizer path. Expected result: `working/metrics.json` plus its hash in the updated
run manifest. Inspect at least one false positive, false negative, boundary error, or ambiguity and
record what you changed in `working/report.md`.

## 8. Validate, package, and submit

Complete the five report headings, replace the figure, and make the reproduction script rerun the
same path. Then:

```text
civ report working
```

Expected result: `working/submission.zip` and its SHA-256 printed to the terminal. Submit the ZIP
unchanged with the printed hash and your participant/team identity through the form shown on the
live page. If the form is unavailable, give those same three items to the organizer by USB.

No bag and no clip is ever bundled. Signal and context MCAPs, extracted frames, and
`working/evidence/` stay local.

## Command products and dependencies

| Order | Command | Reads | Prints or writes | Used by |
| ---: | --- | --- | --- | --- |
| 1 | `civ doctor` | kit, bag, layout, workspace path | readiness only; no files | your recovery decision |
| 2 | `civ inspect` | MCAP | topic/field inventory; no files | `sample`, EventSpec design |
| 3 | `civ sample` | MCAP + topic + field | timestamped values; no files | EventSpec design, report figure |
| 4 | `civ submission-init` | built-in templates | detector/report/figure/reproduction templates | `detect`, `report` |
| 5 | `civ detect` | EventSpec + MCAP + declared resources | `detector/` with exact resources, `events.jsonl`, v2 `run-manifest.json`, optional `extension/manifest.json` | `clip`, `score`, `report` |
| 6 | `civ clip` | events + same MCAP + manifest | `evidence/*.mcap`, updated manifest | visual review, `report` manifest checks |
| 7 | `civ score` | working directory + supplied labels | `metrics.json`, updated manifest | report argument, `report` |
| 8 | `civ report` | completed working directory | `submission.zip` + SHA-256 | organizer intake |

## Working directory versus submission

```text
working/
├── detector/detector.yaml      submitted
├── detector/<resource path>    submitted when declared by EventSpec
├── events.jsonl                submitted
├── run-manifest.json           submitted
├── metrics.json                submitted
├── report.md                   submitted
├── figure.svg                  submitted
├── reproduce.ps1 or .sh        submitted
├── extension/manifest.json     submitted when extension payloads exist
├── extension/*                 optional provenance, inert traces, tests
├── submission.zip              hand in unchanged
└── evidence/<event_id>.mcap    local only
```

The seven core artifacts remain mandatory. A v2 extension may carry at most eight declared
payloads (1 MiB each, 4 MiB combined). `civ report` rejects undeclared, changed, forbidden, unsafe,
or case-colliding files. Intake validates but never runs a submitted trace or regression test.

## Recovery references

- Viewer problem: use `civ sample` and `fallback/<dataset>/`, then raise the printed help card.
- Container problem: pair with another participant while a coach repairs the machine.
- Command problem: read the exact diagnostic, fix only the named input, and rerun that command.
- Submission problem: rerun `civ report`; never manually edit or recompress `submission.zip`.
