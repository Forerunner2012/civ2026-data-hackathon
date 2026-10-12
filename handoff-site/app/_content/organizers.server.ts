/**
 * Organizer-only content — NOT for participants.
 *
 * Production builds scan `public-source/app`, so this module and the organizer
 * route are absent from the public server and client artifacts. Local
 * development scans the full app tree and keeps this internal handoff usable.
 */
import "server-only";

export type Level = "strategy" | "tactics" | "operations";

export const planning = {
  strategy: {
    eyebrow: "Why this event exists",
    title: "Turn raw robotics logs into reusable engineering knowledge.",
    summary:
      "The north star is not a winning timestamp. It is a compact, defensible and repeatable path from observation to action that survives a change of dataset.",
    steps: [
      ["01", "Lock the mission", "Thirty experienced practitioners work solo or in duos and leave with an executable, transferable detector."],
      ["02", "Protect the principles", "Evidence-first, local-first, deterministic core, optional extension, open contracts and progressive disclosure."],
      ["03", "Define success", "Entries batch both datasets, expose one failure, reproduce in one command and state what transferred."],
      ["04", "Guard the scope", "No platform rebuild, day-of compilation, paid key, mandatory GPU or infrastructure contest."],
    ],
  },
  tactics: {
    eyebrow: "How the challenge creates learning",
    title: "One ladder: Kashiwa warm-up → Reims transfer → optional extension.",
    summary:
      "Kashiwa teaches the prepared path. France reveals whether participants understood the event rather than copied a threshold.",
    steps: [
      ["01", "Shape the challenge", "Start with an incomplete incident report; require detector, evidence, limits, transfer and operational response."],
      ["02", "Set the cadence", "Observe, formalize and scale Kashiwa; transfer to Reims IMU/GNSS; challenge a failure; submit by 12:30."],
      ["03", "Make proof the contract", "Machine-score 55 points; jury-score 45 from a capped report; never grade prompt style."],
      ["04", "Extend through seams", "External resources plug in through resources:; custom computation stays behind the reserved detector: seam."],
    ],
  },
  operations: {
    eyebrow: "What must exist before day zero",
    title: "Prove two stacks, then freeze artifacts and rehearse throughput.",
    summary:
      "Build only what carries an attendee from both datasets to a scored evidence package and a one-page argument.",
    steps: [
      ["P0", "Contract", "Scenario, rights, cohort, skill floor, publication, judging and licence posture approved."],
      ["P1", "Vertical slice", "Kashiwa and Reims each complete inspect → detector → batch → clip → score offline."],
      ["P2", "Golden path", "EventSpec seams, CLI, exact schemas, runtime candidates and quickstart frozen."],
      ["P3", "Data + score", "Both dev/sealed splits labelled and the 15/10 rank test passed."],
      ["P4", "Experience", "Public participant site, two-stack fallback, report/jury pack and layouts packaged."],
      ["P5", "Release", "Offline rehearsal, 30-entry throughput and built-image SBOM/source-notice gates passed."],
    ],
  },
} satisfies Record<Level, { eyebrow: string; title: string; summary: string; steps: string[][] }>;

export const successCriteria = [
  "At least 80% of entries complete both dataset runs and a valid submission",
  "Every one-page report carries evidence, one failure and a transfer statement",
  "A fresh laptop runs the required path offline",
  "The same submission produces stable results on rerun",
  "All 15–30 submissions score unattended inside the lunch window",
  "Agent or extension work points to executed tools, sources and evidence",
];

export const nonGoals = [
  "Rebuilding a full fleet-data platform",
  "Teaching ROS installation or container debugging",
  "Requiring a dashboard, GPU, paid model or API key",
  "Grading prompt style",
  "Making every participant invent an advanced detector",
  "Deploying real edge or OTA infrastructure during the session",
];

export const phases: { id: string; title: string; work: string; gate: string }[] = [
  {
    id: "P0",
    title: "Lock the challenge contract",
    work: "Record the two-dataset arc, 30-person solo/duo cohort, high skill floor, programme slots, rights, publication policy, judging model and licence posture.",
    gate: "The revised challenge contract is approved.",
  },
  {
    id: "P1",
    title: "Prove the organizer vertical slice",
    work: "Run Kashiwa and one Reims chunk through inspect → PlotJuggler → EventSpec → batch → events.jsonl → evidence clip → score → report. Measure time, RAM, disk and offline behaviour.",
    gate: "Both sensor stacks complete on the minimum machine without Internet.",
  },
  {
    id: "P2",
    title: "Freeze interfaces and the golden path",
    work: "Freeze CEL, timing, evidence, derive, resources and min_distance_to; reserve detector:; pin schema-matching commits and test the CEL runtime candidate.",
    gate: "A new user reaches a first clip in under 20 minutes and the contracts run on both stacks.",
  },
  {
    id: "P3",
    title: "Build data and evaluation",
    work: "Cut Kashiwa 1+7+8 and Reims five-chunk/four-chunk splits, finish labels, apply temporal IoU matching, rank deliberate detectors on both sets and test 30-entry scoring.",
    gate: "Scoring separates plausible solutions without one magic threshold or manual repair.",
  },
  {
    id: "P4",
    title: "Package the attendee and jury experience",
    work: "Pin viewers, prepare two layouts and fallback packs, publish the participant-only site, and build the fixed report, jury rubric, coach guide and results walkthrough flow.",
    gate: "One public start page and one command path cover the room; no organizer content exists in the public artifact.",
  },
  {
    id: "P5",
    title: "Rehearse and cut the release candidate",
    work: "Fresh-install offline, simulate 15–30 entries and lunch judging, freeze image and dependency digests, then generate SBOM, notices and source/relinking evidence from the built image.",
    gate: "The internal mini-hackathon and the behavioural, throughput, offline and licence gates all pass.",
  },
];

export const readiness: { name: string; status: string; detail: string }[] = [
  { name: "Data", status: "SUBSET + LABEL", detail: "Kashiwa 1+7+8 and Reims five/four splits are decided. Measure Kashiwa bytes, cut packages and turn planning intervals into reviewed labels." },
  { name: "Contracts", status: "DRAFT → FREEZE", detail: "EventSpec + CEL, timing, evidence, derive, resources, min_distance_to, event JSONL and run manifest." },
  { name: "Runner", status: "BUILD", detail: "doctor, inspect, sample, detect, clip, score and report; two stacks, dry-run and actionable errors." },
  { name: "Views", status: "PIN + AUDIT", detail: "PlotJuggler 3.999.3 beta2 required; Lichtblick ships only if its exact artifact passes audit." },
  { name: "Dependencies", status: "PIN", detail: "Humble base digest; MCAP, Polars and CEL hashes; custom schemas by commit plus MCAP schema hash." },
  { name: "Evaluation", status: "DESIGN EARLY", detail: "IoU ≥ 0.5, one-to-one F1, 15/10 two-set ranking, 55 machine / 45 report points and 30-entry throughput." },
  { name: "Experience", status: "PACKAGE", detail: "Solo/duo warm-up, transfer checkpoint, one-page report, jury pack, public site and selected walkthroughs." },
  { name: "Release", status: "SBOM + SOURCE", detail: "Built-image inventory, notices, Debian copyright, MPL source archive and reviewed GPL/LGPL paths." },
];

/** Evaluation mechanics that must stay out of participant-facing material. */
export const evaluationDesign = [
  "Sealed ground truth stays out of every distributed artifact",
  "Kashiwa scores 15 Detection points and Reims 10, provisional until the two-set rank test",
  "Temporal IoU ≥ 0.5, one-to-one best match and F1; extra overlaps are false positives",
  "Reims sealed labels cover nine clear junction-left manoeuvres in chunks _5–_8",
  "Development output validates format and basic metrics — never the sealed result",
  "At 12:30, 55 points run unattended; the jury assigns 45 from capped reports over lunch",
  "Roughly four walkthroughs include the most instructive failure and do not alter ranking",
  "The evaluator must process 15–30 submissions without organizer repair",
];

export const facilitation = [
  "Thirty experienced practitioners work solo or in duos on one leaderboard",
  "The former investigator/author/reviewer/pitch roles are a checklist, not four people",
  "Visible checkpoints at 30, 60, 90, 135 and 165 minutes; tune them in rehearsal",
  "Coaches ask for evidence and assumptions before suggesting thresholds",
  "A short timebox precedes intervention on blocked tooling",
  "Two-stack pre-extracted tables and clips keep reasoning alive if the container fails",
  "Submission intake, report division and unattended scoring are exercised before event day",
];

export const drivingForces = [
  { title: "A concrete engineering question", effect: "prevents aimless visualization." },
  { title: "Two physical data structures", effect: "separate understanding from threshold copying." },
  { title: "Limited time and compute", effect: "reward reduction and prepared tooling." },
  { title: "Partial and hidden truth", effect: "create a real validation loop." },
  { title: "Evidence requirements", effect: "prevent unsupported timestamps or AI claims." },
  { title: "Failure visibility", effect: "makes false positives, misses and poor data productive." },
  { title: "Operational transfer", effect: "turns the detector into a decision." },
];

export type Decision = { ticket: string; group: string; title: string; answer: string; caveat?: string };

/** All 25 wayfinder tickets, resolved 30 July 2026. */
export const decisionsMade: Decision[] = [
  { ticket: "01", group: "Challenge", title: "Dataset", answer: "URT-Kashiwa is the hero dataset; the Reims recording is the scored transfer test." },
  { ticket: "02", group: "Challenge", title: "Scenario", answer: "Unprotected right turns anchor Kashiwa; creativity lies in executable capture and transfer." },
  { ticket: "18", group: "Challenge", title: "Event definition", answer: "Sealed labels mark the right-turn manoeuvre interval in Kashiwa and the left-turn interval in France.", caveat: "Unprotected is context, not something the detector proves." },
  { ticket: "03", group: "Challenge", title: "Scoring basis", answer: "Sealed labels score the target turn; other event types remain a qualitative bonus." },
  { ticket: "08", group: "Challenge", title: "Programme", answer: "Thu 3 Sep, 09:30–12:30; results 14:30–15:00 after lunch." },
  { ticket: "20", group: "Challenge", title: "Cohort and publication", answer: "Thirty experienced practitioners work solo or in duos; CLI, content and public site ship permissively." },
  { ticket: "21", group: "Challenge", title: "Judging", answer: "At 12:30, 55 points auto-score; jury reads one-page reports for 45 over lunch; results reveal plus about four walkthroughs.", caveat: "Detection starts 15 Kashiwa / 10 Reims and may move only after internal rank testing." },

  { ticket: "09", group: "Toolchain", title: "Detector surface", answer: "CEL + timing + evidence is the pass mark; derive is the reach; detector: reserves Python/conflict geometry." },
  { ticket: "13", group: "Toolchain", title: "CLI name", answer: "civ." },
  { ticket: "10", group: "Toolchain", title: "Viewer", answer: "PlotJuggler required; Lichtblick optional.", caveat: "Current identified PlotJuggler asset is 3.999.3, explicitly beta2." },
  { ticket: "04", group: "Toolchain", title: "Target machine", answer: "Container-first, BYOD only, Windows/WSL2 + Ubuntu, CPU-only.", caveat: "No hardware swap: the non-ROS fallback remains load-bearing." },
  { ticket: "11", group: "Toolchain", title: "Model policy", answer: "No model shipped; participant-supplied models remain optional." },
  { ticket: "12", group: "Toolchain", title: "Bonus scoring", answer: "Maximum +20: grounded trace +10, advanced method +5, and failure-derived regression test +5; every non-zero award cites an accepted artifact." },
  { ticket: "25", group: "Toolchain", title: "Extension track", answer: "External resources plug in through resources: + min_distance_to and score under the advanced-method +5 row.", caveat: "Method is unconstrained and judged from bundled provenance and evidence." },
  { ticket: "23", group: "Toolchain", title: "Licences", answer: "Named tools compose; standardize on Humble/Jammy and gate release on exact pins, SBOM, notices and source/relink review.", caveat: "The aggregate image has no single MIT, Apache or CC licence." },

  { ticket: "05", group: "Data & evaluation", title: "Kashiwa rights", answer: "CC BY 4.0 permits subsets and permanent offline copies; attribution is required." },
  { ticket: "19", group: "Data & evaluation", title: "Camera imagery", answer: "Cleared through T-Lab participation." },
  { ticket: "17", group: "Data & evaluation", title: "Kashiwa distribution", answer: "One warm-up + seven dev + eight sealed; drop point clouds/map, retain full-rate detector signals and tested camera evidence.", caveat: "Kashiwa per-topic bytes remain to measure." },
  { ticket: "24", group: "Data & evaluation", title: "Reims survey", answer: "Sixteen clear left turns; chunks _0–_4 dev and _5–_8 sealed. Full-session detector signals are about 350 MB.", caveat: "Reims GNSS supports two 40 m cave encounters." },
  { ticket: "16", group: "Data & evaluation", title: "Evaluator", answer: "Temporal IoU ≥ 0.5, one-to-one best match and F1; extra overlapping predictions are false positives." },

  { ticket: "07", group: "Process", title: "Clean-room boundary", answer: "Independent functional reimplementation around the prior stack and vocabulary, not the domain logic." },
  { ticket: "15", group: "Process", title: "AI build gates", answer: "Gate by failure visibility × cost; human-authored Tier A assertions; cut anything missing its gate." },
  { ticket: "14", group: "Process", title: "Reims bags", answer: "Reversed into the main track as the scored generalisation test across sensor stacks and handedness." },
  { ticket: "06", group: "Process", title: "Previous solution", answer: "Logic and workflow extracted; the historical stack and terminology left behind." },
  { ticket: "22", group: "Process", title: "Public organizer gate", answer: "Production builds contain only the participant app; /organizers and its content exist only in local development." },
];

export const decisionGroups = ["Challenge", "Toolchain", "Data & evaluation", "Process"];

export const eventFacts = {
  where: "Miyazaki City, Japan",
  when: "31 Aug – 4 Sep 2026",
  slot: "Hackathon Thu 3 Sep, 09:30–12:30",
  results: "Results 14:30–15:00",
};

export const blockers = [
  { title: "Mirror and cut the datasets", detail: "Mirror 16 Kashiwa MCAPs, measure its per-topic bytes, then cut Kashiwa 1+7+8 and Reims five/four packages with manifests." },
  { title: "Prove the two-stack vertical slice", detail: "Run inspect → EventSpec → detect → clip → score → report offline on the minimum machine for Kashiwa and Reims." },
  { title: "Finish labels and rank testing", detail: "Review Kashiwa and Reims sealed intervals, rank deliberate detectors across both sets and tune 15/10 only if evidence requires it." },
  { title: "Freeze exact artifacts", detail: "Pin Humble base digest, viewer assets, MCAP/Polars/CEL hashes and schema-matching custom-message commits." },
  { title: "Prove judging throughput", detail: "Accept and auto-score 15–30 submissions, split the capped reports, and rehearse the reveal plus four walkthroughs." },
  { title: "Pass the release-compliance gate", detail: "Generate built-image SBOM/notices, archive exact MPL source and review unknown, GPL/LGPL and relinking/source findings." },
];

export const sources = [
  "exploration/data-hackathon-01-brainstorming.md — initial goals and inheritance from CIV 2025",
  "exploration/data-hackathon-02-survey-and-directions.md — architecture, evaluation and preparation",
  "exploration/side-chat-explorations/handoff-recommended-hackathon-shape.md — rule ladder and proof contract",
  ".scratch/civ2026-challenge-spec/map.md — complete 25-ticket decision map",
  ".scratch/civ2026-challenge-spec/research/23-tool-licence-audit.md — primary-source licence and release audit",
  ".scratch/civ2026-challenge-spec/research/survey_reims_bag.py + ticket 24 — measured Reims manoeuvre, GNSS and zone evidence",
];

/** Approved historical design; original planning exports below remain preserved as evidence. */
export const historicalDesign = [
  { id: "purpose", title: "Purpose", description: "Turn observations in robotics recordings into reproducible EventSpec rules. Support the result with inspected evidence, a documented failure, and a concrete next action." },
  { id: "challenge", title: "Challenge", description: "Develop the first rule on URT-Kashiwa, then test what transfers to the Reims sensor stack. The historical target manoeuvres are Kashiwa right turns and Reims left turns. Unprotected is scenario context; a detected turn does not prove it." },
  { id: "workflow", title: "Workflow", description: "Inspect the recording, write an EventSpec, run it across practice recordings, review evidence, and refine one failure. Transfer the workflow to the second stack, then reproduce and submit the result. External-resource work is an optional extension. Exact commands remain in the canonical quickstart." },
  { id: "requirements", title: "Requirements", description: "Submit the detector/EventSpec, normalized events, metrics, capped report, figure, reproduction entry point, and run manifest in the metadata-only bundle. Keep source recordings and evidence clips local. No paid model, API key, or GPU is required." },
  { id: "evaluation", title: "Evaluation", description: "The historical scoring framework combines 55 machine points, 45 jury points, and up to 20 evidence-backed bonus points. Temporal interval matching uses IoU ≥ 0.5, one-to-one matching, and F1. Jury awards follow the rubric and accepted artifacts, with defined human arbitration." },
  { id: "organizing", title: "Organizing choices", description: "Participants worked solo or in pairs. Coaches supported the next observation without supplying solutions or private evaluation facts. The design included timed checkpoints, tooling recovery, metadata-only intake, written feedback, and consent for selected walkthroughs." },
] as const;
