import "server-only";

export const solutionRelease = {
  status: "approved" as "awaiting-human-approval" | "approved",
  note: "Final public wording and all seven worked approaches approved by the organizer on 2026-08-29.",
} as const;

export const postEventSolutions = [
  {
    beat: "B1",
    title: "Start with one observable condition",
    approach:
      "Inspect the warm-up inventory, bind one longitudinal signal, and make a deliberately loose condition fire before tuning it. Preserve the first imperfect output as comparison evidence.",
  },
  {
    beat: "B2",
    title: "Separate samples, candidates, and events",
    approach:
      "Use the stable timing fields to join consecutive matching samples, bridge only short gaps, and reject fragments that are too short. In the accepted reference run, 189 matching samples become 14 merged candidates and 4 events. That count does not decide which event is meaningful.",
  },
  {
    beat: "B3",
    title: "Scale to find a named failure",
    approach:
      "Batch the same contract across development routes, open the worst interval, and classify the failure before changing one value. Keep the failed clip and record the change it caused.",
  },
  {
    beat: "B4",
    title: "Transfer the contract shape",
    approach:
      "Keep the command, EventSpec, normalized-event, evidence, and report shapes. Re-inventory the second stack and replace only the physical bindings, derivation, condition values, and evidence topics that the data requires.",
  },
  {
    beat: "B5",
    title: "Derive comparable motion evidence",
    approach:
      "Check coordinate frames and units, then derive a shared physical quantity from the available velocity and rotational signals. A vector magnitude can remove dependence on one world-frame axis, but its limitations still need inspection.",
  },
  {
    beat: "B6",
    title: "State what transferred",
    approach:
      "Compare one interval from each stack. Distinguish the stable event and artifact contract from sensor-specific bindings, values, rates, and failure modes. Report both the surviving assumption and the one that changed.",
  },
  {
    beat: "B7",
    title: "Reproduce and submit",
    approach:
      "Run the documented path from a clean working directory, verify the bundle hash, retain one marked figure, and finish the recommendation. Submit the metadata bundle again if the clean run changes it.",
  },
] as const;
