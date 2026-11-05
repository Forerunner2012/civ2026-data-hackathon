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
    expectation: "Your marks will differ at the edges; that disagreement is evidence about the contract you need.",
    hint: "Describe what changed in the trace before naming a threshold or writing code.",
    tip: "Keep one rough interval and one edge disagreement to compare with the runner later.",
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
    expectation: "A useful first condition fires on observable data and is allowed to be visibly imperfect.",
    hint: "Run `civ detect examples/kashiwa/deceleration_timing.yaml data/KSH-64ac27cd029b-signals.mcap --dry-run` unchanged first.",
    tip: "Change one declared value at a time, then keep the result that taught you something.",
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
    expectation: "Matching samples are candidates; the timing contract turns consecutive candidates into reviewable events.",
    hint: "Run the accepted warm-up example with `--dry-run`, then compare its candidate and event counts.",
    tip: "The reference run is 189 matching samples → 14 merged candidates → 4 events. One event has zero brake response, so timing fixes the count, not the meaning.",
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
    expectation: "Scaling should expose a named failure, not merely produce more intervals.",
    hint: "Open the worst interval from a second practice route and classify the failure before editing the condition.",
    tip: "Keep the bad clip and write the change it caused under report headings 1 and 2.",
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
      "Keep the warm-up result in your working directory, open the second recording, and inventory the signal equivalents needed by the same workflow.",
    shouldHave:
      "A warm-up result available locally, detector work paused, and the second recording open.",
    ifYouDont:
      "Keep the work you have, open the second recording, and use the transfer expectation and hints unlocked so far.",
    expectation: "The workflow and artifact shapes transfer; physical bindings and evidence may not.",
    hint: "Inventory fields and units on the second stack before looking for topic-name similarity.",
    tip: "Look for equivalent motion evidence across unlike topics and coordinate frames. Do not assume the first stack's names or signs survive.",
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
    expectation: "A shared physical quantity can be derived from unlike sensor representations without making the decision for you.",
    hint: "Check frames, units, and sampling rates before composing the second condition.",
    tip: "When axes are expressed in a world frame, test a magnitude as a transferable feature and inspect its limitations.",
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
    expectation: "A defensible transfer result separates the stable contract from the values and assumptions that changed.",
    hint: "Put one event from each recording side by side and finish the sentence: ‘This transferred, but this did not.’",
    tip: "Use that contrast for report headings 3 and 4; a visible failure plus a reasoned change is valid evidence.",
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
    title: "Rerun clean and validate locally",
    action: "Reproduce from a clean working directory, finish the report, build the metadata-only ZIP, and keep it and its SHA-256 locally.",
    shouldHave: "A locally validated metadata-only ZIP, its SHA-256, and the final report.",
    ifYouDont: "Write heading 5, run `civ report` on your current work, and keep the validated metadata-only ZIP and SHA-256 locally.",
    expectation: "The final claim is reproducible from pinned inputs and ends with an operational next action.",
    hint: "Rerun from a clean working directory, finish heading 5, run `civ report`, and keep its ZIP and printed SHA-256 locally.",
    tip: "Include one figure and rerun `civ report` after any final edit. Keep the validated ZIP and its printed hash locally.",
    guidance: [
      "Run `civ report` after your final edit, then keep the validated ZIP and its SHA-256 locally.",
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
      "At the 12:30 boundary, stop work on the recordings and keep the locally validated metadata-only ZIP and its SHA-256.",
    shouldHave: "A validated local ZIP, its SHA-256, and local evidence preserved together.",
    ifYouDont:
      "Keep your local work. The room has moved to lunch scoring and no solution is published here.",
    expectation: "The validated local ZIP preserves your reproducible work and next action.",
    hint: "Keep the validated ZIP and its SHA-256 with your local evidence for your own reference.",
    tip: "Worked approaches remain separately controlled until their post-event release is approved.",
    guidance: [
      "The participant page remains a record of the session state.",
      "Results and selected walkthroughs happen after lunch; worked answers are not an in-session unlock.",
    ],
  },
] as const satisfies readonly SessionStage[];
