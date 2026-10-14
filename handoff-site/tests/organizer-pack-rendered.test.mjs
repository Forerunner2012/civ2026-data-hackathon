import assert from "node:assert/strict";
import test from "node:test";

let workerPromise;

function loadWorker() {
  workerPromise ??= import(new URL(`../dist/server/index.js?pack=${process.pid}-${Date.now()}`, import.meta.url)).then(
    ({ default: worker }) => worker,
  );
  return workerPromise;
}

async function html(path) {
  const worker = await loadWorker();
  const response = await worker.fetch(
    new Request(`http://localhost${path}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
  assert.equal(response.status, 200);
  return response.text();
}

test("organizer pack renders the complete operations contract", async () => {
  const body = await html("/organizers/pack");
  assert.match(body, /JURY-PACK-INTERNAL/);
  assert.match(body, /class="pack-card-grid"/);
  assert.match(body, /class="jury-category-list"/);
  assert.match(body, /class="jury-bands"/);
  assert.doesNotMatch(body, /<table/);
  assert.match(body, /What do you have\?/);
  assert.match(body, /Never provide a threshold, EventSpec, handedness answer, private solution/);
  assert.match(body, /Seven checkpoint calls/);
  for (const beat of ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]) assert.match(body, new RegExp(`>${beat}<`));
  assert.match(body, /Internet or hosted page lost/);
  assert.match(body, /Historical form outage fallback/);
  assert.match(body, /retired for this event\. No collection route or recipient is active/i);
  assert.match(body, /Future authorized intake: invalid or incomplete/);
  assert.match(body, /Future authorized intake: duplicate, replacement, or late receipt/);
  assert.match(body, /Investigation and hypothesis/);
  assert.match(body, /Quality and evaluation/);
  assert.match(body, /Visualization and explanation/);
  assert.match(body, /Grounded agent trace/);
  assert.match(body, /Advanced method/);
  assert.match(body, /Failure-derived regression test/);
  assert.match(body, /Grounded agent trace __\/10; advanced method __\/5; failure-derived regression test __\/5/);
  assert.match(body, /same accepted metadata-only bundle/);
  assert.match(body, /Never average away a disagreement/);
  assert.match(body, /Final total __\/120/);
  assert.match(body, /Seven approved worked approaches/);
  assert.match(body, /14:54–14:57/);
  assert.match(body, /No is completely fine/);
});

test("organizer pack preserves fixed evaluator and authority semantics", async () => {
  const body = await html("/organizers/pack");
  assert.match(body, /55 machine points stay deterministic/);
  assert.match(body, /45 jury points and up to 20 bonus/);
  assert.match(body, /Kashiwa __\/15, Reims __\/10/);
  assert.match(body, /jury never changes submission authority/i);
  assert.match(body, /Later valid on-time hash.*replace authority/);
  assert.match(body, /Late: quarantine and never replace an on-time authority/);
});

test("historical organizer design keeps its specification without an active planning queue", async () => {
  const body = await html("/organizers");
  assert.match(body, /CIV 2026.*hackathon design/s);
  for (const id of ["purpose", "challenge", "workflow", "requirements", "evaluation", "organizing", "decisions"]) {
    assert.match(body, new RegExp(`id="${id}"`));
  }
  assert.match(body, /55 machine points, 45 jury points/);
  assert.match(body, /detected turn does not prove it/);
  assert.match(body, /Original caveats and provisional measurements remain historical evidence/);
  assert.doesNotMatch(body, /id="(?:phases|readiness|next)"/);
  assert.doesNotMatch(body, /Grilling complete|nothing remains to settle/);
});

test("operations roles expose summaries while keeping full procedures reachable", async () => {
  const body = await html("/organizers/pack");
  assert.match(body, /aria-label="Operations roles"/);
  assert.match(body, /href="#intake"/);
  assert.match(body, /id="intake"/);
  assert.match(body, /<summary>Full coaching and recovery protocol<\/summary>/);
  assert.match(body, /Suggest one check they can perform/);
  assert.match(body, /Confirm the accepted bundle and machine-score record/);
  assert.match(body, /Never average away a disagreement/);
  assert.match(body, /Consent wording/);
});
