/**
 * Participant-facing content.
 *
 * Everything in this module is public to attendees. It states the contract they
 * are held to — brief, journey, deliverables, rubric, toolchain — but never the
 * organizer's preparation, evaluation internals or open decisions. Organizer
 * material lives in `organizers.server.ts`, which cannot be imported from here.
 */

export const brief =
  "A fleet recorded several passages through a shared environment. A risky or operationally significant behaviour was reported, but the report is incomplete. Your team must locate relevant occurrences, encode a reusable detector, extract compact evidence, evaluate its limitations, and recommend what should happen when the event is detected.";

/** The three-hour ladder, told as activity and output rather than mechanics. */
export const journey: { time: string; title: string; doing: string; produces: string }[] = [
  {
    time: "00:00",
    title: "Observe",
    doing: "Explore one development bag with prepared layouts.",
    produces: "A relevant topic, field and candidate window.",
  },
  {
    time: "00:30",
    title: "Formalize",
    doing: "Express the observation as one executable comparison.",
    produces: "Your first normalized event and evidence clip.",
  },
  {
    time: "01:00",
    title: "Contextualize",
    doing: "Add a second signal, a derived feature, AND/OR, duration or ordering.",
    produces: "An improved detector with a stated hypothesis.",
  },
  {
    time: "01:45",
    title: "Scale",
    doing: "Run the same detector across every development bag.",
    produces: "events.jsonl, clips, metrics and a run manifest.",
  },
  {
    time: "02:15",
    title: "Challenge",
    doing: "Investigate a false positive, a miss, a missing signal or an ambiguity.",
    produces: "A documented failure and one iteration.",
  },
  {
    time: "02:45",
    title: "Transfer",
    doing: "Give a three-minute evidence pitch.",
    produces: "Question, proof, limit and next action.",
  },
];

export const youOwn = [
  "Which signals and fields are worth inspecting",
  "Preprocessing and derived features",
  "Thresholds, CEL logic or model inference",
  "Boolean and temporal composition",
  "Debounce and deduplication parameters",
  "Evidence-window duration and retained topics",
  "Statistical analysis and interpretation",
  "Failure analysis and professional transfer",
];

export const youReceive = [
  "MCAP/ROS decoding and schema availability",
  "A topic and field inventory plus sampling utilities",
  "A deterministic detector runner and batch iteration",
  "Time synchronization, hashes, provenance and run manifest",
  "Clip extraction and standardized output",
  "Tested PlotJuggler 4 layouts and an offline bundle",
  "A warm-up bag, a reference detector and a submission template",
];

export const deliverables = [
  "The engineering question and your detection hypothesis",
  "The data you used, what was missing, and what you judged unreliable",
  "An executable EventSpec or detector",
  "Normalized events.jsonl and compact MCAP evidence clips",
  "A run manifest and metrics",
  "One synchronized evidence view",
  "One false positive, false negative or ambiguity — and what you changed",
  "A one-command reproduction path",
  "The downstream action and the relevant deployment mode",
  "Optional: an agent trace or advanced-analysis artifact",
];

export const scoring: { category: string; points: number; looksFor: string }[] = [
  { category: "Investigation and hypothesis", points: 15, looksFor: "Deliberate signal choice, inspection, physical reasoning" },
  { category: "Detection", points: 25, looksFor: "Accuracy, temporal logic, duplicate handling, robustness" },
  { category: "Evidence and extraction", points: 15, looksFor: "Useful context, correct clips, meaningful volume reduction" },
  { category: "Quality and evaluation", points: 15, looksFor: "Metrics, failure analysis, missing and bad data handling" },
  { category: "Visualization and explanation", points: 15, looksFor: "Synchronized, legible proof and careful claims" },
  { category: "Reproducibility", points: 15, looksFor: "One command, pinned inputs, manifest, stable output" },
];

export const bonus = [
  { label: "Bounded agent with a useful trace", points: 10 },
  { label: "Advanced multimodal or data-quality method", points: 5 },
  { label: "Regression test built from a failure you found", points: 5 },
];

/**
 * Published scoring rules. Attendees are told up front that the final ranking
 * runs on a sealed set — the rule is public even though the labels are not.
 */
export const scoringRules = [
  "The common score is 100 points, with up to 20 bonus points on top.",
  "A public development score validates your submission format and basic metrics during the session.",
  "The final ranking is computed on a sealed test set, so a detector tuned to one bag will not travel.",
  "Bonus points cannot compensate for a core result that does not reproduce.",
  "Prompt style is not graded. Executed evidence is.",
];

export const pipeline: { title: string; note: string; owner: "you" | "provided" }[] = [
  { title: "MCAP", note: "raw recording", owner: "provided" },
  { title: "PlotJuggler 4", note: "manual exploration", owner: "provided" },
  { title: "Polars", note: "selected signals", owner: "provided" },
  { title: "EventSpec + CEL", note: "your detection logic", owner: "you" },
  { title: "Batch runner", note: "scale + provenance", owner: "provided" },
  { title: "Evidence", note: "clips + score", owner: "provided" },
];

export const commands = [
  { command: "cive doctor", note: "check your machine" },
  { command: "cive inspect BAG", note: "topics, fields, durations" },
  { command: "cive sample BAG --topic ...", note: "pull signals into a table" },
  { command: "cive detect SPEC DATASET", note: "run your detector, --dry-run first" },
  { command: "cive clip EVENTS DATASET", note: "cut compact evidence" },
  { command: "cive score SUBMISSION", note: "public development score" },
  { command: "cive report SUBMISSION", note: "package the write-up" },
];

export const submissionTree = `submission/
├── detector/              # EventSpec and optional code
├── events.jsonl           # normalized detections
├── evidence/              # compact MCAP clips
├── metrics.json
├── run-manifest.json      # versions, hashes, parameters, timings
├── report.md              # hypothesis, evidence, failure, transfer
└── reproduce.ps1|sh       # one-command entry point`;

export const comeReady = [
  "A laptop. CPU-only is enough — no GPU is required.",
  "Nothing to install on the day: the kit is prebuilt, pinned and versioned.",
  "No account, no paid model and no API key. The required path runs fully offline.",
  "Teams of 3–5. Suggested roles: investigator, detector author, evidence reviewer, pitch owner.",
  "Curiosity about physical signals matters more than ROS experience.",
];

export const notYourJob = [
  "Implementing MCAP parsing or ROS message discovery",
  "Synchronizing time or scheduling batch jobs",
  "Building provenance, clip generation or scoring",
  "Debugging containers or ROS installations",
  "Shipping a dashboard or training a model",
];
