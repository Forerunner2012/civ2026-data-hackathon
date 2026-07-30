# CIV 2026 Data Hackathon — planning and experience handoff

> **Status:** internal working baseline for organizers and attendee-perspective review.  
> **Decision rule used:** the initial brainstorming establishes the intent; the documents in `exploration/side-chat-explorations/` refine and, where they conflict, override the earlier implementation shape.  
> **Working title:** **Data Detective — from raw bag to defensible proof**.

## 1. Executive decision

CIV 2026 should be a **three-hour, team-based data investigation workshop** in the ROS 2 ecosystem. Attendees explore a robot/vehicle recording, turn an observation into executable extraction logic, apply that logic across several recordings, inspect failure cases, and present compact evidence plus an operational recommendation.

The organizer provides the execution system. Attendees provide the valuable reasoning:

- which signals and fields matter;
- which transformations, comparisons, temporal conditions, or model inference identify the event;
- how duplicate detections and evidence windows are handled;
- which topics belong in the extracted clip;
- what the results mean, where the detector fails, and what action should follow.

The attendee journey is:

```text
observe → formalize → contextualize → temporalize → scale → challenge → transfer
```

The technical journey prepared by organizers is:

```text
MCAP → PlotJuggler 4 exploration → selected signals in Polars
     → derived features → CEL/EventSpec condition → normalized intervals
     → MCAP evidence clips → visual validation → score + explanation
```

The event is **not** an infrastructure-building contest. Attendees should not have to implement MCAP parsing, ROS message discovery, time synchronization, batch scheduling, provenance, clip generation, or hidden-label scoring.

## 2. Intention and what is new

### Enduring intention from CIV 2025

Make the complete data loop tangible: reduce hours of heterogeneous robotics logs to a few useful, annotated evidence windows, then connect those windows to acquisition, validation, debugging, or operations.

### CIV 2026 shift

| Before / common failure mode | CIV 2026 intention |
|---|---|
| Product-centered workflow | Open, file-first contracts and replaceable tools |
| “Find the timestamp” | Produce a defensible evidence package |
| Upload or inspect everything | Selective extraction and explicit volume reduction |
| Threshold demonstrated once | Reusable logic executed across multiple bags |
| Success-only demo | False-positive / false-negative investigation |
| Notebook or screenshots | One-command, structured, reproducible submission |
| AI as a chatbot or trend | AI as an optional, bounded investigation accelerator with tool traces |
| Opaque result | Provenance: input hash, spec version, parameters, evidence, and run manifest |

The novelty is therefore **workflow intelligence**, not merely generative AI. Teams experience how an observation becomes reusable engineering knowledge and how that knowledge can drive action in three deployment modes:

1. **Fully online:** raw data and computation are centralized.
2. **Partially offline:** data stays local for part of the workflow; selected computation is offloaded.
3. **Edge triage:** the device selects compact evidence; learning and deeper analysis are offloaded.

## 3. Strategic planning

### 3.1 North-star outcome

An attendee leaves able to explain and demonstrate how to go from a raw robotics log to a compact, repeatable, evidence-backed detection workflow—and how the same pattern applies to their professional system.

### 3.2 Strategic objectives

1. **Awareness:** reveal that robotics analytics is a workflow spanning acquisition, quality, search, extraction, validation, and action.
2. **Capability:** give attendees a working mental model and an executable detector, not only slides.
3. **Open replacement:** preserve the useful Smart Data loop without recreating the unavailable historical platform.
4. **Trust:** make evidence, failure analysis, provenance, and reproducibility part of the definition of success.
5. **AI literacy:** show where an agent helps and where deterministic tools, permissions, and human judgment remain mandatory.
6. **Transfer:** connect the exercise to fleet acquisition, test validation, debugging, and operations.

### 3.3 Design principles

- **Evidence-first:** a timestamp without synchronized context is incomplete.
- **Local-first and offline-capable:** the required path must not depend on SaaS accounts, personal keys, or event-day downloads.
- **Deterministic core, optional agent:** everyone can finish without a model; advanced teams may add a bounded, traceable agent.
- **Progressive disclosure:** one sample bag and one condition before multimodal and temporal logic.
- **Quality over event count:** false positives, missed events, missing data, duplicates, and unstable thresholds matter.
- **One prepared golden path:** attendee time is spent on reasoning, not ROS/container plumbing.
- **Open contracts:** MCAP, EventSpec/JSON Schema, JSONL, run manifests, and portable reports are the stable seams.
- **Clean implementation boundary:** replace observable workflow capabilities. The line runs around the **Heex stack and its terminology** — never *System, Datasource, Signal, Trigger, Recording*; always *bag, topic, field, EventSpec, detector, event, clip, manifest*. It does **not** run around the domain logic: condition expressions and their thresholds describe this vehicle in this dataset and are reusable. Settled in [ticket 07](.scratch/civ2026-challenge-spec/issues/07-clean-room-boundary.md).

### 3.4 Strategic success criteria

The event is strategically successful if:

- at least 80% of teams complete a batch run and valid submission;
- every final pitch shows one piece of evidence and one failure or ambiguity;
- a fresh laptop can run the required path offline;
- the same submission produces stable results on rerun;
- attendees can name a realistic downstream action and deployment mode;
- agent use, when present, points to executed tools and evidence rather than unsupported claims.

### 3.5 Non-goals

- rebuilding a full fleet-data platform;
- teaching ROS installation or container debugging;
- requiring a dashboard, a GPU, a paid model, or an API key;
- grading prompt style;
- asking every team to invent an advanced anomaly detector;
- deploying real edge/OTA infrastructure during the session.

## 4. Tactical planning

### 4.1 Challenge shape

Use one coherent challenge with progressive ambition:

- **Warm-up — Smart Data OSS:** guided signal exploration and a first executable condition.
- **Main challenge — Data Detective:** investigate a scenario, combine context and time, batch the detector, and build a case from evidence.
- **Bonus — Agent / advanced analytics:** use a bounded agent, similarity search, anomaly detection, multimodal reasoning, or a regression test. Bonus cannot compensate for an irreproducible core.

This is one ladder, not three parallel hackathons.

### 4.2 Three-hour run of show

| Time | Attendee activity | Observable checkpoint | Driving force |
|---|---|---|---|
| 00:00–00:30 | **Observe:** guided exploration of one development bag | Relevant topic, field, and candidate window | Curiosity + low-friction first success |
| 00:30–01:00 | **Formalize:** write one comparison and run it | First normalized event and evidence clip | Executability, not speculation |
| 01:00–01:45 | **Contextualize + temporalize:** add AND/OR, a derived feature, duration, transition, or ordering | Improved EventSpec/detector with stated hypothesis | Physical meaning + noise reduction |
| 01:45–02:15 | **Scale:** batch execution over development bags | `events.jsonl`, clips, metrics, run manifest | Reuse and fleet-scale thinking |
| 02:15–02:45 | **Challenge:** inspect one false positive, false negative, missing signal, or ambiguous case | Documented failure and one iteration | Hidden labels + quality pressure |
| 02:45–03:00 | **Transfer:** three-minute evidence pitch | Question, proof, limit, next action, professional transfer | Communication + operational relevance |

If more time becomes available, add it to investigation and pitch review—not to installation.

### 4.3 Participant brief

> A fleet recorded several passages through a shared environment. A risky or operationally significant behaviour was reported, but the report is incomplete. Your team must locate relevant occurrences, encode a reusable detector, extract compact evidence, evaluate its limitations, and recommend what should happen when the event is detected.

### 4.4 Participant deliverable

Each team presents and submits:

1. the engineering question and detection hypothesis;
2. the data used, missing, or judged unreliable;
3. an executable EventSpec or detector;
4. normalized `events.jsonl` and compact MCAP evidence clips;
5. a run manifest and metrics;
6. one synchronized evidence view;
7. one false positive, false negative, or ambiguity and the resulting change;
8. a one-command reproduction path;
9. the downstream action and the relevant deployment mode;
10. optional agent trace or advanced-analysis artifact.

### 4.5 Ownership boundary

| Attendees own | Organizers provide |
|---|---|
| Signal and field selection | MCAP/ROS decoding and schema availability |
| Preprocessing and derived features | Topic/field inventory and sampling utilities |
| Thresholds, CEL logic, or model inference | Deterministic detector runner |
| Boolean and temporal composition | Batch iteration and time synchronization |
| Debounce/deduplication parameters | Clip extraction and standardized output |
| Evidence-window duration and retained topics | Hashes, provenance, and run manifest |
| Statistical analysis and interpretation | Hidden labels and scoring infrastructure |
| Failure analysis and professional transfer | Tested visualization layouts and offline bundle |

### 4.6 Evaluation

Recommended common score: 100 points.

| Category | Points | What the jury looks for |
|---|---:|---|
| Investigation and hypothesis | 15 | Deliberate signal choice, inspection, physical reasoning |
| Detection | 25 | Accuracy, temporal logic, duplicates, robustness |
| Evidence and extraction | 15 | Useful context, correct clips, meaningful volume reduction |
| Quality and evaluation | 15 | Metrics, failure analysis, missing/bad data handling |
| Visualization and explanation | 15 | Synchronized, legible proof and careful claims |
| Reproducibility | 15 | One command, pinned inputs, manifest, stable output |

Optional bonus, maximum 20 points:

- bounded agent with useful trace: 10;
- advanced multimodal or data-quality method: 5;
- regression test created from a discovered failure: 5.

### 4.7 Facilitation mechanics

- Teams of 3–5 with suggested roles: investigator, detector author, evidence reviewer, and pitch owner.
- One shared warm-up; coaches intervene on blocked tooling after a short timebox.
- Visible checkpoints at 30, 60, 105, 135, and 165 minutes.
- A public development score can validate format and basic metrics; final ranking uses hidden labels.
- Coaches ask for evidence and assumptions before suggesting thresholds.
- A fallback pack contains pre-extracted tables and clips so data reasoning can continue if ROS/container execution fails.

## 5. Operational planning

### Phase 0 — lock the challenge contract

Decide the scenario, duration, team count, target hardware/OS, data rights, required skill floor, scoring role of agentic work, and the definition of “open source.”

**Gate:** one-page challenge contract approved.

### Phase 1 — prove the organizer vertical slice

On one authorized bag, complete:

```text
MCAP → inspect → PlotJuggler 4 → detector → batch runner
     → events.jsonl → evidence clip → score → report
```

Measure runtime, RAM, disk use, bundle size, and offline behaviour.

**Gate:** complete path works on the minimum supported machine without Internet.

### Phase 2 — freeze interfaces and golden path

- version EventSpec and event-output schemas;
- implement `doctor`, `inspect`, `sample`, `detect`, `clip`, `score`, and `report`;
- provide declarative CEL/EventSpec support;
- decide whether custom Python detectors are a supported advanced path;
- embed or bundle custom ROS schemas;
- prepare a reference detector and one-page quickstart;
- pin runtime and dependencies.

**Gate:** a new user gets from unpacking the kit to a first clip in under 20 minutes.

### Phase 3 — build data and evaluation

- prepare `sample/`, `dev/`, and hidden `test/` sets;
- publish a dataset manifest with sizes, durations, topics, hashes, provenance, and licence;
- create partial development annotations and sealed ground truth;
- define temporal matching tolerance, duplicate policy, and missing-data cases;
- calibrate scoring against multiple deliberately different detectors;
- inject one or two educational quality defects;
- ensure evidence clips do not leak hidden labels.

**Gate:** scoring rewards robust reasoning and separates plausible solutions without requiring one magic threshold.

### Phase 4 — package the attendee experience

- preconfigure PlotJuggler 4 layouts; add Lichtblick only if synchronized robotic context requires it;
- prepare warm-up, challenge brief, cheat sheet, submission template, and pitch template;
- create organizer solution, coach guide, troubleshooting tree, and checkpoint prompts;
- prepare the optional agent tool boundary and trace example only after the deterministic path is stable;
- build offline caches/bundles and a non-ROS fallback pack.

**Gate:** all attendee-facing instructions fit behind one start page and one primary command path.

### Phase 5 — rehearse and release-candidate

- fresh-install on each supported OS/hardware class;
- disconnect the Internet and rerun;
- rehearse with representative novices and advanced users;
- simulate simultaneous dataset distribution and scoring;
- time every checkpoint and the final pitch turnover;
- verify hashes, licences, SBOM, model-card/weight licence if applicable, and recovery media;
- freeze versions several weeks before the event.

**Gate:** a two-hour internal mini-hackathon completes with no organizer-only workaround.

## 6. Required kit and readiness definition

### Data

- authorized MCAP source data with embedded or bundled schemas;
- small warm-up sample, several development bags, sealed test bags;
- dataset manifest, checksums, provenance, and redistribution terms;
- partial labels, hidden labels, and documented quality defects;
- CPU/laptop-sized variant and distribution plan.

### Code, API, and contracts

- versioned EventSpec schema;
- stable event record schema and run manifest;
- narrow detector interface;
- deterministic batch engine;
- evidence-window extraction and topic filtering;
- offline evaluator and report generator;
- optional read-only agent tools with bounded structured input/output.

### CLI and binaries

Minimum commands:

```text
civ doctor
civ inspect BAG
civ sample BAG --topic ...
civ detect SPEC DATASET [--dry-run]
civ clip EVENTS DATASET
civ score SUBMISSION
civ report SUBMISSION
```

Distribute a prebuilt, versioned bundle/image and checksums. No compile or package download should be required on the event day.

### Dependencies and views

- one pinned ROS 2 distribution and MCAP tooling;
- PlotJuggler 4 as the primary signal exploration surface;
- Python MCAP reader + Polars for selected signals and derived features;
- CEL evaluation inside EventSpec;
- Lichtblick only where images, transforms, point clouds, or synchronized replay add required evidence;
- CPU-only baseline; GPU/model path strictly optional;
- locked dependency files, offline cache, and licence/SBOM inventory.

### Submission structure

```text
submission/
├── detector/              # EventSpec and optional code
├── events.jsonl           # normalized detections
├── evidence/              # compact MCAP clips
├── metrics.json
├── run-manifest.json      # versions, hashes, parameters, timings
├── report.md              # hypothesis, evidence, failure, transfer
└── reproduce.ps1|sh       # one-command entry point
```

## 7. Driving forces during the hackathon

The attendee experience is shaped by seven forces:

1. **A concrete engineering question** prevents aimless visualization.
2. **Heterogeneous physical data** forces translation from behaviour to signals.
3. **Limited time and compute** reward reduction, prioritization, and prepared tooling.
4. **Partial and hidden truth** creates a real validation loop instead of answer copying.
5. **Evidence requirements** prevent unsupported timestamps or AI claims.
6. **Failure visibility** makes false positives, missed cases, and poor-quality data productive.
7. **Operational transfer** turns the detector into a decision: annotate, collect, notify, validate, or investigate.

Competition provides energy, but the main pedagogical pressure comes from the checkpoints and proof contract. Teams are rewarded for a traceable process, not only the highest raw metric.

## 8. Decision queue — closed

Tracked as a wayfinder map at [`.scratch/civ2026-challenge-spec/map.md`](.scratch/civ2026-challenge-spec/map.md).
Each decision lives in exactly one place — its ticket. This section gists and links; it never
restates the detail.

> **All 19 tickets are resolved.** Nothing remains to decide before the kit gets built. Building
> it is downstream execution, deliberately outside this map's scope.

### 8.1 The challenge

- ✅ **Dataset** ([01](.scratch/civ2026-challenge-spec/issues/01-dataset-choice.md)) — URT-Kashiwa is the hero dataset and the freeze depends only on it.
- ✅ **Scenario** ([02](.scratch/civ2026-challenge-spec/issues/02-scenario-anchor.md)) — unprotected right turns; creativity lies in *how* teams capture them, not in inventing another event class.
- ✅ **Event definition** ([18](.scratch/civ2026-challenge-spec/issues/18-urt-operational-definition.md)) — sealed labels mark the **right-turn manoeuvre interval**. "Unprotected" is scenario context the brief supplies, not something the detector proves. Accepted cost: detection no longer separates teams on cleverness, so separation comes from interval precision, robustness across all 16 routes, duplicate handling, and the other 75 points.
- ✅ **Scoring basis** ([03](.scratch/civ2026-challenge-spec/issues/03-scoring-basis.md)) — sealed labels for the turn only; other event types are a qualitatively judged bonus.
- ✅ **Duration** ([08](.scratch/civ2026-challenge-spec/issues/08-agenda-duration.md)) — fixed by the programme: **Thu 3 Sep 2026, 09:30–12:30**, plus a **14:30–15:00 results** slot. The three hours produce a submission; the pitch has its own slot after lunch.

### 8.2 The toolchain

- ✅ **Detector surface** ([09](.scratch/civ2026-challenge-spec/issues/09-detector-authoring-surface.md)) — EventSpec carries CEL conditions + `timing` (min duration, merge gap) + `evidence` + a declarative `derive` stage. Rung 1 (CEL + timing + evidence) is the pass mark; rung 2 (`derive`) is the reach. Python and conflict geometry are **deferred** to the organizer demo and an extra track, behind a reserved `detector:` seam.
- ✅ **CLI name** ([13](.scratch/civ2026-challenge-spec/issues/13-cli-name.md)) — **`civ`**.
- ✅ **Viewer** ([10](.scratch/civ2026-challenge-spec/issues/10-visualization-surface.md)) — PlotJuggler 4 required and supported; Lichtblick shipped but optional. Contingent on 17 keeping a camera stream.
- ✅ **Target machine** ([04](.scratch/civ2026-challenge-spec/issues/04-target-machine.md)) — container-first, BYOD only, Windows/WSL2 + Ubuntu, CPU-only. Risk accepted: no hardware swap on setup failure, so the non-ROS fallback pack (§4.7) is load-bearing.
- ✅ **Model policy** ([11](.scratch/civ2026-challenge-spec/issues/11-model-policy.md)) — no model shipped. Teams may bring their own; the required path needs none.
- ✅ **Agent scoring** ([12](.scratch/civ2026-challenge-spec/issues/12-agent-scoring.md)) — bonus up to 10 points, judged on a trace pointing to executed tools and evidence. Said plainly: with rung 3 deferred and no model shipped, the agent track is thin this edition — the AI story is carried by how the kit is built.

### 8.3 Data, rights and evaluation

- ✅ **Data rights** ([05](.scratch/civ2026-challenge-spec/issues/05-kashiwa-redistribution-rights.md)) — CC BY 4.0 from Tsukada Laboratory, University of Tokyo. Subsets and permanent offline attendee copies expressly permitted; attribution is the only condition. A delete-after-the-event clause would itself breach the licence. Take a pinned local copy of the 16 MCAPs with checksums.
- ✅ **Camera imagery** ([19](.scratch/civ2026-challenge-spec/issues/19-personal-data-clearance.md)) — cleared; T-Lab participates in the hackathon.
- ✅ **Subsetting and distribution** ([17](.scratch/civ2026-challenge-spec/issues/17-dataset-subsetting-and-distribution.md)) — 1 warm-up + 7 development routes distributed, 8 sealed. Drop point clouds and the map, keep scalars at full rate, keep camera downscaled and rate-limited. Target 15 GB, pre-event download with checksums, USB fallback. **Needs a per-topic byte measurement to confirm.**
- ✅ **Evaluator calibration** ([16](.scratch/civ2026-challenge-spec/issues/16-evaluator-calibration.md)) — temporal IoU >= 0.5, one-to-one best match, F1 across routes; extra overlapping predictions are false positives, which is what gives `merge_gap` teeth. Gaps excluded from both sets; deliberate quality defects scored under Quality, not Detection. Validated by ranking four deliberately different detectors. All values provisional until that run — there is no historical calibration data.

### 8.4 Process

- ✅ **Clean-room boundary** ([07](.scratch/civ2026-challenge-spec/issues/07-clean-room-boundary.md)) — independent functional reimplementation with provenance review, drawn around the Heex stack and its terminology, not the domain logic. Gate before the freeze: zero hits when grepping the kit, docs and site for the excluded vocabulary.
- ✅ **AI build gates** ([15](.scratch/civ2026-challenge-spec/issues/15-ai-build-review-gates.md)) — gate by failure visibility x cost. The evaluator gets golden files, a determinism check, the rank test and line-by-line review; the runner gets behavioural tests and actionable errors; clips get structural assertions. Nothing ships without a test that fails when it breaks; a human writes the Tier A assertions; a component missing its gate is cut rather than slipped.
- ✅ **French-city bags** ([14](.scratch/civ2026-challenge-spec/issues/14-bespoke-collection-scope.md)) — out of the main track. Inspection showed a ZED + GNSS rig with no Autoware stack and no vehicle bus, one continuous 38-minute drive, unlabelled; a Kashiwa detector cannot run on it at all. Excellent "port your logic to a different sensor stack" material for the extra track.
- ✅ **Previous solution** ([06](.scratch/civ2026-challenge-spec/issues/06-retrieve-previous-solution.md)) — reviewed. Logic, thresholds and workflow extracted; the stack and its terminology left behind.

## 9. Immediate next actions

All decisions are closed (§8). What follows is execution, in dependency order.

1. **Measure per-topic bytes on one bag** and confirm the subset lands under target. Everything about distribution, the container and the viewer choice rests on this number, and it is the one figure in §8 that is still assumed rather than observed.
2. **Take a pinned local copy of the 16 source MCAPs** with checksums and a retrieval date. Rights are permanent; access is not.
3. **Assign one owner each** for data, runner/contracts, evaluation, attendee experience, and release engineering.
4. **Run the one-bag vertical slice** end to end — inspect, sample, EventSpec with `timing`, detect, clip, score, report — offline on the minimum machine, before building slides, dashboards or agents.
5. **Write the URT reference detector** at rung 1 and confirm a mixed-skill team could have written it inside the Formalize block. Ticket 06 has reusable starting thresholds.
6. **Label the sealed set**, then run the four-detector calibration (§8.3) and check the ranking holds before trusting any score.
7. **Rebuild the run of show** around the real slots: 09:30–12:30 produces a submission, 14:30–15:00 presents it. §4.2's 15-minute Transfer block inside the three hours is now the wrong shape.
8. **Schedule the internal mini-hackathon** as the release gate — it is the only place the evaluator gets validated against real behaviour.

> **The slot, verified.** CIV 2026 runs **31 August – 4 September 2026 in Miyazaki, Japan**. The
> hackathon is **Thursday 3 September, 09:30–12:30**, with a separate **14:30–15:00 results**
> block. Read these as design inputs: the three hours produce a submission, and the pitch has its
> own slot after a two-hour lunch in which teams can prepare it.
>
> **Where the substance now sits.** Data, rights, scenario and toolchain are settled. What remains
> is definition made concrete, evaluation made defensible, and the whole path proven end to end.
> These reward care rather than volume of code.

## 10. Source precedence and traceability

This handoff synthesizes:

1. `exploration/data-hackathon-01-brainstorming.md` — initial goals and inheritance from CIV 2025;
2. `exploration/data-hackathon-02-survey-and-directions.md` — expanded format, architecture, evaluation, and preparation workstreams;
3. `exploration/open-source-landscape-research.md` — tool and licence landscape;
4. `exploration/side-chat-explorations/handoff-recommended-hackathon-shape.md` — latest rule ladder, three-hour schedule, and evidence-centred deliverable;
5. `exploration/side-chat-explorations/handoff-early-vertical-slice.md` — latest ownership boundary and organizer-first vertical slice;
6. `exploration/side-chat-explorations/handoff-agent-skills-for-hackathon.md` — latest reference flow through PlotJuggler/Lichtblick, Polars, derived features, CEL, evidence clips, and scoring;
7. `exploration/exploration-notes-INBOX.md` — clean implementation intent, AI-as-enabler framing, deployment modes, and PlotJuggler 4 direction.

