export type SessionStage = {
  id: string;
  time: string;
  beat: string;
  title: string;
  action: string;
  shouldHave: string;
  ifYouDont: string;
  guidance: readonly string[];
  reportPrompt?: string;
};

function tokyoTimestamp(hours: number, minutes: number): number {
  return Date.UTC(2026, 8, 3, hours - 9, minutes);
}

export const SESSION_STAGE_IDS = [
  "opening",
  "b1",
  "b2",
  "b3",
  "b4",
  "b5",
  "b6",
  "b7",
  "close",
] as const;

const START_TIMES = [
  tokyoTimestamp(9, 30),
  tokyoTimestamp(10, 0),
  tokyoTimestamp(10, 20),
  tokyoTimestamp(10, 40),
  tokyoTimestamp(11, 0),
  tokyoTimestamp(11, 25),
  tokyoTimestamp(11, 45),
  tokyoTimestamp(12, 10),
  tokyoTimestamp(12, 30),
] as const;

export function scheduleIndexAt(nowMs: number): number {
  let index = 0;
  for (let candidate = 1; candidate < START_TIMES.length; candidate += 1) {
    if (nowMs < START_TIMES[candidate]) {
      break;
    }
    index = candidate;
  }
  return index;
}

export function effectiveStageIndex(nowMs: number, coachFloorIndex: number): number {
  return Math.min(
    SESSION_STAGE_IDS.length - 1,
    Math.max(scheduleIndexAt(nowMs), coachFloorIndex),
  );
}

export function countdownSecondsAt(nowMs: number, effectiveIndex: number): number | null {
  const nextStart = START_TIMES[effectiveIndex + 1];
  if (nextStart === undefined) {
    return null;
  }
  return Math.max(0, Math.ceil((nextStart - nowMs) / 1_000));
}

export function nextStageStartAt(effectiveIndex: number): number | null {
  return START_TIMES[effectiveIndex + 1] ?? null;
}

export type CoachState = {
  readonly floorIndex: number;
  readonly appliedRequestIds: readonly string[];
};

export type CoachAdvanceResult = {
  readonly outcome: "advanced" | "already-applied" | "stale" | "closed";
  readonly state: CoachState;
};

export function createCoachState(): CoachState {
  return { floorIndex: 0, appliedRequestIds: [] };
}

export function advanceCoachState(
  state: CoachState,
  command: {
    readonly requestId: string;
    readonly observedStageIndex: number;
    readonly scheduledStageIndex: number;
  },
): CoachAdvanceResult {
  if (state.appliedRequestIds.includes(command.requestId)) {
    return { outcome: "already-applied", state };
  }
  const currentIndex = Math.max(state.floorIndex, command.scheduledStageIndex);
  if (command.observedStageIndex !== currentIndex) {
    return { outcome: "stale", state };
  }
  if (currentIndex >= SESSION_STAGE_IDS.length - 1) {
    return { outcome: "closed", state };
  }
  return {
    outcome: "advanced",
    state: {
      floorIndex: currentIndex + 1,
      appliedRequestIds: [...state.appliedRequestIds, command.requestId],
    },
  };
}

export type LivePublicSnapshot = {
  readonly nowMs: number;
  readonly stageIndex: number;
  readonly stage: SessionStage;
  readonly unlockedGuidance: readonly string[];
  readonly nextStartMs: number | null;
  readonly advancedEarly: boolean;
};
