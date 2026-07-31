# CIV 2026 Data Hackathon — planning and experience handoff

> **Status:** internal working baseline for organizers and attendee-perspective review.  
> **Decision rule used:** the initial brainstorming establishes the intent; the documents in `exploration/side-chat-explorations/` refine and, where they conflict, override the earlier implementation shape.  
> **Working title:** **Data Detective — from raw bag to defensible proof**.

## 1. Executive decision

CIV 2026 should be a **three-hour data investigation for 30 experienced practitioners, working
solo or in duos**. The Kashiwa recordings teach the prepared path; the French recording tests
whether participants understood the manoeuvre well enough to transfer it across handedness,
topics and sensor stacks. Every entry ends as compact evidence, a reproducible submission and a
one-page argument—not a live pitch from every participant.

The organizer provides the execution system. Participants provide the valuable reasoning:

- which signals and fields matter on each sensor stack;
- which transformations, comparisons and temporal conditions identify the physical event;
- how duplicate detections and evidence windows are handled;
- what transfers between Kashiwa and France, and what must change;
- which topics belong in the extracted clip;
- what the evidence supports, where the detector fails, and what action should follow.

The attendee journey is:

```text
observe → formalize → scale → transfer → challenge → submit → explain
```

The prepared technical journey is:

```text
Kashiwa MCAP → PlotJuggler → selected signals → EventSpec/CEL → evidence
                                             │
                                             └─ transfer the reasoning
French ZED/GNSS → derived yaw + speed → same event/clip/report contracts
```

The event is **not** an infrastructure-building contest. Participants do not implement MCAP
parsing, ROS message discovery, time synchronization, batch scheduling, provenance, clip
generation or sealed-label scoring. The required path is deterministic and offline; the extension
track may add outside resources or custom computation through named seams.

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
- **Deterministic core, optional agent:** everyone can finish without a model; advanced entries may add a bounded, traceable agent.
- **Progressive disclosure:** one sample bag and one condition before multimodal and temporal logic.
- **Quality over event count:** false positives, missed events, missing data, duplicates, and unstable thresholds matter.
- **One prepared golden path:** attendee time is spent on reasoning, not ROS/container plumbing.
- **Open contracts:** MCAP, EventSpec/JSON Schema, JSONL, run manifests, and portable reports are the stable seams.
- **Clean implementation boundary:** replace observable workflow capabilities. The line runs around the **Heex stack and its terminology** — never *System, Datasource, Signal, Trigger, Recording*; always *bag, topic, field, EventSpec, detector, event, clip, manifest*. It does **not** run around the domain logic: condition expressions and their thresholds describe this vehicle in this dataset and are reusable. Settled in [ticket 07](.scratch/civ2026-challenge-spec/issues/07-clean-room-boundary.md).

### 3.4 Strategic success criteria

The event is strategically successful if:

- at least 80% of entries complete both dataset runs and a valid submission;
- every one-page report shows evidence, one failure or ambiguity, and what transferred;
- a fresh laptop can run the required path offline;
- the same submission produces stable results on rerun;
- all 15–30 submissions can be scored during lunch without manual evaluator repair;
- attendees can name a realistic downstream action and deployment mode;
- agent use, when present, points to executed tools and evidence rather than unsupported claims.

### 3.5 Non-goals

- rebuilding a full fleet-data platform;
- teaching ROS installation or container debugging;
- requiring a dashboard, a GPU, a paid model, or an API key;
- grading prompt style;
- asking every participant to invent an advanced anomaly detector;
- deploying real edge/OTA infrastructure during the session.

## 4. Tactical planning

### 4.1 Challenge shape

Use one coherent challenge with a real transfer test:

- **Kashiwa warm-up:** manually inspect the hero dataset, then express the turn interval as an
  executable EventSpec and scale it across its development routes.
- **French transfer challenge:** adapt the reasoning to a ZED + GNSS recording in right-hand
  traffic. The target manoeuvre is a **left** turn that crosses oncoming traffic; yaw, speed and
  object context come from different topics and schemas.
- **Extension track:** extend either the inputs or the computation. The concrete input exemplar is
  a participant-sourced Reims cave list through `resources:` and `min_distance_to`; the computation
  exemplar remains the reserved Python/conflict-geometry seam. Judged qualitatively.

Kashiwa remains the hero dataset and carries the full learning arc. France carries the harder
question: did the participant understand the event, or copy a threshold?

### 4.2 Three-hour run of show

This is the **rehearsal baseline**, not an immutable minute plan; Phase 5 may move any beat.
Resolved as [ticket 03](.scratch/civ2026-attendee-experience/issues/03-cadence.md) of the
attendee-experience map. The stage order and the 12:30 deadline do not move.

The room is paced by **one progressive attendee page**, not by a facilitator. It shows what was
expected at each stage, then hints, tips and — once a stage's points are settled — its solution.
Nothing is delivered live except a five-minute opening briefing.

| Time | | Attendee activity | `BY NOW YOU SHOULD HAVE` / `IF YOU DON'T` | Page unlocks |
|---|---|---|---|---|
| 09:30 | | **Briefing** — organizational, five minutes | where things are; what to do if lost; the page exists and waiting for a hint is legitimate | — |
| 09:35 | | **Observe (analogue)** — pen on a printed signal trace | one candidate interval, marked by hand | — |
| 09:45 | | **Compare** with a neighbour | you disagree — and that is why labels are intervals, why matching needs a tolerance, and why a sealed set exists | — |
| 09:50 | | **Gate** | card down: `civ doctor && civ inspect` passed **and the page opens**. Still up → recovery | — |
| 10:00 | B1 | **Formalize** | a first `civ detect` on the warm-up route / run the shipped example unchanged | Formalize expectation + hints |
| 10:20 | B2 | Formalize | a condition that fires at all — even a bad one / loosen until it fires, then tighten | Formalize tips |
| 10:40 | B3 | **Scale** | events across more than one route, and one failure you can name / run one route and move on. **Write report headings 1–2 now** | Scale hints + tips |
| 11:00 | B4 | **Transfer** | a Kashiwa detector you are willing to stop improving, submitted once / stop improving it anyway. Submit what you have and open the French data — **the transfer hints are open now**, and a coach will work through it with you | Transfer expectation **+ hints, pulled forward** |
| 11:25 | B5 | Transfer | the French signals identified, and a condition that fires / the equivalents are in the hints. The manoeuvre is yours | Transfer hints |
| 11:45 | B6 | **Challenge** | French events, however imperfect / take what you have. **Write headings 3–4 now**, while the transfer is fresh | Transfer tips |
| 12:10 | B7 | **Submit** | a submission already accepted — and be improving it / submit an incomplete one now, you can submit again. **Write heading 5** | — |
| 12:30 | | **Close** | hard cutoff | — (solutions publish after the event) |

Three properties of this cadence are load-bearing and should not be quietly dropped:

- **`IF YOU DON'T` is always a permission to do less.** A beat that only asserts tells a stuck
  person they are stuck, which they already know.
- **The cliff at 11:00 is carried without an answer.** Three things arrive together: the permission
  stated plainly, the **transfer hints pulled forward** to that beat, and a coach. Nothing hands over
  a threshold, which is what keeps Detection discriminating on both datasets.
- **The report is written in three instalments**, at the beats where each heading is freshest. That
  is a 30-minute report budget rather than 15, and it makes Submit *finish and check* rather than
  *write*.

The separate results block is fixed:

| When | What |
|---|---|
| 12:30 | Submissions close; unattended machine scoring starts. |
| 12:30–14:30 | Jury splits the capped reports and awards judgement-based points. |
| 14:30–14:40 | Leaderboard reveal and explanation of what the scores showed. |
| 14:40–14:55 | Roughly four selected walkthroughs, including the most instructive failure. |
| 14:55–15:00 | Wrap on the transfer lesson. |

### 4.3 Participant brief

> A fleet recorded several passages through a shared environment. A risky or operationally
> significant behaviour was reported, but the report is incomplete. Locate relevant occurrences,
> encode a reusable detector, transfer the reasoning to a structurally different recording,
> extract compact evidence, evaluate the limits, and recommend what should happen next.

### 4.4 Participant deliverable

Each solo or duo entry submits:

1. the engineering question and detection hypothesis;
2. the signals used, missing, or judged unreliable;
3. an executable EventSpec or detector;
4. normalized `events.jsonl` and compact MCAP evidence clips;
5. a run manifest and metrics;
6. one synchronized evidence view;
7. one false positive, false negative, or ambiguity and the resulting change;
8. a one-command reproduction path;
9. a **one-page `report.md`** with fixed headings: question, signals, what transferred, one failure,
   and downstream action;
10. optional agent or extension artifact with provenance.

### 4.5 Ownership boundary

| Participants own | Organizers provide |
|---|---|
| Signal and field selection on both stacks | MCAP/ROS decoding and schema availability |
| Preprocessing and derived features | Topic/field inventory and sampling utilities |
| Thresholds and CEL logic | Deterministic detector runner |
| Boolean and temporal composition | Batch iteration and time synchronization |
| Debounce/deduplication parameters | Clip extraction and standardized output |
| Evidence-window duration and retained topics | Hashes, provenance and run manifest |
| Transfer reasoning and interpretation | Sealed labels and scoring infrastructure |
| Failure analysis and operational recommendation | Tested visualization layouts and offline bundle |

### 4.6 Evaluation

The common score remains 100 points; 55 are machine-scored at 12:30 and 45 are jury-scored from
the capped report over lunch.

| Category | Points | Method |
|---|---:|---|
| Detection — Kashiwa | 15 | Sealed temporal matching |
| Detection — French transfer | 10 | Sealed temporal matching |
| Evidence and extraction | 15 | Machine checks from the run manifest: topics retained, volume reduction, self-attested clip validity |
| Reproducibility | 15 | Machine checks: one command, pinned inputs, stable rerun |
| Investigation and hypothesis | 15 | Jury reads `report.md` |
| Quality and evaluation | 15 | Jury reads the failure analysis |
| Visualization and explanation | 15 | Jury reads the evidence and claims |

The 15/10 Detection split is **provisional until the internal two-dataset ranking test**. Tune it
if either set dominates ranking or adds excessive noise; do not change the 25-point total.

Optional bonus remains up to 20 points: bounded agent trace (10), advanced multimodal/data-quality
method (5), and regression test from a discovered failure (5). Bonus cannot rescue an
irreproducible core.

### 4.7 Facilitation mechanics

Resolved across the [attendee-experience map](.scratch/civ2026-attendee-experience/map.md). This
section replaces the earlier reactive sketch: the room is paced **proactively**, and coaching is the
exception handler rather than the mechanism.

**Why the inversion.** The binding constraint is not skill and not blockage — it is **budget
awareness**. Every participant can do this work; what they cannot do is do it in 180 minutes without
knowing the budget. Someone who spends 70 minutes perfecting a Kashiwa detector has done excellent
work and failed the event, and that failure is invisible from outside: not blocked, just absorbed
down a defensible branch. Broadcast tempo is the only mechanism whose cost does not grow with the
cohort, because it moves the noticing to the participant.

**Tempo.** One progressive attendee page (§4.2), served from an organizer machine over **both**
Tailscale Funnel — enabled on the morning only, so nothing leaks early. If the internet dies, the
static export on the SSDs is already in the room. Submission goes through a form; there is no room
LAN and no organizer machine.
It advances automatically and **any coach may advance
it early; nobody may hold it back**. **Solutions are handed over only after the event**: during the
session the ladder stops at hints and tips, and the pace car and coaches guide *towards* an answer
without giving one. No material ever resolves handedness. No live teaching: it
penalises deep work, since the people most likely to miss it are the ones head-down doing what the
event wants.

**Help.** A two-sided card on the laptop. Side A is environment and routes to recovery; side B is
approach and routes to a coach. It needs no network, and the side showing triages the request before
anyone arrives. **Coaches guide towards a solution and never hand one over** — no thresholds, no
specs, not even at the cliff. A coach who wants to give the room more advances the page, which
delivers the next hints and tips to everyone at once. Help is never private and never improvised.

**Coaches.** Three minimum, four preferred — a floor, not a ratio. They sweep the room once per beat,
glancing rather than interrupting, and otherwise answer cards. Before anything else they ask *what
have you got* and *what do you think is happening*, then answer the hypothesis rather than the code.
They log who they spent real time with, so the jury can route around conflicts. **They do not rescue
people from the designed friction:** the warm-up's tedium is the lesson.

**Opening.** A five-minute organizational briefing, then a deliberately **analogue** block — pen on a
printed signal trace — so a broken laptop costs time but not the lesson. Its output is *disagreement*
between neighbours, which is what makes intervals, tolerance and sealed labels concrete. The
environment gate runs underneath it: everyone starts with the card up and puts it down when
`civ doctor && civ inspect` passes and the page opens, so recovery starts at minute ten without anyone announcing
anything.

**Recovery.** **Pair up.** A broken container and an underpowered laptop have the same answer, and
solo and duo already rank together, so a paired participant has a complete entry rather than a
degraded one. Offer it aloud in the briefing — nobody volunteers *my laptop is too weak* to a room of
peers. The fallback pack on the SSDs supports reasoning meanwhile. No organizer runner, no room LAN,
no standby machine: all three were designed and cut once pairing was shown to cover the case.

**Intake.** **Metadata only — no evidence data is collected.** A submission is the EventSpec,
`events.jsonl`, an extended run manifest and the one-page report: kilobytes, sent through a simple
form, with a local/USB fallback. The manifest carries what the clips used to prove — topics
retained, window durations, input versus output bytes, hashes — so *correct topics* and *volume
reduction* stay machine-checkable while *clip validity* weakens to self-attested, offset by every
spec being re-runnable on the sealed data. **Unlimited resubmission** is unchanged and load-bearing;
two beats depend on it. `civ` validates structure **before** submission rather than at intake, so a
missing manifest fails at 11:00 rather than 12:29. Participants keep their own evidence.

**Materials.** Three things on the desk — printed trace, help card, one-page brief. Everything else
is on the page. No cheat sheet and no pace card: a sheet that duplicates a screen is what people hunt
for at minute 95.

**Extension.** The *lesson* closes the event at 14:55. The *exercise* is a page section unlocked
in-session as an optional branch and **scored** under the existing bonus, remaining available
afterwards. The run of show allocates it no time and says so, or it becomes a trap.

**Judging and the afternoon.** One organizer, two AI agents against human-written anchors, and a
T-Lab owner if confirmed; the agents read each report **against the submission**, which no human jury
could do in the time. Disagreement between the two routes to the human. Walkthroughs are **narrated by the organizer** from the
submitted spec, report and figure — nobody presents or is interviewed; the participant stays seated
and receives applause. Picks are known by ~13:15, and the instructive-failure entry is told
beforehand rather than shown unannounced. **Every participant receives written feedback**,
which is what finally makes "every submission is genuinely assessed" true in their hands.

## 5. Operational planning

### Phase 0 — lock the challenge contract

Closed: scenario, programme slots, 30-person solo/duo cohort, experienced skill floor, target
machine, data rights, public/permissive outbound licensing, agent scoring and the inbound tool
licence posture are all decided.

**Gate:** achieved when this revised one-page contract is approved.

### Phase 1 — prove the organizer vertical slice

Complete the required path first on one Kashiwa bag, then prove the transfer seam on one French
chunk:

```text
inspect → PlotJuggler → EventSpec → batch → events.jsonl → clip → score → report
                                      ↓
                     remap signals and handedness to the French stack
```

Measure runtime, RAM, disk use, bundle size and offline behaviour.

**Gate:** both stacks complete on the minimum supported machine without Internet.

### Phase 2 — freeze interfaces and golden path

- version EventSpec, event-output and run-manifest schemas;
- implement `doctor`, `inspect`, `sample`, `detect`, `clip`, `score`, and `report`;
- freeze CEL + `timing` + `evidence` + declarative `derive`;
- add the external-resource seam (`resources:` and `min_distance_to`) before schema freeze;
- keep `detector:` reserved for the deferred Python/conflict-geometry extension;
- pin schema-matching custom messages by repository commit and MCAP schema hash;
- test `cel-python` 0.5.0 as the initial runtime candidate against every scoring operator/type;
- prepare reference detectors, layouts and a one-page quickstart.

**Gate:** a new user gets from unpacking the kit to a first clip in under 20 minutes, and the same
contracts run against both sensor stacks.

### Phase 3 — build data and evaluation

- Kashiwa: distribute 1 warm-up + 7 development routes; keep 8 routes sealed;
- French: distribute signals-only chunks `_0`–`_4` (~21m49s, 7 clear left turns plus 2 borderline
  teaching cases); keep `_5`–`_8` sealed (~16m09s, 9 clear left turns);
- publish manifests with sizes, durations, topics, hashes, provenance and licences;
- turn the planning-grade French intervals into reviewed ground truth;
- apply temporal IoU ≥ 0.5, one-to-one best matching and F1 on both datasets;
- run the deliberate-detector ranking test across both sealed sets and validate the 15/10 split;
- verify 15–30 submissions score unattended within the lunch window;
- ensure evidence clips and development output do not leak hidden labels.

**Gate:** scoring separates plausible solutions across both stacks without one magic threshold or
manual evaluator repair.

### Phase 4 — package the attendee experience

- pin and smoke-test the exact PlotJuggler 3.999.3 “PlotJuggler 4: beta2” asset;
- ship Lichtblick only if its exact artifact is pinned, audited and still earns its image-size cost;
- prepare Kashiwa and French layouts, warm-up, brief, cheat sheet, submission template and fixed
  one-page report template;
- create organizer solution, jury rubric, coach guide, troubleshooting tree and checkpoints;
- package the two-example extension track only after the deterministic path is stable;
- build offline caches and a two-stack non-ROS fallback pack;
- publish only the participant app; keep the organizer site in local development.

**Gate:** all participant instructions fit behind one public start page and one command path; the
public server and client artifacts contain no organizer route or organizer-only text.

### Phase 5 — rehearse and release-candidate

- fresh-install on Windows/WSL2 and Ubuntu; disconnect the Internet and rerun;
- rehearse with solo and duo personas from the actual skill floor;
- simulate 15–30 submissions, concurrent intake, lunch scoring and report division;
- run the two-dataset evaluator ranking test and tune the 15/10 split only if evidence requires it;
- freeze the ROS 2 Humble / Ubuntu 22.04 base by multi-arch digest;
- freeze every apt package, Python wheel, CLI, viewer asset and custom-schema commit/hash;
- generate an image-level SBOM and `THIRD_PARTY_NOTICES.md`;
- preserve Debian copyright files, archive exact MPL viewer source, and review every unknown,
  GPL/LGPL and relinking/source finding against the built image;
- verify CC BY data/content attribution separately and prepare recovery media.

**Gate:** a two-hour internal mini-hackathon completes with no organizer-only workaround, and the
built image passes both the behavioural release gates and the licence/source-notice audit.

## 6. Required kit and readiness definition

### Data

- authorized Kashiwa MCAP source with a mirrored, checksummed copy;
- Kashiwa warm-up/dev/sealed split: 1 + 7 + 8 routes;
- French ZED/GNSS split: chunks `_0`–`_4` development, `_5`–`_8` sealed;
- signals at full rate; point clouds and map removed; camera retained only at the evidence rate and
  resolution justified by the tested layouts;
- dataset manifests, checksums, provenance, CC BY attribution and modification records;
- partial development annotations, sealed interval labels and documented quality defects;
- pre-event download plus **four 2 TB high-speed SSDs**, each a complete event-in-a-box: container
  image, both datasets, the optional image context pack, the static attendee-page export and the
  fallback pack. exFAT, USB-C and USB-A adapters, checksum-verified before travel, circulating from
  the moment people arrive rather than held for failures
  ([ticket 07](.scratch/civ2026-attendee-experience/issues/07-pre-event-readiness-and-reveal.md)).
  The image, not the data, is the payload that matters — nobody downloads a ROS 2 image in the room.
  French detector signals measure ~350 MB for the full
  38-minute session; Kashiwa still needs the same per-topic byte measurement.

### Code, API, and contracts

- versioned EventSpec with CEL conditions, `timing`, `evidence`, declarative `derive`, `resources:`
  and `min_distance_to`;
- reserved `detector:` seam for the extension computation path;
- stable event record schema and run manifest;
- deterministic two-stack batch engine;
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

Publish the `civ` CLI with the workshop kit under MIT and/or Apache-2.0. Frame it as a forkable
gift, not a contribution programme: no roadmap, issue-triage or PR-review promise. Distribute a
prebuilt, versioned image and checksums; no compile or package download on event day.

### Dependencies, views and licences

- ROS 2 Humble / Ubuntu 22.04 from a digest-pinned `ros:humble-ros-base-jammy`-derived image;
- PlotJuggler 3.999.3 “PlotJuggler 4: beta2” required, invoked as a standalone MPL-2.0 program;
- Lichtblick optional and MPL-2.0; ship only an exact pinned, tested and audited asset;
- MCAP CLI, `mcap`, `mcap-ros2-support`, Polars and the chosen CEL runtime independently pinned
  with hashes;
- `cel-python` 0.5.0 is the initial Apache-2.0 candidate, gated by deterministic conformance tests;
- custom message schemas pinned by repository commit plus embedded MCAP schema hash; compiled
  packages included only if schema-driven decoding is insufficient;
- CPU-only baseline; GPU/model path strictly optional;
- machine-readable SBOM plus human-readable notices/source index from the built image.

The image is a mixed-licence aggregate: CIV code stays MIT/Apache, the viewers remain MPL, base
packages keep their individual terms, and data/content remain CC BY 4.0. Do not label the whole
container with one outbound licence.

### Submission structure

The participant's working directory holds everything, including the evidence clips. **What is
*submitted* is metadata only** — see
[attendee-experience ticket 09](.scratch/civ2026-attendee-experience/issues/09-submission-intake.md).
Clips stay with the participant.

```text
working/                          submitted?
├── detector/                     ✅  EventSpec and optional extension code
├── events.jsonl                  ✅  normalized detections — intervals, not data
├── run-manifest.json             ✅  versions, hashes, parameters, timings, and
│                                     per-clip topics / durations / bytes-in-vs-out /
│                                     `civ clip` validity result
├── metrics.json                  ✅
├── report.md                     ✅  one page, five headings, **one required figure**
├── extension/                    ✅  optional resources, provenance, agent/tool trace
├── reproduce.ps1|sh              ✅  one-command entry point
└── evidence/                     ❌  compact MCAP clips — kept locally, never uploaded
```

`civ` validates this structure **before** submission and refuses to emit a submission blob that is
incomplete, so a missing manifest fails at 11:00 rather than 12:29.

The fixed report headings are: question and hypothesis; signals used/missing; what transferred and
what did not; one failure and the resulting change; downstream action and deployment mode. The
figure is required because no clip reaches the jury.

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
Each decision lives in exactly one ticket; this section gists and links it.

> **The challenge spec is closed; the attendee experience is not.** A second map,
> [`.scratch/civ2026-attendee-experience/map.md`](.scratch/civ2026-attendee-experience/map.md),
> charts the room: tempo, coaching, recovery, cadence, extension placement, the jury and the
> afternoon. §4.2 and §4.7 above are its inputs, and both will be rewritten from it. It may not
> reopen anything in this section.

> **All 25 tickets are resolved.** The specification is complete. Build, labelling, artifact
> pinning, evaluator validation, rehearsal and licence compliance are downstream execution gates,
> not open design questions.

### 8.1 The challenge and room

- ✅ **Dataset** ([01](.scratch/civ2026-challenge-spec/issues/01-dataset-choice.md)) — Kashiwa is
  the hero dataset; France is the scored transfer test.
- ✅ **Scenario** ([02](.scratch/civ2026-challenge-spec/issues/02-scenario-anchor.md)) — the event
  is the turn that crosses oncoming traffic.
- ✅ **Event definition** ([18](.scratch/civ2026-challenge-spec/issues/18-urt-operational-definition.md))
  — right turns in Kashiwa, left turns in France; sealed labels mark manoeuvre intervals, not
  inferred right-of-way.
- ✅ **Scoring basis** ([03](.scratch/civ2026-challenge-spec/issues/03-scoring-basis.md)) — sealed
  labels score the target turn; other event types are qualitative bonus work.
- ✅ **Programme** ([08](.scratch/civ2026-challenge-spec/issues/08-agenda-duration.md)) — Thu 3 Sep,
  09:30–12:30, with results 14:30–15:00 after lunch.
- ✅ **Cohort and publication** ([20](.scratch/civ2026-challenge-spec/issues/20-cohort-skill-floor-licensing.md))
  — 30 experienced practitioners, solo or in duos; CLI and content published permissively.
- ✅ **Judging** ([21](.scratch/civ2026-challenge-spec/issues/21-pitch-and-judging-model.md)) — 55
  machine points at 12:30, 45 report points over lunch, then a reveal and ~4 walkthroughs. Detection
  starts at 15 Kashiwa / 10 French, provisional until internal evaluation.

### 8.2 The toolchain and extension seams

- ✅ **Detector surface** ([09](.scratch/civ2026-challenge-spec/issues/09-detector-authoring-surface.md))
  — CEL + `timing` + `evidence` is the pass mark; declarative `derive` is the reach; `detector:` is
  reserved for Python/conflict geometry.
- ✅ **CLI name** ([13](.scratch/civ2026-challenge-spec/issues/13-cli-name.md)) — **`civ`**.
- ✅ **Viewer** ([10](.scratch/civ2026-challenge-spec/issues/10-visualization-surface.md)) —
  PlotJuggler required; Lichtblick optional.
- ✅ **Target machine** ([04](.scratch/civ2026-challenge-spec/issues/04-target-machine.md)) —
  container-first BYOD, Windows/WSL2 + Ubuntu, CPU-only; fallback pack is load-bearing.
- ✅ **Model policy** ([11](.scratch/civ2026-challenge-spec/issues/11-model-policy.md)) — no model
  shipped; participant-supplied models remain optional.
- ✅ **Agent scoring** ([12](.scratch/civ2026-challenge-spec/issues/12-agent-scoring.md)) — up to 10
  bonus points for a trace tied to executed tools and evidence.
- ✅ **Extension track** ([25](.scratch/civ2026-challenge-spec/issues/25-geofence-agent-track.md)) —
  participant-sourced cave zones plug in through `resources:` + `min_distance_to`; 40 m yields two
  clear Reims encounters. Method is unconstrained and judged qualitatively.
- ✅ **Tool licences** ([23](.scratch/civ2026-challenge-spec/issues/23-tool-licence-audit.md)) — named
  licences compose, but the built image needs exact pins, SBOM/notices and MPL/GPL/LGPL
  source/relink review. Standardize on ROS 2 Humble / Ubuntu 22.04; the aggregate has no one licence.

### 8.3 Data, rights and evaluation

- ✅ **Kashiwa rights** ([05](.scratch/civ2026-challenge-spec/issues/05-kashiwa-redistribution-rights.md))
  — CC BY 4.0, permanent offline copies allowed; mirror the 16 MCAPs with checksums.
- ✅ **Camera imagery** ([19](.scratch/civ2026-challenge-spec/issues/19-personal-data-clearance.md))
  — cleared through T-Lab’s participation.
- ✅ **Kashiwa distribution** ([17](.scratch/civ2026-challenge-spec/issues/17-dataset-subsetting-and-distribution.md))
  — 1 warm-up + 7 dev + 8 sealed; drop point clouds/map, retain full-rate detector signals and a
  tested evidence camera stream. Kashiwa per-topic bytes still need measuring.
- ✅ **French survey** ([24](.scratch/civ2026-challenge-spec/issues/24-survey-french-bag.md)) — 16
  clear left turns; `_0`–`_4` dev and `_5`–`_8` sealed. Detector signals are ~350 MB for the full
  session; Reims GNSS supports two 40 m cave zones.
- ✅ **Evaluator semantics** ([16](.scratch/civ2026-challenge-spec/issues/16-evaluator-calibration.md))
  — temporal IoU ≥ 0.5, one-to-one best match and F1; extra overlaps are false positives; validate
  ranking across deliberate detectors and both sealed sets.

### 8.4 Process and publication boundary

- ✅ **Clean-room boundary** ([07](.scratch/civ2026-challenge-spec/issues/07-clean-room-boundary.md))
  — independent functional reimplementation around the prior stack and vocabulary, not the domain
  logic; provenance and excluded-term review gate the freeze.
- ✅ **AI build gates** ([15](.scratch/civ2026-challenge-spec/issues/15-ai-build-review-gates.md))
  — failure visibility × cost; human-authored Tier A assertions; cut any component missing its gate.
- ✅ **French role reversal** ([14](.scratch/civ2026-challenge-spec/issues/14-bespoke-collection-scope.md))
  — French data is in the main track as the scored generalisation test.
- ✅ **Previous solution** ([06](.scratch/civ2026-challenge-spec/issues/06-retrieve-previous-solution.md))
  — reusable logic extracted; prior stack and terminology left behind.
- ✅ **Public organizer gate** ([22](.scratch/civ2026-challenge-spec/issues/22-public-site-organizer-gate.md))
  — production builds contain only `/` and `/participants`; `/organizers` and its content are
  absent from server and client artifacts and remain local-development only.

## 9. Immediate next actions

The **challenge** decisions are closed and execution proceeds in dependency order. The **attendee
experience** — the room, the tempo, the support and the afternoon — is charted separately and is
still open; item 10 below tracks it.

1. **Mirror the 16 Kashiwa source MCAPs** with checksums and retrieval date.
2. **Assign owners** for data, runner/contracts, evaluation, attendee/jury experience and release
   engineering/licence compliance.
3. **Freeze the dependency candidates:** Humble base digest, exact PlotJuggler asset, optional
   Lichtblick decision, MCAP/Polars/CEL hashes and schema-matching custom-message commits.
4. **Run the two-stack vertical slice** offline on the minimum machine before slides, dashboards
   or extension work.
5. **Cut the real subsets:** measure Kashiwa per-topic bytes; produce Kashiwa 1+7+8 and French
   five-chunk/four-chunk packages with manifests and CC BY records.
6. **Finish sealed labels** for Kashiwa and turn the 16 French planning intervals into reviewed
   ground truth.
7. **Run the deliberate-detector evaluator test across both sealed sets** and tune 15/10 only if
   ranking evidence requires it.
8. **Prove intake and judging throughput** on 15–30 submissions, including one-page report division
   and the four-walkthrough results block.
9. **Generate the SBOM/notices/source bundle from the built image**, review unknown and copyleft
   findings, and archive exact MPL viewer source.
10. **Work the attendee-experience map** at
    [`.scratch/civ2026-attendee-experience/map.md`](.scratch/civ2026-attendee-experience/map.md).
    **17 of 18 tickets are resolved and §4.2 and §4.7 above are rewritten from it.** One item
    remains: [ticket 16](.scratch/civ2026-attendee-experience/issues/16-decoy-event-class.md) needs a
    twenty-minute check against the Kashiwa warm-up route on a machine holding the bags. The map's
    exit condition is [ticket 18](.scratch/civ2026-attendee-experience/issues/18-rehearsal-observations.md),
    six things the Phase 5 rehearsal must observe.
11. **Run the internal mini-hackathon** with solo and duo personas; release only when behavioural,
    throughput, offline and licence gates all pass.

> **The slot, verified.** CIV 2026 runs **31 August – 4 September 2026 in Miyazaki, Japan**. The
> hackathon is **Thursday 3 September, 09:30–12:30**, with results **14:30–15:00**.
>
> **What can still move.** Internal evaluation may tune checkpoint minutes and the 15/10 Detection
> split. It does not reopen the two-dataset arc, the 25-point Detection total, the report-based
> judging model or the release-compliance boundary.

## 10. Source precedence and traceability

This handoff synthesizes, in precedence order from broad context to current decisions:

1. `exploration/data-hackathon-01-brainstorming.md` — initial goals and inheritance from CIV 2025;
2. `exploration/data-hackathon-02-survey-and-directions.md` — architecture, evaluation and preparation workstreams;
3. `exploration/open-source-landscape-research.md` — initial tool and licence landscape;
4. `exploration/side-chat-explorations/handoff-recommended-hackathon-shape.md` — rule ladder and evidence-centred deliverable;
5. `exploration/side-chat-explorations/handoff-early-vertical-slice.md` — ownership boundary and organizer-first slice;
6. `exploration/side-chat-explorations/handoff-agent-skills-for-hackathon.md` — reference flow, derived features, CEL, evidence and scoring;
7. `exploration/exploration-notes-INBOX.md` — clean implementation intent and AI-as-enabler framing;
8. `.scratch/civ2026-challenge-spec/map.md` and its 25 linked tickets — the current decision authority;
9. `.scratch/civ2026-challenge-spec/research/23-tool-licence-audit.md` — primary-source licence and release audit;
10. `.scratch/civ2026-challenge-spec/research/survey_french_bag.py` plus ticket 24 — reproducible French manoeuvre, GNSS and byte evidence.

Where these disagree, the resolved ticket and its measured evidence win.

