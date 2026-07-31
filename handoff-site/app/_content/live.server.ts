/**
 * Placeholder content for the day's live page.
 *
 * NOT part of the production artifact — this module is imported only by
 * `app/live/page.tsx`, which exists outside `public-source/`. It carries what
 * unlocks when, so an organizer can project themselves into the session and see
 * what participants are expected to be doing with the recordings at any minute.
 *
 * The real page replaces this: it unlocks on a schedule, is served over
 * Tailscale Funnel on the morning, and exports statically to the SSDs. This is
 * a flat preview of every state at once.
 */

export const status =
  "Placeholder. The real page unlocks section by section on the day; this shows every state at once so the shape can be judged before it is built.";

export const rules = [
  "Unlocks run automatically on the schedule below. A room where every organizer is busy still gets its material.",
  "Any coach may release the next step early, for everyone at once. Nobody may hold one back.",
  "Participants never unlock anything themselves — the arc depends on the tedium landing before the tool arrives.",
  "Worked solutions publish after the event. During the session the ladder stops at tips.",
  "Nothing here ever resolves which way the manoeuvre goes. That is the whole transfer test.",
];

export type Step = {
  time: string;
  beat?: string;
  stage: string;
  /** What the participant is doing with the recordings, in plain terms. */
  onTheData: string;
  shouldHave: string;
  ifYouDont: string;
  unlocks: string;
};

export const steps: Step[] = [
  {
    time: "09:30",
    stage: "Briefing",
    onTheData: "Nothing yet. Container starting in the background.",
    shouldHave: "Where things are, what to do if you get lost, and that waiting for a hint is fine.",
    ifYouDont: "—",
    unlocks: "The page itself.",
  },
  {
    time: "09:35",
    stage: "By hand",
    onTheData:
      "Reading a printed trace of the warm-up route by eye. No laptop involved, so a broken container costs nothing here.",
    shouldHave: "Intervals marked in pen — start and end of every occurrence you can see.",
    ifYouDont: "Mark any one. Precision is not the lesson yet.",
    unlocks: "—",
  },
  {
    time: "09:45",
    stage: "Compare",
    onTheData:
      "Two people's marks side by side on the same window. They will differ at the edges — that is the point, and it is why matching needs a tolerance rather than an exact timestamp.",
    shouldHave: "A disagreement with your neighbour about where an occurrence starts.",
    ifYouDont: "Ask someone two seats away instead.",
    unlocks: "—",
  },
  {
    time: "09:50",
    stage: "Check",
    onTheData: "First contact with the real recording: decode it, list its topics, confirm it opens.",
    shouldHave: "`civ doctor && civ inspect <warm-up>` passed, and the page open.",
    ifYouDont: "Card stays up. A coach comes to you. Ten minutes, then pair up with a neighbour.",
    unlocks: "—",
  },
  {
    time: "10:00",
    beat: "B1",
    stage: "Formalize",
    onTheData:
      "Plotting one or two signals from the warm-up route and finding a condition that lines up with what you marked in pen.",
    shouldHave: "A first run of the detector on the warm-up route.",
    ifYouDont: "Run the shipped example spec unchanged and look at what comes out.",
    unlocks: "Formalize: what is expected, plus hints.",
  },
  {
    time: "10:20",
    beat: "B2",
    stage: "Formalize",
    onTheData:
      "Watching a naive threshold fire on every sample it is true for, then collapsing those samples into intervals.",
    shouldHave: "A condition that fires at all — even a bad one.",
    ifYouDont: "Loosen the threshold until it fires, then tighten it.",
    unlocks: "Formalize: tips.",
  },
  {
    time: "10:40",
    beat: "B3",
    stage: "Scale",
    onTheData:
      "Running the same detector across several practice routes and opening the one result that is obviously wrong.",
    shouldHave: "Events across more than one route, and one failure you can name.",
    ifYouDont: "Run one route and move on — batching is not the lesson. Write report headings 1 and 2 now.",
    unlocks: "Scale: hints and tips.",
  },
  {
    time: "11:00",
    beat: "B4",
    stage: "Transfer",
    onTheData:
      "Opening the second recording for the first time. Different vehicle, different sensors, no vehicle bus — the equivalents of what you used exist but have to be derived.",
    shouldHave: "A detector on the first recording you are willing to stop improving, submitted once.",
    ifYouDont:
      "Stop improving it anyway. Submit what you have and open the second recording — the transfer hints are open now, and a coach will work through it with you.",
    unlocks: "Transfer: what is expected, plus hints — pulled forward to land exactly here.",
  },
  {
    time: "11:25",
    beat: "B5",
    stage: "Transfer",
    onTheData:
      "Finding rotation rate and forward speed on a stack that publishes neither directly, at sample rates an order of magnitude apart.",
    shouldHave: "The second stack's signals identified, and a condition that fires.",
    ifYouDont: "The signal equivalents are in the hints. The manoeuvre itself is yours.",
    unlocks: "Transfer: tips.",
  },
  {
    time: "11:45",
    beat: "B6",
    stage: "Challenge",
    onTheData:
      "Comparing what your two detectors found, and being specific about which part of your reasoning survived the move and which did not.",
    shouldHave: "Events on the second recording, however imperfect.",
    ifYouDont: "Take what you have. Write headings 3 and 4 now, while the transfer is fresh.",
    unlocks: "—",
  },
  {
    time: "12:10",
    beat: "B7",
    stage: "Submit",
    onTheData: "Rerunning from a clean state to prove the result is not an accident of your shell history.",
    shouldHave: "A submission already accepted — and be improving it.",
    ifYouDont: "Submit an incomplete one now. You can submit again. Write heading 5.",
    unlocks: "—",
  },
  {
    time: "12:30",
    stage: "Close",
    onTheData: "Hands off the recordings.",
    shouldHave: "Your last submission counts. The deadline is hard.",
    ifYouDont: "—",
    unlocks: "The extension exercise, which stays available afterwards.",
  },
];

/** What an organizer still has to build behind this preview. */
export const stillToBuild = [
  "Author roughly twenty units — per-stage expectation, hints, tips — plus the solutions that publish afterwards.",
  "Timed unlock, with a control that lets any coach advance the schedule.",
  "A visible countdown to the next unlock, for the room's shared screen.",
  "A static export for the SSDs, which is both the internet-down path and the public artifact afterwards.",
  "One decision outstanding: which example the sample-versus-interval unit demonstrates on.",
];
