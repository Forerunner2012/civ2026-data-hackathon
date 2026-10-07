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

export const participantIntroduction =
  "Investigate an incomplete report of vehicle behaviour. Inspect the recordings, write an EventSpec, and test your reasoning on a different recording. Check the evidence, explain one failure, and recommend a next action.";

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
    produces: "Nothing to build yet. Start your container while you listen.",
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
    doing: "Batch the detector across routes and inspect one failure you can name.",
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
    title: "Submit",
    doing: "Rerun reproduction, finish the one-page report, hand in.",
    produces: "An accepted submission — and you may keep improving it until 12:30.",
  },
];

/**
 * The page is the room's tempo. It says what you should be holding by now and,
 * more usefully, what to do if you are not.
 */
export const theDayPage = [
  "A page you keep open all session. It moves on a schedule; you do not have to watch it.",
  "At each step it states what you should have by now — and what to do if you do not.",
  "Hints and tips unlock as the session goes. Waiting for one is legitimate, not a confession.",
  "A coach can release the next hints early for the whole room, so help is never private.",
  "Worked solutions are published after the event, not during it.",
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
  "The answer key for two or three events, so you can see where an occurrence starts and ends",
  "A page that tells you what you should have by now, and what to do if you do not",
  "SSDs in the room carrying the container image and both recordings, if your download failed",
];

export const deliverables = [
  "The engineering question and your detection hypothesis",
  "The signals you used, what was missing, and what you judged unreliable",
  "An executable EventSpec or detector",
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
  "A development score validates submission format and basic metrics during the session.",
  "The final ranking runs on a held-back test set, so a detector tuned to one route will not travel.",
  "Submit as often as you like. The last one counts, and the deadline is hard at 12:30.",
  "Solo and duo entries share one leaderboard; the selected afternoon walkthroughs do not change the score.",
  "Ties break on the earliest submission of the tied score.",
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

export const commands = [
  { command: "civ doctor", note: "check your machine", output: "readiness only · no files" },
  { command: "civ inspect BAG", note: "topics, fields, durations", output: "inventory · no files" },
  { command: "civ sample BAG --topic ... --field ...", note: "inspect values", output: "timestamped values · no files" },
  { command: "civ submission-init working --shell ...", note: "create your workspace once", output: "detector + report + figure + reproduce templates" },
  { command: "civ detect SPEC DATASET --output working", note: "run your detector, --dry-run first", output: "detector/ (spec + exact resources) + events.jsonl + v2 run-manifest.json" },
  { command: "civ clip working/events.jsonl DATASET", note: "cut compact local evidence", output: "evidence/*.mcap + updated manifest" },
  { command: "civ score working --labels DEVELOPMENT_LABELS", note: "development score", output: "metrics.json + updated manifest" },
  { command: "civ report working", note: "validate and package", output: "submission.zip + printed SHA-256" },
];

export const viewerResources = [
  {
    tool: "PlotJuggler 3.999.3",
    platforms: "Windows amd64 · Linux amd64",
    project: "https://github.com/PlotJuggler/PlotJuggler",
    releases: "https://github.com/PlotJuggler/PlotJuggler/releases",
  },
  {
    tool: "Lichtblick 1.28.0",
    platforms: "Windows amd64 · Linux amd64 · macOS universal",
    project: "https://github.com/lichtblick-suite/lichtblick",
    releases: "https://github.com/lichtblick-suite/lichtblick/releases",
  },
];

export const participantProducts = [
  {
    dataset: "Kashiwa warm-up",
    product: "data/KSH-64ac27cd029b-signals.mcap",
    plotJugglerLayout: "layouts/kashiwa-right-turn.pj4.xml",
    lichtblickLayout: "layouts/lichtblick-kashiwa-right-turn.json",
    inventory: "steering angle, vehicle speed, vehicle error code, object-detected flag",
  },
  {
    dataset: "Reims development chunk 0",
    product: "data/RMS-CHUNK-0-0a0817b3afc8-signals.mcap",
    plotJugglerLayout: "layouts/reims-left-turn.pj4.xml",
    lichtblickLayout: "layouts/lichtblick-reims-left-turn.json",
    inventory: "IMU yaw rate and linear velocity x, y, z",
  },
];

export const deskMaterials = [
  { href: "/desk/warmup-trace.html", title: "Printed signal trace", note: "One write-on A4 sheet for the analogue warm-up." },
  { href: "/desk/help-card.html", title: "Two-sided help card", note: "Print double-sided; raise it when you need a coach." },
  { href: "/desk/brief.html", title: "One-page brief", note: "The session contract, report shape, deadline, and scoring rules." },
];

/**
 * You keep your evidence. What is handed in is the record of the work, not the
 * recordings behind it — kilobytes, through a form.
 */
export const submissionTree = `working/                       handed in?
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
  "Start once with `civ submission-init working --shell powershell` (or `--shell posix`). The workspace is deliberately incomplete and is never an answer.",
  "Replace every template prompt, run the stable detect → clip → score path, and keep exactly one reproduction script plus one marked figure.",
  "Run `civ report working`. It validates the metadata shape and prints the SHA-256 of the unchanged `submission.zip`.",
  "Optional traces and regression tests are inert: intake validates but never runs them.",
  "Submit the unchanged ZIP, printed hash, and the same participant or team identity. Keep the confirmation reference; its server receipt time is authoritative.",
  "If the form is unavailable, hand over those same three items by USB. Never unpack, rename, recompress, or add recordings or clips.",
];

export const submissionOutcomes = [
  { state: "Accepted", action: "Keep the reference, hash, and receipt time. You may continue working." },
  { state: "Replaced", action: "A later valid on-time bundle for the same dataset is authoritative; keep both receipts." },
  { state: "Incomplete or invalid", action: "Read the `civ report` diagnostic, fix the named artifact, rebuild, and submit again." },
  { state: "Hash mismatch", action: "Upload the unchanged ZIP and paste the exact hash printed by the same report run." },
  { state: "Duplicate reference", action: "The existing receipt stands. Use a new form response only for a newly built bundle." },
  { state: "Late", action: "The receipt is retained as late and cannot replace your last valid on-time bundle." },
];

/**
 * The optional extension branch. Scored under the existing bonus, never scheduled, and
 * deliberately carries no zone coordinates — sourcing them is the exercise.
 */
export const extensionTrack = {
  lesson:
    "The system used knowledge that was never in the bag to find events it could not otherwise have found.",
  placement: [
    "This branch is open and scored before 12:30, and it receives no time in the run of show. Nothing in the three hours is planned around it.",
    "If your core submission is not accepted yet, do the core. Bonus points cannot rescue a result that does not reproduce.",
    "It stays on this page after the event, and it runs on the same products you keep. Do it at lunch, on the plane, or in six months.",
  ],
  steps: [
    "Choose a class of places the recording never knew about. The worked case is the champagne cellars along the Reims route.",
    "Write a `civ.point-resource/v1` file: an id, a latitude and a longitude per point. That is the entire contract.",
    "Reference it from an EventSpec under `resources:`, derive `min_distance_to` from your GNSS latitude and longitude signals, and put that distance in the condition. The shipped `examples/reims/cave-encounter.yaml` is a complete worked spec with illustrative points — the shape is real, the coordinates are not.",
    "Run it across the Reims development products with the same `civ detect` you already use. It copies each declared resource byte-for-byte beside the bundled EventSpec and declares it in `extension/manifest.json`.",
    "Put a short provenance note under `extension/` and declare its kind, path, SHA-256, and media type in the sorted extension manifest.",
  ],
  provenance: [
    "How you source the points is deliberately unconstrained: a chat assistant, an OpenStreetMap query, a published directory, or twenty minutes with a map and a spreadsheet are all legitimate.",
    "No model is required, and nothing on the required path needs network access — only your own sourcing step might.",
    "There is no answer key here and nothing is diffed against a held-back list. What is judged is whether the zones are plausible, the predicate is sound, the evidence shows what you claim, and you can say where the knowledge came from.",
    "A 40 m radius is a sensible starting point on this route, and `timing.min_duration` is what suppresses a glancing hit. Expect a handful of encounters at most: this is a small exercise, not a hunt.",
  ],
  budget:
    "Budget 30–45 minutes, and expect almost all of it to be sourcing. The detection itself is seconds — one spec across all five Reims development products finishes in under ten seconds on the target machine.",
  scoredAs:
    "Maximum +20: grounded agent trace +10; advanced multimodal, data-quality, or external-resource method +5; regression test derived from a demonstrated failure +5. Every non-zero award cites a bundled artifact.",
};

export const comeReady = [
  "A laptop you can install software on, with room to spare: a container plus recordings needs disk and memory, not a GPU.",
  "Set up before you arrive: Docker, plus WSL2 on Windows. The kit ships as a container.",
  "Run `civ doctor && civ inspect <warm-up>` in the week before, open the day's page, and post what it prints. That is the whole readiness check.",
  "Support is asynchronous from two weeks out, with two live drop-ins about ten days before — deliberately before anyone starts travelling.",
  "Explore the recordings beforehand if you want to. It is allowed and encouraged; you are not stealing a march on anyone.",
  "Nothing to compile or download on the day. If your download failed, SSDs in the room carry the image and both recordings.",
  "No account, paid model or API key is required. The required path runs fully offline.",
  "Work solo or with one partner. Solo and duo entries share one leaderboard — and if your machine struggles, pairing up on the day is normal and expected.",
  "Everything runs in professional English.",
  "Bring experience with robotic or vehicular recordings; the challenge starts above the beginner floor.",
];

export const notYourJob = [
  "Implementing MCAP parsing or ROS message discovery",
  "Synchronizing time or scheduling batch jobs",
  "Building provenance, clip generation or scoring",
  "Debugging containers or ROS installations",
  "Shipping a dashboard or training a model",
];
