/**
 * Organizer-only content — NOT for participants.
 *
 * Holds the teaching goals, evaluation internals, preparation phases and the
 * open decision queue. The `server-only` import makes any client-side import a
 * build error, so this material can never be pulled into a browser bundle by
 * accident. It is still rendered into the /organizers HTML, so route separation
 * is a content boundary, not an access control: gate the route before deploying
 * anywhere participants can reach.
 */
import "server-only";

export type Level = "strategy" | "tactics" | "operations";

export const planning = {
  strategy: {
    eyebrow: "Why this event exists",
    title: "Turn raw robotics logs into reusable engineering knowledge.",
    summary:
      "The north star is not a winning timestamp. It is a compact, defensible and repeatable path from observation to action.",
    steps: [
      ["01", "Lock the mission", "Awareness + capability: attendees experience the complete data workflow and leave with an executable detector."],
      ["02", "Protect the principles", "Evidence-first, local-first, deterministic core, optional agent, open contracts and progressive disclosure."],
      ["03", "Define success", "Teams batch-run, expose one failure, reproduce in one command and name the next operational action."],
      ["04", "Guard the scope", "No platform rebuild, no day-of compilation, no paid key, no mandatory GPU and no infrastructure contest."],
    ],
  },
  tactics: {
    eyebrow: "How the challenge creates learning",
    title: "One ladder: Smart Data warm-up → Data Detective → optional agent.",
    summary:
      "All teams follow the same progression. Advanced methods add ambition without creating three incomparable hackathons.",
    steps: [
      ["01", "Shape the challenge", "Give teams an incomplete incident report and ask for a detector, evidence, limits and an operational response."],
      ["02", "Set the cadence", "Thirty-minute observation, simple rule, temporal context, batch scale, failure review, then transfer pitch."],
      ["03", "Make proof the contract", "Score hypothesis, detection, extraction, quality, visualization and reproducibility—not prompt style."],
      ["04", "Support the room", "Prepared layouts, public checkpoints, hidden labels, coach prompts and a non-ROS fallback pack."],
    ],
  },
  operations: {
    eyebrow: "What must exist before day zero",
    title: "Prove one vertical slice, then freeze and rehearse the kit.",
    summary:
      "Build only what carries the attendee from a bag to a scored evidence package. Everything else waits.",
    steps: [
      ["P0", "Contract", "Scenario, data rights, audience floor, duration, hardware, OSS definition and scoring policy approved."],
      ["P1", "Vertical slice", "One bag completes MCAP → detector → batch → clip → score offline on the minimum laptop."],
      ["P2", "Golden path", "Schemas, CLI, sample, reference detector, pinned runtime and one-page quickstart frozen."],
      ["P3", "Data + score", "Dev/test split, labels, tolerances, quality defects and evaluator calibrated across different detectors."],
      ["P4", "Experience", "Warm-up, layouts, coach guide, submission and fallback pack packaged."],
      ["P5", "Rehearsal", "Fresh install, offline run, concurrent scoring and two-hour internal mini-hackathon passed."],
    ],
  },
} satisfies Record<Level, { eyebrow: string; title: string; summary: string; steps: string[][] }>;

export const successCriteria = [
  "At least 80% of teams complete a batch run and a valid submission",
  "Every final pitch shows one piece of evidence and one failure or ambiguity",
  "A fresh laptop can run the required path offline",
  "The same submission produces stable results on rerun",
  "Attendees can name a realistic downstream action and deployment mode",
  "Agent use, where present, points to executed tools rather than unsupported claims",
];

export const nonGoals = [
  "Rebuilding a full fleet-data platform",
  "Teaching ROS installation or container debugging",
  "Requiring a dashboard, a GPU, a paid model or an API key",
  "Grading prompt style",
  "Asking every team to invent an advanced anomaly detector",
  "Deploying real edge/OTA infrastructure during the session",
];

export const phases: { id: string; title: string; work: string; gate: string }[] = [
  {
    id: "P0",
    title: "Lock the challenge contract",
    work: "Decide scenario, duration, team count, target hardware and OS, data rights, required skill floor, the scoring role of agentic work, and the definition of “open source”.",
    gate: "One-page challenge contract approved.",
  },
  {
    id: "P1",
    title: "Prove the organizer vertical slice",
    work: "On one authorized bag: inspect → PlotJuggler 4 → detector → batch runner → events.jsonl → evidence clip → score → report. Measure runtime, RAM, disk use, bundle size and offline behaviour.",
    gate: "The complete path works on the minimum supported machine without Internet.",
  },
  {
    id: "P2",
    title: "Freeze interfaces and the golden path",
    work: "Version EventSpec and event schemas, implement the seven CLI verbs, decide whether custom Python detectors are supported, embed ROS schemas, prepare a reference detector and quickstart, pin the runtime.",
    gate: "A new user gets from unpacking the kit to a first clip in under 20 minutes.",
  },
  {
    id: "P3",
    title: "Build data and evaluation",
    work: "Prepare sample/dev/hidden test sets, publish a dataset manifest, create partial annotations and sealed ground truth, define tolerance and duplicate policy, calibrate against different detectors, inject educational quality defects.",
    gate: "Scoring separates plausible solutions without requiring one magic threshold.",
  },
  {
    id: "P4",
    title: "Package the attendee experience",
    work: "Preconfigure layouts; prepare warm-up, brief, cheat sheet, submission and pitch templates; write the organizer solution, coach guide, troubleshooting tree and checkpoint prompts; build offline caches and the non-ROS fallback pack.",
    gate: "All attendee-facing instructions fit behind one start page and one command path.",
  },
  {
    id: "P5",
    title: "Rehearse and cut the release candidate",
    work: "Fresh-install on each supported OS, rerun disconnected, rehearse with novice and advanced personas, simulate simultaneous distribution and scoring, time every checkpoint, verify hashes, licences, SBOM and recovery media.",
    gate: "A two-hour internal mini-hackathon completes with no organizer-only workaround.",
  },
];

export const readiness: { name: string; status: string; detail: string }[] = [
  { name: "Data", status: "RIGHTS PENDING", detail: "Hero set and scenario fixed. Still to cut: sample/dev/sealed-test split, hidden truth, laptop-sized subset — and redistribution terms are unconfirmed." },
  { name: "Contracts", status: "DRAFT → FREEZE", detail: "EventSpec + CEL, event JSONL, run manifest, detector interface, time semantics." },
  { name: "Runner", status: "BUILD", detail: "doctor, inspect, sample, detect, clip, score and report; dry-run and actionable errors." },
  { name: "Views", status: "PREPARE", detail: "PlotJuggler 4 primary layouts; Lichtblick only if robotic context is required." },
  { name: "Dependencies", status: "PIN", detail: "One ROS 2 distro, MCAP, Polars, CEL runtime, CPU baseline, image/bundle checksums." },
  { name: "Evaluation", status: "DESIGN EARLY", detail: "Temporal tolerance, duplicates, missing data, volume reduction and proof quality." },
  { name: "Experience", status: "PACKAGE", detail: "Warm-up, start page, coach guide, checkpoints, submission and pitch template." },
  { name: "Resilience", status: "REHEARSE", detail: "Fresh install, no Internet, simultaneous scoring, recovery media and non-ROS fallback." },
];

/** Evaluation mechanics that must stay out of participant-facing material. */
export const evaluationDesign = [
  "Sealed ground truth stays out of every distributed artifact",
  "Development bags carry partial annotations only; ranking runs on hidden test bags",
  "Temporal matching tolerance, duplicate policy and missing-data cases are fixed before the dataset grows",
  "The evaluator is calibrated against several deliberately different detectors",
  "One or two educational quality defects are injected on purpose",
  "Evidence clips are verified not to leak hidden labels",
  "The public development score exposes format and basic metrics — never the sealed result",
];

export const facilitation = [
  "Teams of 3–5 with suggested roles: investigator, detector author, evidence reviewer, pitch owner",
  "Visible checkpoints at 30, 60, 105, 135 and 165 minutes",
  "Coaches ask for evidence and assumptions before ever suggesting a threshold",
  "A short timebox before a coach intervenes on blocked tooling",
  "One shared warm-up so the room starts from the same first success",
  "A non-ROS fallback pack of pre-extracted tables and clips keeps data reasoning alive if execution fails",
];

/** The seven forces the room is engineered around. */
export const drivingForces = [
  { title: "A concrete engineering question", effect: "prevents aimless visualization." },
  { title: "Heterogeneous physical data", effect: "forces translation from behaviour to signals." },
  { title: "Limited time and compute", effect: "rewards reduction, prioritization and prepared tooling." },
  { title: "Partial and hidden truth", effect: "creates a real validation loop instead of answer copying." },
  { title: "Evidence requirements", effect: "prevent unsupported timestamps or AI claims." },
  { title: "Failure visibility", effect: "makes false positives, misses and poor data productive." },
  { title: "Operational transfer", effect: "turns the detector into a decision." },
];

/**
 * Closed decisions, charted 30 July 2026. Detail lives in the wayfinder tickets
 * under `.scratch/civ2026-challenge-spec/`; this only gists them.
 */
export const decisionsMade: { ticket: string; title: string; answer: string; caveat?: string }[] = [
  {
    ticket: "01",
    title: "Dataset",
    answer:
      "URT-Kashiwa is the hero dataset and the freeze depends only on it. French-city bespoke bags are additive-only, behind a hard drop-dead date.",
    caveat: "Assumes redistribution rights that are not yet confirmed — ticket 05.",
  },
  {
    ticket: "02",
    title: "Scenario",
    answer:
      "Unprotected right turns (URT). Teams may catch other event types, but the creativity expected is in how they express and capture the scenario with the OSS toolchain.",
  },
  {
    ticket: "03",
    title: "Scoring basis",
    answer:
      "Sealed labels exist for URT only, so the 25-point detection category stays objective. Other event types are judged qualitatively in the bonus track.",
  },
  {
    ticket: "04",
    title: "Target machine",
    answer:
      "Container-first, BYOD only, Windows/WSL2 + Ubuntu, CPU-only. Also settles native-vs-container bundling.",
    caveat:
      "Risk accepted: no hardware swap when setup fails, so the non-ROS fallback pack is load-bearing.",
  },
  {
    ticket: "05",
    title: "Data rights",
    answer:
      "URT-Kashiwa is published by Tsukada Laboratory, University of Tokyo, under CC BY 4.0. Subsets and permanent offline attendee copies are expressly permitted; attribution is the only condition.",
    caveat:
      "A delete-after-the-event clause would breach the licence. Access is not guaranteed to persist — mirror the 16 MCAPs now. Personal data is a separate, open question (19).",
  },
  {
    ticket: "06",
    title: "Previous solution",
    answer:
      "Reviewed. Logic and workflow extracted; tool usage and tuned thresholds deliberately left behind. The prior detector was really “a right turn while something was detected”, and nothing was scored against ground truth.",
    caveat: "No historical calibration data exists. The internal mini-hackathon is the only source.",
  },
  {
    ticket: "08",
    title: "Duration",
    answer:
      "Not a decision — fixed by the published programme. Thursday 3 September 2026, 09:30–12:30, with a separate 14:30–15:00 results slot.",
    caveat:
      "Pitches can leave the three-hour block entirely, and teams get the two-hour lunch to prepare one. §4.2 needs rebuilding around this.",
  },
];

/** Verified against the published programme on 30 July 2026. */
export const eventFacts = {
  where: "Miyazaki City, Japan",
  when: "31 Aug – 4 Sep 2026",
  slot: "Hackathon Thu 3 Sep, 09:30–12:30 · results 14:30–15:00",
  daysOut: 35,
};

/** Open questions. Deliberately visible; resolve in dependency order. */
export const decisionsOpen: { ticket: string; choices: string; blocked?: string; urgent?: boolean }[] = [
  {
    ticket: "19",
    choices:
      "is the camera imagery clear to redistribute? CC BY 4.0 does not license privacy rights, and no consent, anonymisation or ethics statement exists in the public record",
    urgent: true,
  },
  { ticket: "17", choices: "how does 112 GB (16 bags × ~7 GB) reach BYOD laptops offline? subsetting and distribution", urgent: true },
  { ticket: "18", choices: "what is an “unprotected right turn” operationally? you cannot label what you have not defined", urgent: true },
  { ticket: "15", choices: "review and test gates for AI-built tooling — no definition of done yet" },
  { ticket: "09", choices: "EventSpec with CEL only | EventSpec plus an advanced Python detector API" },
  { ticket: "10", choices: "PlotJuggler 4 only | PlotJuggler 4 plus Lichtblick for robotic context" },
  { ticket: "11", choices: "no model supplied | one pinned local CPU model | shared on-site inference service" },
  { ticket: "12", choices: "agent as unscored demonstration | agent bonus up to 10 points | separate advanced prize", blocked: "11" },
  { ticket: "13", choices: "`cive` CLI name | `civ` CLI name" },
  { ticket: "07", choices: "strict legal clean-room process | independent functional reimplementation with provenance review" },
  { ticket: "16", choices: "URT evaluator calibration: tolerance, duplicates, missing data — no historical calibration data exists", blocked: "09, 18" },
  { ticket: "14", choices: "bespoke French-city bags — recommendation is now to rule out of scope: 35 days, mirrored handedness, worse personal-data posture" },
];

export const blockers = [
  { title: "Resolve the three blockers", detail: "Scenario and data rights, target machine, and the three-hour contract. They constrain everything else." },
  { title: "Assign five owners", detail: "Data, runner/contracts, evaluation, attendee experience, release engineering." },
  { title: "Run the one-bag slice", detail: "MCAP → detector → batch → evidence clip → score, offline, before building slides or agents." },
];

export const sources = [
  "exploration/data-hackathon-01-brainstorming.md — initial goals and inheritance from CIV 2025",
  "exploration/data-hackathon-02-survey-and-directions.md — expanded format, architecture, evaluation, preparation",
  "exploration/open-source-landscape-research.md — tool and licence landscape",
  "exploration/side-chat-explorations/handoff-recommended-hackathon-shape.md — rule ladder and evidence-centred deliverable",
  "exploration/side-chat-explorations/handoff-early-vertical-slice.md — ownership boundary and organizer-first slice",
  "exploration/side-chat-explorations/handoff-agent-skills-for-hackathon.md — reference flow and scoring",
  "exploration/exploration-notes-INBOX.md — clean implementation intent and AI-as-enabler framing",
];
