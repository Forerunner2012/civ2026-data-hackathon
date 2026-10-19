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

export const participantOpening =
  "Investigate an incomplete report of vehicle behaviour. Inspect the recordings, write an EventSpec, and test your reasoning on a different recording. Check the evidence, explain one failure, and recommend a next action.";

export const participantIntroduction =
  `${participantOpening} Start with the participant page and kit README, then follow the kit's docs/quickstart.md. Build a reproducible metadata-only bundle. Recordings and evidence clips stay local.`;

export const datasetAttributionUrl =
  "https://github.com/Forerunner2012/civ2026-data-hackathon/blob/main/kit/ATTRIBUTION.md";

/**
 * The three-hour run of show. A rehearsal baseline, not a countdown: the order
 * and the 12:30 deadline are fixed, the minutes may move.
 */
export const journey: { time: string; title: string; doing: string; produces: string }[] = [
  {
    time: "09:30",
    title: "Briefing",
    doing: "Five minutes on where everything is and what to do if you get lost.",
    produces: "Nothing to build yet. Open your supplied kit while you listen.",
  },
  {
    time: "09:35",
    title: "By hand",
    doing: "Mark every occurrence you can find on a printed trace. Pen, paper, no laptop.",
    produces: "Your own candidate intervals, drawn by eye.",
  },
  {
    time: "09:45",
    title: "Compare",
    doing: "Put your marks next to your neighbour's.",
    produces: "A disagreement worth having — and the reason intervals need a tolerance.",
  },
  {
    time: "09:50",
    title: "Check",
    doing: "Confirm the toolchain runs and that you can reach the day's page.",
    produces: "A working environment, or a coach on their way to you.",
  },
  {
    time: "10:00",
    title: "Formalize",
    doing: "Express the observation as an executable EventSpec and run it.",
    produces: "Your first normalized event and evidence clip.",
  },
  {
    time: "10:40",
    title: "Scale",
    doing: "Run your EventSpec across recordings and inspect one failure you can name.",
    produces: "Events, metrics, one reasoned iteration — and report headings 1 and 2, written now.",
  },
  {
    time: "11:00",
    title: "Transfer",
    doing: "Map the same physical event onto a different sensor stack and driving context.",
    produces: "A working detector on the second practice set.",
  },
  {
    time: "11:45",
    title: "Challenge",
    doing: "Compare both recordings and state exactly what transferred and what did not.",
    produces: "Headings 3 and 4, written while the transfer is fresh.",
  },
  {
    time: "12:10",
    title: "Package",
    doing: "Rerun reproduction, finish the one-page report, build and validate the metadata-only ZIP, then keep it and its SHA-256 locally.",
    produces: "A validated metadata-only ZIP and its SHA-256, with recordings and evidence kept locally through 12:30.",
  },
];

/**
 * The static participant page points readers to the separate live session page.
 */
export const theDayPage = [
  "This participant page and its kit copy are static guides. Use the separate live page supplied for your session.",
  "The live page states what you should have at each step and what to do if you do not.",
  "Hints and tips unlock on the live page as the session goes. Waiting for a public hint is allowed.",
  "A coach can release the next hints early for the whole room, so help is never private.",
  "Worked solutions require a separate approved release after the session.",
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
  "Pre-loaded PlotJuggler and Lichtblick layouts for both recordings, and an offline bundle",
  "Practice data, a reference detector and a submission template",
  "Complete reviewed practice labels for the exact source announced in your session, when supplied",
  "These labels may be shared in the same space as participant kits at a time chosen for your session",
  "Static kit guidance and a separately supplied live page for session progress",
  "Setup and recovery instructions in docs/setup.md",
];

export const deliverables = [
  "The engineering question and your detection hypothesis",
  "The signals you used, what was missing, and what you judged unreliable",
  "An executable EventSpec",
  "Normalized events.jsonl — the intervals you found, not the data behind them",
  "A run manifest and metrics, recording the clips you cut: topics, durations, bytes in and out",
  "One figure in the report — a plot or a frame with the occurrence marked",
  "One false positive, false negative or ambiguity — and what you changed",
  "A one-command reproduction path",
  "A one-page report: question, signals, transfer, failure and next action",
  "Optional v2 extension: grounded trace, advanced-method provenance, and regression test",
];

export const scoring: { category: string; points: number; looksFor: string }[] = [
  { category: "Investigation and hypothesis", points: 15, looksFor: "Deliberate signal choice, inspection, physical reasoning" },
  { category: "Detection", points: 25, looksFor: "15 points on the first set, 10 on transfer; timing, duplicates, robustness" },
  { category: "Evidence and extraction", points: 15, looksFor: "Read from your run manifest: correct topics, sane windows, real volume reduction" },
  { category: "Quality and evaluation", points: 15, looksFor: "Metrics, failure analysis, missing and bad data handling" },
  { category: "Visualization and explanation", points: 15, looksFor: "Synchronized, legible proof and careful claims" },
  { category: "Reproducibility", points: 15, looksFor: "One command, pinned inputs, manifest, stable output" },
];

export const bonus = [
  { label: "Bounded agent with a useful trace", points: 10 },
  { label: "Advanced multimodal, data-quality or external-resource method", points: 5 },
  { label: "Regression test built from a failure you found", points: 5 },
];

/** Published scoring and judging rules; the answer key itself stays private. */
export const scoringRules = [
  "The common score is 100 points, with up to 20 bonus points on top.",
  "Detection is split 15 points on the first held-back set and 10 on the transfer set.",
  "At 12:30, 55 points are machine-scored; the jury reads the one-page report for the other 45 over lunch.",
  "Practice labels support learning and self-evaluation.",
  "Development metrics do not guarantee results on sealed evaluation.",
  "Sealed evaluation truth is visible only to the event team.",
  "The final ranking runs on a held-back test set.",
  "During the event, participants could submit multiple versions by 12:30. The event team used the latest valid on-time receipt for each participant or duo on each dataset. The team retained late receipts separately. A late receipt did not replace an on-time receipt. For a score tie, the team ranked the entry with the earliest receipt for that score first.",
  "Solo and duo entries share one leaderboard; the selected afternoon walkthroughs do not change the score.",
  "The 45 report points are scored by AI agents against anchors written by a human, with a human resolving any disagreement between them. You are told this because you should know it.",
  "Every entry gets written feedback at 15:00 — not just the ones shown.",
  "Bonus points cannot compensate for a core result that does not reproduce.",
  "Prompt style is not graded. Executed evidence is.",
];

/** What is recognised at 15:00. No prize is attached — this is a podium. */
export const recognition = [
  "First, second and third overall.",
  "Best transfer — what the second recording was really testing.",
  "Most instructive failure. An honest dead end, well analysed, teaches the room more than a clean win.",
  "No prize money and nothing to carry home: a podium, the room's applause and a public mention.",
];

export const pipeline: { title: string; note: string; owner: "you" | "provided" }[] = [
  { title: "MCAP", note: "two recording structures", owner: "provided" },
  { title: "PlotJuggler / Lichtblick", note: "manual exploration", owner: "provided" },
  { title: "Polars", note: "selected signals", owner: "provided" },
  { title: "EventSpec + CEL", note: "your detection logic", owner: "you" },
  { title: "Batch runner", note: "scale + provenance", owner: "provided" },
  { title: "Evidence", note: "clips + score", owner: "provided" },
];

export const workflow = [
  { step: "Inspect", action: "Explore the supplied signals in a viewer or with the CLI." },
  { step: "Detect", action: "Write an EventSpec and run it across the supplied recordings." },
  { step: "Check evidence", action: "Inspect local clips and evaluate the detected intervals." },
  { step: "Package", action: "Run `civ report` to validate the metadata-only ZIP, then keep the ZIP and its SHA-256 locally." },
];

export const kitGuides = [
  { title: "Attendee kit guide", path: "README.md", note: "Kit contents, supplied recordings, layouts, and fallback material." },
  { title: "Viewer guide", path: "viewer/README.md", note: "Choose a supplied viewer and verify its checksum." },
  { title: "Participant quickstart", path: "docs/quickstart.md", note: "Run the workflow and prepare your metadata-only ZIP." },
];

export const deskMaterials = [
  { href: "/desk/warmup-trace.html", title: "Printed signal trace", note: "One write-on A4 sheet for the analogue warm-up." },
  { href: "/desk/help-card.html", title: "Two-sided help card", note: "Print double-sided; raise it when you need a coach." },
  { href: "/desk/brief.html", title: "One-page brief", note: "The session contract, report shape, deadline, and scoring rules." },
];

/**
 * The bundle contains the record of the work. Source recordings stay local.
 * The collection route is retired. This list describes the file contract.
 */
export const submissionTree = `working/                       in ZIP?
├── detector/                  yes   EventSpec + exact declared resources
├── events.jsonl               yes   the intervals you found
├── run-manifest.json          yes   v2 versions, hashes, parameters, timings,
│                                    and per-clip topics / durations / bytes
├── metrics.json               yes
├── report.md                  yes   one page, five headings, one figure
├── extension/manifest.json    if used   bounded payload declarations
├── extension/*                if used   provenance, inert trace, regression test
├── reproduce.ps1|sh           yes   one-command entry point
└── evidence/                  no    your clips stay on your machine`;

export const submissionSteps = [
  "Start once with `civ submission-init working --shell posix` (use `--shell powershell` in PowerShell on Windows). The workspace is deliberately incomplete and is never an answer.",
  "Replace every template prompt, run the stable detect → clip → score path, and keep exactly one reproduction script plus one marked figure.",
  "Run `civ report working`. It builds and validates the metadata-only ZIP and prints its SHA-256. Keep both locally.",
  "Optional traces and regression tests are inert. `civ report` validates their declarations but never runs them.",
  "The historical form and USB route for this event are retired. No collection route or recipient is active. See docs/submission-fields.md for the historical fields and current metadata-only ZIP contract.",
];

/**
 * The optional extension branch. Scored under the existing bonus, never scheduled, and
 * deliberately carries no zone coordinates — sourcing them is the exercise.
 */
export const extensionTrack = {
  lesson: "Find encounters using geographic points from outside both the recording and kit.",
  steps: [
    "Collect the geographic points and note your sources.",
    "Copy the supplied point resource and EventSpec into your workspace. Replace the illustrative points and use them in the EventSpec.",
    "Run detection, inspect the evidence, and include your resource and provenance in the submission.",
  ],
};

export const comeReady = [
  "Bring a laptop you can install software on, with space for the supplied kit and recordings.",
  "Follow your session's setup guide before arriving.",
  "Run civ doctor and inspect the supplied warm-up recording.",
  "Open a supplied recording in a viewer, or check its signals with civ sample. Use the kit fallback material or pair with someone if blocked.",
];

export const notYourJob = [
  "Implementing MCAP parsing or ROS message discovery",
  "Synchronizing time or scheduling batch jobs",
  "Building provenance, clip generation or scoring",
  "Debugging containers or ROS installations",
  "Shipping a dashboard or training a model",
];
