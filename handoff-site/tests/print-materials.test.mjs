import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { fileURLToPath } from "node:url";

async function material(name) {
  return readFile(fileURLToPath(new URL(`../dist/client/desk/${name}`, import.meta.url)), "utf8");
}

const FORBIDDEN = /<script|organizer path|sealed|ground truth|answer interval|right turn|left turn|cheat sheet|pace card/i;

test("warm-up trace is a one-page real participant-safe A4 print", async () => {
  const body = await material("warmup-trace.html");
  assert.match(body, /@page\s*\{\s*size:\s*A4 landscape/i);
  assert.match(body, /data-print-material="signal-trace" data-pages="1"/);
  assert.match(body, /KSH-64ac27cd029b-signals\.mcap/);
  assert.match(body, /real decimated longitudinal acceleration signal/i);
  const points = body.match(/<polyline[^>]+points="([^"]+)"/i)?.[1].trim().split(/\s+/);
  assert.ok(points && points.length >= 80, "expected at least 80 real trace points");
  assert.doesNotMatch(body, FORBIDDEN);
});

test("help card is exactly two A5 sides with the settled protocol", async () => {
  const body = await material("help-card.html");
  assert.match(body, /@page\s*\{\s*size:\s*A5 landscape/i);
  assert.match(body, /data-print-material="help-card" data-pages="2"/);
  assert.equal((body.match(/<section class="side /g) ?? []).length, 2);
  assert.match(body, /civ doctor/);
  assert.match(body, /civ inspect/);
  assert.match(body, /What have you got so far\?/);
  assert.match(body, /What do you think is happening\?/);
  assert.doesNotMatch(body, FORBIDDEN);
});

test("brief is one A4 page with the full participant contract", async () => {
  const body = await material("brief.html");
  assert.match(body, /@page\s*\{\s*size:\s*A4 portrait/i);
  assert.match(body, /data-print-material="participant-brief" data-pages="1"/);
  assert.match(body, /first set 15 \/ transfer 10/i);
  assert.match(body, /Solo and duo entries share one leaderboard/i);
  assert.match(body, /HARD CLOSE[\s\S]*12:30 JST/i);
  assert.match(body, /last valid on-time receipt is authoritative/i);
  assert.match(body, /AI agents score.*human-written anchors.*human arbitrates/is);
  assert.match(body, /Everyone receives written feedback at 15:00/i);
  assert.match(body, /Winners are published only with consent/i);
  assert.match(body, /scored runner constrains executable evidence, not what you may write/i);
  assert.match(body, /ONE RENDERED PAGE · ONE FIGURE/i);
  assert.match(body, /grounded trace \+10.*advanced method \+5.*regression test \+5/is);
  assert.match(body, /v2 ZIP keeps seven core artifacts/i);
  assert.doesNotMatch(body, FORBIDDEN);
});
