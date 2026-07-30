/**
 * Participant-facing content.
 *
 * Everything in this module is public to attendees. It states the contract they
 * are held to — brief, journey, deliverables, rubric, toolchain — but never the
 * organizer's preparation or evaluation internals. Organizer material lives in
 * `organizers.server.ts`, which is absent from the production artifact.
 */

export const brief =
  "A fleet recorded several passages through a shared environment. A risky or operationally significant behaviour was reported, but the report is incomplete. You must locate relevant occurrences, encode a reusable detector, transfer the reasoning to a structurally different recording, extract compact evidence, evaluate its limitations, and recommend what should happen next.";

/** The three-hour rehearsal baseline, told as activity and output. */
export const journey: { time: string; title: string; doing: string; produces: string }[] = [
  {
    time: "00:00",
    title: "Observe",
    doing: "Explore one development route manually with a prepared layout.",
    produces: "A relevant signal, candidate interval and physical hypothesis.",
  },
  {
    time: "00:30",
    title: "Formalize",
    doing: "Express the observation as an executable EventSpec.",
    produces: "Your first normalized event and evidence clip.",
  },
  {
    time: "01:00",
    title: "Scale",
    doing: "Batch the detector and inspect one false positive, miss or ambiguity.",
    produces: "Events, clips, metrics and one reasoned iteration.",
  },
  {
    time: "01:30",
    title: "Transfer",
    doing: "Map the same physical event onto a different sensor stack and driving context.",
    produces: "A working detector on the second development set.",
  },
  {
    time: "02:15",
    title: "Challenge",
    doing: "Compare both datasets and state exactly what transferred and what did not.",
    produces: "Defensible evidence and a documented boundary.",
  },
  {
    time: "02:45",
    title: "Submit",
    doing: "Rerun reproduction, finalize the one-page report and hand in by 12:30.",
    produces: "A valid submission ready for automated scoring.",
  },
];

export const youOwn = [
  "Which signals and fields are worth inspecting on both recordings",
  "Preprocessing and derived features",
  "Thresholds and CEL logic",
  "Boolean and temporal composition",
  "Debounce and deduplication parameters",
  "Evidence-window duration and retained topics",
  "What transferred between sensor stacks — and what had to change",
  "Failure analysis and professional recommendation",
];

export const youReceive = [
  "MCAP/ROS decoding and schema availability",
  "Topic and field inventories plus sampling utilities",
  "A deterministic detector runner and batch iteration",
  "Time synchronization, hashes, provenance and run manifest",
  "Clip extraction and standardized output",
  "Tested PlotJuggler layouts and an offline bundle",
  "Development data, a reference detector and a submission template",
];

export const deliverables = [
  "The engineering question and your detection hypothesis",
  "The signals you used, what was missing, and what you judged unreliable",
  "An executable EventSpec or detector",
  "Normalized events.jsonl and compact MCAP evidence clips",
  "A run manifest and metrics",
  "One synchronized evidence view",
  "One false positive, false negative or ambiguity — and what you changed",
  "A one-command reproduction path",
  "A one-page report: question, signals, transfer, failure and next action",
  "Optional: an agent trace or extension artifact with provenance",
];

export const scoring: { category: string; points: number; looksFor: string }[] = [
  { category: "Investigation and hypothesis", points: 15, looksFor: "Deliberate signal choice, inspection, physical reasoning" },
  { category: "Detection", points: 25, looksFor: "15 points on the first set, 10 on transfer; timing, duplicates, robustness" },
  { category: "Evidence and extraction", points: 15, looksFor: "Useful context, correct clips, meaningful volume reduction" },
  { category: "Quality and evaluation", points: 15, looksFor: "Metrics, failure analysis, missing and bad data handling" },
  { category: "Visualization and explanation", points: 15, looksFor: "Synchronized, legible proof and careful claims" },
  { category: "Reproducibility", points: 15, looksFor: "One command, pinned inputs, manifest, stable output" },
];

export const bonus = [
  { label: "Bounded agent with a useful trace", points: 10 },
  { label: "Advanced multimodal, data-quality or external-resource method", points: 5 },
  { label: "Regression test built from a failure you found", points: 5 },
];

/** Published scoring and judging rules; the labels themselves remain private. */
export const scoringRules = [
  "The common score is 100 points, with up to 20 bonus points on top.",
  "Detection is split 15 points on the first sealed set and 10 on the transfer set.",
  "At 12:30, 55 points are machine-scored; the jury reads the one-page report for the other 45 over lunch.",
  "A development score validates submission format and basic metrics during the session.",
  "The final ranking runs on a sealed test set, so a detector tuned to one route will not travel.",
  "Solo and duo entries share one leaderboard; the selected afternoon walkthroughs do not change the score.",
  "Bonus points cannot compensate for a core result that does not reproduce.",
  "Prompt style is not graded. Executed evidence is.",
];

export const pipeline: { title: string; note: string; owner: "you" | "provided" }[] = [
  { title: "MCAP", note: "two recording structures", owner: "provided" },
  { title: "PlotJuggler", note: "manual exploration", owner: "provided" },
  { title: "Polars", note: "selected signals", owner: "provided" },
  { title: "EventSpec + CEL", note: "your detection logic", owner: "you" },
  { title: "Batch runner", note: "scale + provenance", owner: "provided" },
  { title: "Evidence", note: "clips + score", owner: "provided" },
];

export const commands = [
  { command: "civ doctor", note: "check your machine" },
  { command: "civ inspect BAG", note: "topics, fields, durations" },
  { command: "civ sample BAG --topic ...", note: "pull signals into a table" },
  { command: "civ detect SPEC DATASET", note: "run your detector, --dry-run first" },
  { command: "civ clip EVENTS DATASET", note: "cut compact evidence" },
  { command: "civ score SUBMISSION", note: "development score" },
  { command: "civ report SUBMISSION", note: "package the one-page argument" },
];

export const submissionTree = `submission/
├── detector/              # EventSpec and optional extension code
├── events.jsonl           # normalized detections
├── evidence/              # compact MCAP clips
├── metrics.json
├── run-manifest.json      # versions, hashes, parameters, timings
├── report.md              # one page: hypothesis, transfer, failure, action
├── extension/             # optional resources and tool trace
└── reproduce.ps1|sh       # one-command entry point`;

export const comeReady = [
  "A laptop you can install software on. CPU-only is enough — no GPU is required.",
  "Set up before you arrive: Docker, plus WSL2 on Windows. The kit ships as a container.",
  "Run the environment check in the week before the event; use the support channel before event morning.",
  "Nothing to compile or download on the day: the kit is prebuilt, pinned and versioned.",
  "No account, paid model or API key is required. The required path runs fully offline.",
  "Work solo or with one partner. Solo and duo entries share one leaderboard.",
  "Bring experience with robotic or vehicular recordings; the challenge starts above the beginner floor.",
];

export const notYourJob = [
  "Implementing MCAP parsing or ROS message discovery",
  "Synchronizing time or scheduling batch jobs",
  "Building provenance, clip generation or scoring",
  "Debugging containers or ROS installations",
  "Shipping a dashboard or training a model",
];
