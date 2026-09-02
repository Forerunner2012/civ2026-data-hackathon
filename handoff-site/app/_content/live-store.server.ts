import "server-only";

import { SESSION_STAGES } from "./live-content.server";
import {
  advanceCoachState,
  createCoachState,
  effectiveStageIndex,
  nextStageStartAt,
  scheduleIndexAt,
  type CoachAdvanceResult,
  type LivePublicSnapshot,
} from "./live-state";

let coachState = createCoachState();

export function clockFromValue(value: string | null | undefined): number {
  if (!value) {
    return Date.now();
  }
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) {
    throw new Error("now must be an ISO-8601 timestamp");
  }
  return parsed;
}

export function requestClockFromValue(value: string | null | undefined): number {
  return process.env.LIVE_ALLOW_CONTROLLED_CLOCK === "true"
    ? clockFromValue(value)
    : Date.now();
}

export function liveSnapshotAt(nowMs: number): LivePublicSnapshot {
  const scheduledIndex = scheduleIndexAt(nowMs);
  const stageIndex = effectiveStageIndex(nowMs, coachState.floorIndex);
  return {
    nowMs,
    stageIndex,
    stage: SESSION_STAGES[stageIndex],
    unlockedGuidance: SESSION_STAGES.slice(0, stageIndex + 1).flatMap((stage) => stage.guidance),
    nextStartMs: nextStageStartAt(stageIndex),
    advancedEarly: stageIndex > scheduledIndex,
  };
}

export function advanceLiveStage(
  nowMs: number,
  requestId: string,
  observedStageId: string,
): LivePublicSnapshot & { outcome: CoachAdvanceResult["outcome"] } {
  const observedStageIndex = SESSION_STAGES.findIndex((stage) => stage.id === observedStageId);
  if (observedStageIndex < 0) {
    throw new Error("observedStageId is not a session stage");
  }
  const result = advanceCoachState(coachState, {
    requestId,
    observedStageIndex,
    scheduledStageIndex: scheduleIndexAt(nowMs),
  });
  coachState = result.state;
  return { ...liveSnapshotAt(nowMs), outcome: result.outcome };
}
