import "server-only";

import type { SessionStage } from "./live-state";

export const SESSION_STAGES = [
  {
    id: "opening",
    time: "09:30",
    beat: "OPENING",
    title: "Observe before you automate",
    action:
      "Mark one interval by eye, compare its edges with another participant, then confirm the warm-up recording opens.",
    shouldHave: "One marked interval, the session page open, and a successful recording inventory.",
    ifYouDont:
      "Mark any one interval. If the recording still will not open after ten minutes, pair with a neighbour and keep reasoning.",
    guidance: [
      "The first boundary is allowed to be rough; disagreement is evidence, not failure.",
      "Keep the raw recording local. Your eventual submission is metadata only.",
    ],
  },
  {
    id: "b1",
    time: "10:00",
    beat: "B1",
    title: "Formalize one observable condition",
    action:
      "Choose one or two signals, write a first EventSpec condition, and run it on the warm-up recording.",
    shouldHave: "A first detector run, even if its intervals are visibly imperfect.",
    ifYouDont:
      "Run the shipped example unchanged, inspect the normalized intervals, and change only one thing next.",
    guidance: [
      "Start with a condition that fires. Precision comes after a visible result.",
      "Treat field names, units, and sample rates as evidence you can write down.",
    ],
  },
  {
    id: "b2",
    time: "10:20",
    beat: "B2",
    title: "Turn samples into intervals",
    action:
      "Use the shared timing fields to collapse consecutive matching samples into reviewable events.",
    shouldHave: "A condition that fires and at least one normalized interval you can open.",
    ifYouDont: "Loosen one condition value until it fires, then tighten it against the evidence clip.",
    guidance: [
      "A detector emits intervals, not one event per matching sample.",
      "Review starts, ends, duplicates, and gaps separately; they fail for different reasons.",
    ],
  },
  {
    id: "b3",
    time: "10:40",
    beat: "B3",
    title: "Scale just far enough to expose a failure",
    action: "Run the same detector on more than one practice route and open the worst result.",
    shouldHave: "Events from more than one route and one failure you can name precisely.",
    ifYouDont: "Run one route and move on; batching is provided. Write report headings 1 and 2 now.",
    guidance: [
      "Name the failure before changing the condition: false positive, miss, boundary, duplicate, or data gap.",
      "Keep one bad clip. Your report needs the change it caused, not a perfect origin story.",
    ],
    reportPrompt: "Write report headings 1 and 2 now: question/hypothesis, then signals and limits.",
  },
  {
    id: "b4",
    time: "11:00",
    beat: "B4",
    title: "Transfer the contract, not the first detector",
    action:
      "Submit the warm-up result once, open the second recording, and inventory the signal equivalents needed by the same workflow.",
    shouldHave:
      "A warm-up detector you have stopped polishing, one accepted submission, and the second recording open.",
    ifYouDont:
      "Stop polishing anyway. Submit what you have, open the second recording, and use the transfer expectation and hints unlocked so far.",
    guidance: [
      "Transfer expectation: keep the command and candidate artifact shapes; change only the real bindings, required derivation, condition values, and evidence topics.",
      "Compare the second stack's field inventory and units. Look for rotational motion and translational motion without reusing first-stack topic names.",
    ],
  },
  {
    id: "b5",
    time: "11:25",
    beat: "B5",
    title: "Make unlike sensors comparable",
    action:
      "Express the second stack's motion evidence in the shared condition and inspect the intervals it produces.",
    shouldHave: "The second stack's signals identified and a condition that fires.",
    ifYouDont:
      "Use the inventory and units to build a motion magnitude first. Keep the manoeuvre decision in your own evidence.",
    guidance: [
      "When velocity axes belong to a world frame, a magnitude is often more transferable than one axis.",
      "Different sample rates are expected; the runner carries the latest declared signal values.",
    ],
  },
  {
    id: "b6",
    time: "11:45",
    beat: "B6",
    title: "Compare what transferred",
    action:
      "Put the two results side by side and state which assumption survived the sensor change and which did not.",
    shouldHave: "Second-recording events, however imperfect, and one concrete transfer claim.",
    ifYouDont: "Use the events you have. Write report headings 3 and 4 while the contrast is fresh.",
    guidance: [
      "Separate a contract that transferred from a condition value that did not.",
      "A visible failure with a defensible change is stronger than an unexplained clean chart.",
    ],
    reportPrompt: "Write report headings 3 and 4 now: transfer, then one failure and its change.",
  },
  {
    id: "b7",
    time: "12:10",
    beat: "B7",
    title: "Rerun clean and submit",
    action: "Reproduce from a clean working directory, check the bundle hash, and submit again.",
    shouldHave: "A submission already accepted and a final rerun in progress.",
    ifYouDont: "Submit an incomplete valid bundle now. You may submit again before close. Write heading 5.",
    guidance: [
      "Your last on-time valid submission is authoritative; resubmission is expected.",
      "Evidence clips and organizer labels never belong in the metadata bundle.",
    ],
    reportPrompt: "Write heading 5 now: downstream action and deployment mode.",
  },
  {
    id: "close",
    time: "12:30",
    beat: "CLOSE",
    title: "Submissions closed",
    action:
      "Stop work on the recordings. Late receipts are retained separately and do not replace an on-time submission.",
    shouldHave: "A final receipt and the bundle hash you submitted.",
    ifYouDont:
      "Keep your local work. The room has moved to lunch scoring and no solution is published here.",
    guidance: [
      "The participant page remains a record of the session state.",
      "Results and selected walkthroughs happen after lunch; worked answers are not an in-session unlock.",
    ],
  },
] as const satisfies readonly SessionStage[];
