import "server-only";

export const ORGANIZER_PACK_MARKER = "JURY-PACK-INTERNAL";

export const coachProtocol = [
  "Ask two questions first: What do you have? What do you think is happening? Then respond to the participant's hypothesis, not their code.",
  "Guide toward a next observation. Never provide a threshold, EventSpec, handedness answer, private solution, or sealed-evaluation fact during the session.",
  "Card side A means environment trouble: timebox diagnosis to ten minutes, then pair the participant so the reasoning work continues.",
  "Card side B means data or reasoning trouble: inspect the last artifact, ask for the current hypothesis, suggest one discriminating check, then leave them to run it.",
  "If the same gap affects the room, advance the live page once for everyone. Never give one desk future guidance privately.",
  "Use only participant-contract vocabulary: bag, topic, field, EventSpec, detector, normalized event, evidence clip, and run manifest.",
] as const;

export const sweepProtocol = [
  "Assign 2–3 coaches before opening. With two coaches, sweep every other checkpoint; with three, sweep every checkpoint.",
  "During a sweep, glance for card state and visible progress without interrupting. Route side A before side B.",
  "Record only team identifier, checkpoint, side A/B, minutes spent, pairing action, and coach initials. Do not copy participant content or personal data.",
  "Log any desk receiving material help. The log is a jury conflict input, not a participant-performance record.",
  "At 40+ participants, add coaches or keep every-other-checkpoint sweeps. At 10–15, keep the same protocol and allow near-continuous coverage.",
] as const;

export const troubleshooting = [
  ["Container engine unavailable", "Check Docker Desktop/WSL2 once. If virtualization is disabled or the ten-minute limit expires, pair immediately and continue from the partner's environment."],
  ["Image or dependencies missing", "Use the tracked offline image/archive input. Never download an unpinned replacement or alter the participant contract on the day."],
  ["Disk space insufficient", "Remove only disposable local runtime state with the participant's consent; otherwise pair. Never delete recordings, working evidence, or submissions."],
  ["Recording path or mount fails", "Confirm the path literally, then use the documented Windows/WSL2 mount form. Do not copy the recording into the repository."],
  ["Viewer cannot display", "Continue with civ inspect, sample, and tracked fallback tables/layouts. Viewer state is optional runtime input, not submission content."],
  ["Schema or topic mismatch", "Run civ doctor and civ inspect against the named participant product. If the product hash differs, replace it from tracked event media; do not patch the spec with private knowledge."],
  ["Internet or hosted page lost", "Hand out the static participant export from event media. Keep the same beat, expectation, hint, and tip; coaches become the distribution channel."],
  ["Historical form outage fallback", "The former event route accepted the unchanged metadata-only ZIP by local or USB intake and recorded team identity, dataset, organizer receipt time, SHA-256, and reference. It is retired for this event. No collection route or recipient is active. The CLI validator and receipt rules remain available for a future authorized workflow."],
  ["Future authorized intake: invalid or incomplete", "Return the exact validation failure. Keep the receipt as rejected and ask for a corrected resubmission; never repair participant artifacts."],
  ["Future authorized intake: duplicate, replacement, or late receipt", "Duplicate hash: retain one reference. Later valid on-time hash for the same team and dataset: replace authority. Late: quarantine and never replace an on-time authority."],
] as const;

export const juryCategories = [
  {
    name: "Investigation and hypothesis",
    headings: "Report headings 1–3; detector/EventSpec; events.jsonl; run manifest",
    anchors: [
      [0, "No testable question, no named signals, and no artifact-supported transfer claim."],
      [5, "A question exists, but the hypothesis or signal choice is generic and the transfer statement is unsupported by the submitted artifacts."],
      [10, "A specific hypothesis names relevant signals and the transfer claim identifies one concrete stable element and one changed binding or assumption."],
      [15, "The hypothesis is discriminating, limitations are explicit, and every transfer claim is traceable to the EventSpec, normalized events, metrics, or manifest."],
    ],
  },
  {
    name: "Quality and evaluation",
    headings: "Report headings 3–4; events.jsonl; metrics.json; run manifest",
    anchors: [
      [0, "No evaluable failure or change is identified, or the claimed result contradicts the submitted artifacts."],
      [5, "A failure is named but not tied to a normalized event/metric, or the resulting change is merely asserted."],
      [10, "One real failure is tied to a submitted artifact and leads to a specific, plausible change whose limitation is acknowledged."],
      [15, "The submission distinguishes defect, assumption, and transfer effect; the resulting change is artifact-supported and evaluated without overstating causality."],
    ],
  },
  {
    name: "Visualization and explanation",
    headings: "The single submitted figure; report headings 2–5; events.jsonl",
    anchors: [
      [0, "The figure is absent/unreadable or makes a claim that cannot be matched to the submission."],
      [5, "The figure is legible but decorative, weakly labelled, or disconnected from the event/failure discussed in the report."],
      [10, "The figure marks the relevant interval, names signals/units, and supports one report claim with a clear downstream action."],
      [15, "The figure makes event, context, failure, and uncertainty inspectable at a glance; explanation stays precise without relying on prose polish."],
    ],
  },
] as const;

export const bonusCategories = [
  ["Grounded agent trace", 10, "Award only when claims point to executed tools and produced artifacts in the accepted v2 extension. Prompt style, transcript length, confidence, and model choice earn nothing."],
  ["Advanced method", 5, "Award for a defensible multimodal, data-quality, or external-resource method. The resources plus min_distance_to exercise belongs here."],
  ["Failure-derived regression test", 5, "Award only when the accepted inert test encodes a demonstrated failure and a check that would catch its return."],
  ["Cave encounter replay", 10, "Automatic only: weighted mean recording F1 times 10, with the common temporal matcher. Empty recordings share at most 10% of its weight. No manual or Evidence award is required."],
] as const;

export const juryProcedure = [
  "Freeze the accepted ZIP/hash and automatic score first. The jury never changes submission authority or automatic Detection and Cave points. Organizers or agents separately review Evidence and Reproducibility, 15 points each, using docs/reference/scoring.md.",
  "Give both agents the same accepted metadata-only bundle, machine-score summary, anchors, and output schema. Do not provide sealed labels, coach logs, participant identity, or the other agent's output.",
  "Each agent scores all three categories and all three optional bonuses independently, citing an accepted artifact path plus a verifiable observation for every non-zero award and every deduction.",
  "Do not reward fluency, formatting beyond the contract, length, confidence, prompt craft, or inferred intent. If an artifact does not support a claim, score the artifact—not the prose.",
  "Agreement stands when category scores differ by at most 5 points and jury totals differ by at most 5. Any larger delta, any factual contradiction, or any invalid citation routes to human arbitration.",
  "The human records the disputed anchor, both cited observations, the ruling, and initials. Never average away a disagreement.",
  "If the human materially coached that team, route arbitration to the independent organizer/T-Lab owner. If none is available, disclose the conflict and use the lower supported score.",
  "Retain both raw agent outputs, the arbitration record, final per-category score, feedback, accepted bundle hash, receipt reference/time, machine-score record, and rubric version as the score trace.",
] as const;

export const feedbackTemplate = [
  "Entry and accepted bundle SHA-256:",
  "Machine score: Detection __/25 (Kashiwa __/15, Reims __/10); Evidence __/15; Reproducibility __/15.",
  "Jury score: Investigation __/15; Quality __/15; Visualization __/15.",
  "Bonus: Grounded agent trace __/10; advanced method __/5; failure-derived regression test __/5.",
  "What the artifacts support:",
  "Strongest next improvement:",
  "Disagreement/arbitration note (or none):",
  "Evidence __/15; Reproducibility __/15; automatic Cave bonus __/10. Final total __/130. This feedback does not change submission authority.",
] as const;

export const afternoonRun = [
  ["13:15", "Agents flag five worth-showing candidates independently of rank, including more than one honest/instructive failure candidate."],
  ["13:30", "Human confirms scores, skims every feedback sheet, resolves conflicts, and asks walkthrough consent privately. A decline is accepted without negotiation."],
  ["14:30–14:38", "Reveal the leaderboard and explain 25 automatic Detection / 30 manual technical / 45 jury / 20 existing bonus / 10 automatic Cave bonus, the two-agent process, human arbitration, score distribution, signal choices, and how transfer moved ranking."],
  ["14:38–14:54", "Organizer narrates roughly four submitted artifacts—EventSpec, report heading 3 or 4, and the figure. Participants remain seated; recognitions ride on the walkthroughs."],
  ["14:54–14:57", "Deliver the extension lesson in three minutes: external knowledge entered through a declared resource and found events the recording alone could not name."],
  ["14:57–15:00", "Close, hand every entry its reviewed written feedback, and release nothing whose consent or post-event gate is missing."],
] as const;

export const consentWording =
  "We would like to show your submitted artifacts because the dead end you documented is unusually useful to the room. The organizer will narrate it; you will not present or answer questions. May we show it? No is completely fine.";

export const coachChecklist = [
  "Ask what the participant observed and what they think is happening.",
  "Suggest one check they can perform. Do not supply a solution or private evaluation facts.",
  "Timebox tooling diagnosis to ten minutes, then use the approved fallback or pairing procedure.",
  "Give the room equal access to released guidance. Record material help using the existing minimal log.",
] as const;

export const juryChecklist = [
  "Confirm the accepted bundle and machine-score record.",
  "Apply the existing rubric to accepted artifacts. Cite the evidence for awards and deductions.",
  "Follow the existing independent-review and human-arbitration procedure.",
  "Record the final category scores and written feedback.",
] as const;
