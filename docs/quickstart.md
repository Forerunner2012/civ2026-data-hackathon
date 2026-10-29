# Quickstart: unpacked kit to metadata bundle

First install the participant CLI using the [setup instructions](setup.md). Use native Windows AMD64 or native Linux AMD64; WSL2 is an optional Linux route on Windows. Run these steps from the root of the unpacked attendee kit with its supplied local recordings, EventSpecs and practice labels. Once the CLI and those inputs are available, the core workflow does not need a network connection. See [runtime requirements](runtime-requirements.md). Commands below use the Kashiwa warm-up. For Reims, use `examples/reims/left_turn.yaml` and `layouts/reims-left-turn.pj4.xml` with the matching Reims MCAP.

## Dataset access and terms

The public [URT-Kashiwa dataset page](https://github.com/tlab-wide/URT-Kashiwa) remains available.
See Tsukada Laboratory's [publisher page for the URT-Kashiwa dataset](https://tlab.hongo.wide.ad.jp/portfolio/urt-kashiwa-dataset-unprotected-right-turn-kashiwa-campus/)
for the dataset description. Follow the repository's attribution terms. Reims recordings are
limited to registered CIV 2026 participants for event learning and demonstration. Do not
redistribute them. Delete participant copies derived from source recordings after the event. For
Reims access questions, use the maintainer's
[GitHub profile](https://github.com/Forerunner2012) or
[LinkedIn profile](https://www.linkedin.com/in/matthieucarreutc/). Do not forward direct download
links.

## Install before the first command

With Git and uv available, run in PowerShell or a Linux shell while connected:

```text
uv tool install --python 3.12 "git+https://github.com/Forerunner2012/civ2026-data-hackathon.git@main#subdirectory=participant"
uv tool update-shell
```

Restart your shell, then run `civ --help`. Follow [setup and recovery](setup.md) if access, PATH, Python or the matching wheel backup needs attention. After installation, run the steps below from the root of the unpacked kit.

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
metadata bundle enters `submission.zip`.

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
civ doctor --workspace . --bag data/KSH-64ac27cd029b-signals.mcap --layout layouts/kashiwa-right-turn.pj4.xml --offline-kit .
```

The command checks the current writable kit directory before `working/` exists. If the kit directory is read-only, pass another existing writable directory with `--workspace`. Do not pre-create `working/`; step 4 creates the submission workspace.

Expected result: `Doctor: READY`. This command downloads, installs, and writes nothing. If it exits 2, follow the printed `Action:` for the failing check and rerun the same command. Use the viewer shipped under `viewer/<your-platform>/`; its local instructions are in `viewer/README.md`.

## 2. Inventory topics and fields

```text
civ inspect data/KSH-64ac27cd029b-signals.mcap
```

Expected result: bag duration followed by topics, message counts, rates, and fields. This is read only. A missing topic is not in this bag; confirm the exact dataset path before changing a detector.

## 3. Sample one signal and look at the recording

```text
civ sample data/KSH-64ac27cd029b-signals.mcap --topic /pix_hooke/v2a_steerstafb --field vcu_chassis_steer_angle_fb --limit 4
```

Expected result: up to four timestamped values printed to the terminal. Nested fields use dotted paths; `--start-ns` and `--end-ns` narrow the window. This command writes nothing.

For a visual inspection, open the same signal MCAP and `layouts/kashiwa-right-turn.pj4.xml` in the supplied PlotJuggler. In Lichtblick, open the signal MCAP together with its same-source companion from `context/kashiwa/`, then load `layouts/lichtblick-kashiwa-right-turn.json`. Do not mix source IDs. If a viewer does not start, continue with `civ sample` or the supplied `fallback/` material.

## 4. Create your working submission once

```text
civ submission-init working --shell posix
```

Use `--shell powershell` when running in PowerShell on Windows. This creates `working/README.md`, an incomplete detector, report and figure template, plus exactly one reproduction script. It never overwrites an existing directory. If `working/` already exists, keep it or choose a new empty path.

## 5. Detect intervals

First run the supplied EventSpec without writing:

```text
civ detect examples/kashiwa/right_turn.yaml data/KSH-64ac27cd029b-signals.mcap --output working --dry-run
```

Then copy the relevant logic into `working/detector/detector.yaml`, make one evidence-led change, and write the run:

```text
civ detect working/detector/detector.yaml data/KSH-64ac27cd029b-signals.mcap --output working
```

Expected result: `working/events.jsonl`, a byte-for-byte EventSpec copy under `working/detector/`, and `working/run-manifest.json`. Inputs are never rewritten. If zero events appear, loosen one condition or timing value and rerun `--dry-run` before writing again.

## 6. Extract local evidence

```text
civ clip working/events.jsonl data/KSH-64ac27cd029b-signals.mcap
```

With detections, expect one `working/evidence/<event_id>.mcap` per event and clip facts added to the run manifest. Reopen a clip in a supplied viewer. With zero events, the command writes no clips; inspect your conditions and timing, then continue to scoring and reporting to record the result. A failure names the missing topic or empty window; every `evidence.topics` entry must exist in the same bag used by `civ detect`.

## 7. Score against the supplied practice labels

```text
civ score working --labels PRACTICE_LABELS.json
```

The Kashiwa warm-up is the first practice target. Organizers are encouraged to share complete, source-bound practice labels in the same space as participant kits, at a time they choose. Use practice labels for learning and self-evaluation. Development metrics do not guarantee results on sealed evaluation, whose truth remains organizer-only.

Replace `PRACTICE_LABELS.json` with the complete practice pack matched to the exact source and event definition announced for your kit. Do not substitute organizer truth, a partial answer key, or labels for a different event. The repository's reserved practice-labels folder contains no real label JSON; use the pack supplied for your session. Expected result: `working/metrics.json` plus its hash in the updated run manifest. Inspect at least one false positive, false negative, boundary error, or ambiguity and record what you changed in `working/report.md`.

When no matching practice labels are supplied, run `civ score working` without `--labels`. It writes `civ.metrics/v2` with `status: "not_evaluated"` and null metrics. Continue to `civ report`; packaging does not require truth access. Explain your manual inspection and uncertainty in the report. A supplied missing or invalid label file remains an error and never silently becomes an unevaluated run.

## 8. Validate and keep the metadata-only ZIP

Complete the five report headings and replace the figure before running the generated reproduction script. It runs detection, clips, practice or unevaluated scoring, and packaging. Use the exact source and matching practice pack, with a new output directory to keep the completed submission unchanged:

```sh
sh working/reproduce.sh data/KSH-64ac27cd029b-signals.mcap PRACTICE_LABELS.json reproduced
```

For a track without matching practice truth, use `-` as the second argument. This records `not_evaluated`, not a zero score:

```sh
sh working/reproduce.sh data/REIMS_SIGNALS.mcap - reproduced-reims
```

PowerShell uses the same argument order: `./working/reproduce.ps1 DATASET PRACTICE_LABELS.json reproduced`. Omit the third argument only when you intend to regenerate the existing workspace. The script stops on a failed command and refuses an existing explicit output directory. Fresh runs copy the detector/resources, declared extension payloads, report, figure and script; labels and recordings stay outside the output. Valid extension declarations survive detection. Finish and declare any optional payloads before the reproduction check.

Compare `events.jsonl`, `metrics.json` and clip hashes with the original run. Record the source, EventSpec/resource hashes, CLI/Python versions and the exact command in your report. Explain any material differences. Packaging alone does not establish reproducibility or earn its assessment points.

If you replace the generated script, keep a direct command line beginning with `civ detect` or `uv run civ detect`. PowerShell may prefix either with `&`. The static validator does not recognize wrappers or command variables and never executes submitted scripts.

To package an already completed workspace directly:

```text
civ report working
```

Expected result: `working/submission.zip` and its SHA-256 printed to the terminal. The historical
submission form and USB instructions are retired; this repository provides no active collection
route or intended recipient. See the [submission fields and bundle contract](submission-fields.md)
for the historical collection fields and current metadata-only ZIP contents.

No bag and no clip is ever bundled. Signal and context MCAPs, extracted frames, and `working/evidence/` stay local.

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
| 8 | `civ report` | completed working directory | validated `submission.zip` + SHA-256 | local ZIP and hash preservation |

## Working directory and metadata-only ZIP

```text
working/                         ZIP contents
├── detector/detector.yaml      yes
├── detector/<resource path>    yes, when declared by EventSpec
├── events.jsonl                yes
├── run-manifest.json           yes
├── metrics.json                yes
├── report.md                   yes
├── figure.svg                  yes
├── reproduce.ps1 or .sh        yes
├── extension/manifest.json    yes, when extension payloads exist
├── extension/*                 optional provenance, inert traces, tests
├── submission.zip              local archive; keep unchanged
└── evidence/<event_id>.mcap    local only
```

The seven core artifacts remain mandatory in the ZIP. A v2 extension may carry at most eight declared payloads (1 MiB each, 4 MiB combined). `civ report` rejects undeclared, changed, forbidden, unsafe, or case-colliding files. The ZIP validator does not execute declared traces or regression tests.

## Recovery references

- Viewer problem: use `civ sample` and `fallback/<dataset>/`, then raise the printed help card.
- CLI setup problem: follow [setup and recovery](setup.md), or pair with another participant while a coach helps. Container recovery is optional.
- Command problem: read the exact diagnostic, fix only the named input, and rerun that command.
- ZIP problem: rerun `civ report`; keep its validated `submission.zip` and printed SHA-256 locally. Never manually edit or recompress the ZIP.
