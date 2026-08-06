import assert from "node:assert/strict";
import test from "node:test";
import {
  SESSION_STAGE_IDS,
  advanceCoachState,
  countdownSecondsAt,
  createCoachState,
  effectiveStageIndex,
  scheduleIndexAt,
} from "../app/_content/live-state.ts";

function tokyo(time: string): number {
  return Date.parse(`2026-09-03T${time}:00+09:00`);
}

test("controlled clock crosses every opening, beat, and close boundary", () => {
  const boundaries = [
    ["09:30", "opening"],
    ["10:00", "b1"],
    ["10:20", "b2"],
    ["10:40", "b3"],
    ["11:00", "b4"],
    ["11:25", "b5"],
    ["11:45", "b6"],
    ["12:10", "b7"],
    ["12:30", "close"],
  ] as const;

  assert.deepEqual(SESSION_STAGE_IDS, boundaries.map(([, id]) => id));
  for (const [time, id] of boundaries) {
    assert.equal(SESSION_STAGE_IDS[scheduleIndexAt(tokyo(time))], id);
  }
  assert.equal(SESSION_STAGE_IDS[scheduleIndexAt(tokyo("10:39"))], "b2");
});

test("countdown follows the next not-yet-visible scheduled state", () => {
  const now = tokyo("10:05");
  assert.equal(countdownSecondsAt(now, effectiveStageIndex(now, 0)), 15 * 60);
  assert.equal(countdownSecondsAt(now, 2), 35 * 60);
  assert.equal(countdownSecondsAt(tokyo("12:30"), 8), null);
});

test("coach advance is monotonic, next-only, and idempotent by request id", () => {
  const initial = createCoachState();
  const first = advanceCoachState(initial, {
    requestId: "advance-b1-once",
    observedStageIndex: 1,
    scheduledStageIndex: 1,
  });
  assert.equal(first.outcome, "advanced");
  assert.equal(first.state.floorIndex, 2);

  const repeated = advanceCoachState(first.state, {
    requestId: "advance-b1-once",
    observedStageIndex: 1,
    scheduledStageIndex: 1,
  });
  assert.equal(repeated.outcome, "already-applied");
  assert.deepEqual(repeated.state, first.state);

  const stale = advanceCoachState(first.state, {
    requestId: "stale-screen",
    observedStageIndex: 1,
    scheduledStageIndex: 1,
  });
  assert.equal(stale.outcome, "stale");
  assert.equal(stale.state.floorIndex, 2);
});
