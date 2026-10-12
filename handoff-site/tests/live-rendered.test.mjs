import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import test from "node:test";
import { fileURLToPath } from "node:url";

let workerPromise;

function loadWorker() {
  workerPromise ??= (async () => {
    const workerUrl = new URL("../dist/server/index.js", import.meta.url);
    workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
    const { default: worker } = await import(workerUrl.href);
    return worker;
  })();
  return workerPromise;
}

async function request(path, init) {
  const worker = await loadWorker();
  return worker.fetch(
    new Request(`http://localhost${path}`, init),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

async function htmlAt(time) {
  const response = await request(`/live?now=${encodeURIComponent(`2026-09-03T${time}:00+09:00`)}`, {
    headers: { accept: "text/html" },
  });
  assert.equal(response.status, 200);
  return response.text();
}

test("live page renders schedule, countdown, prompts, and participant-safe transfer guidance", async () => {
  const boundaries = [
    ["09:30", /OPENING/],
    ["10:00", /B1/],
    ["10:20", /B2/],
    ["10:40", /B3/],
    ["11:00", /B4/],
    ["11:25", /B5/],
    ["11:45", /B6/],
    ["12:10", /B7/],
    ["12:30", /CLOSE/],
  ];
  for (const [time, stage] of boundaries) {
    assert.match(await htmlAt(time), stage);
  }

  const b1 = await htmlAt("10:00");
  assert.match(b1, /B1/);
  assert.match(b1, /EXPECTED RESULT/);
  assert.match(b1, /IF BLOCKED/);
  assert.match(b1, /<summary>Expectation<\/summary>/);
  assert.match(b1, /<summary>Hint<\/summary>/);
  assert.match(b1, /<summary>Tip<\/summary>/);
  assert.match(b1, /20:00/);
  assert.match(await htmlAt("10:05"), /15:00/);

  assert.match(await htmlAt("10:40"), /headings 1 and 2/i);
  const timing = await htmlAt("10:20");
  assert.match(timing, /189 matching samples.*14 merged candidates.*4 events/i);
  assert.match(timing, /zero brake response/i);
  assert.match(timing, /timing fixes the count, not the meaning/i);
  assert.doesNotMatch(timing, /headings 1 and 2/i);
  const transfer = await htmlAt("11:00");
  assert.match(transfer, /transfer expectation/i);
  assert.match(transfer, /Guidance released so far/i);
  assert.doesNotMatch(transfer, /Kashiwa|right turn|left turn|0\.08|4 m\/s|>=|<=/i);
  assert.match(await htmlAt("11:45"), /headings 3 and 4/i);
  assert.match(await htmlAt("12:10"), /heading 5/i);
  assert.match(await htmlAt("12:30"), /Submissions closed/i);

  assert.match(b1, /Submit metadata bundle/i);
  assert.match(b1, /Quickstart reference/);
  assert.doesNotMatch(b1, /Eight commands, one evidence chain/);
  assert.match(b1, /docs\/quickstart\.md/i);
  assert.match(b1, /civ report/i);
  assert.match(b1, /submission\.zip/i);
  assert.match(b1, /12 MiB per bundle.*8 MiB per metadata artifact/i);
  assert.match(b1, /USB fallback/i);
  if (process.env.SUBMISSION_FORM_URL) {
    assert.match(b1, /https:\/\/forms\.example\.test\/civ-phase1/);
  } else {
    assert.doesNotMatch(b1, /forms\.example\.test/);
    assert.match(b1, /online form is not configured.*USB fallback/i);
  }
  assert.match(b1, /confirmation.*submission reference/i);
  assert.match(b1, /server receipt time tied.*authoritative/i);
  assert.match(b1, /latest valid response for.*dataset.*12:30 JST is authoritative/i);
  assert.match(b1, /organizer records the same hash-and-time receipt/i);
});

test("approved post-event solutions require a separate release flag", async () => {
  const response = await request("/solutions", { headers: { accept: "text/html" } });
  assert.equal(response.status, 200);
  const body = await response.text();
  assert.match(body, /Post-event · released/i);
  assert.match(body, /Seven beats, one defensible workflow/i);
  assert.equal((body.match(/class="phase-id"/g) ?? []).length, 7);
  assert.doesNotMatch(body, /right turn|left turn|answer interval/i);
});

test("authorized coach advance is next-only, idempotent, and survives refresh", async () => {
  const path = `/api/live?now=${encodeURIComponent("2026-09-03T10:00:00+09:00")}`;
  const unauthorized = await request(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ requestId: "advance-rendered", observedStageId: "b1" }),
  });
  assert.equal(unauthorized.status, 401);

  const command = {
    method: "POST",
    headers: {
      authorization: "Bearer test-coach-token",
      "content-type": "application/json",
    },
    body: JSON.stringify({ requestId: "advance-rendered", observedStageId: "b1" }),
  };
  const first = await request(path, command);
  assert.equal(first.status, 200);
  assert.equal((await first.json()).stage.id, "b2");

  const repeated = await request(path, command);
  assert.equal(repeated.status, 200);
  assert.equal((await repeated.json()).outcome, "already-applied");

  const stale = await request(path, {
    method: "POST",
    headers: {
      authorization: "Bearer test-coach-token",
      "content-type": "application/json",
    },
    body: JSON.stringify({ requestId: "attempt-reversal", observedStageId: "b1" }),
  });
  assert.equal(stale.status, 409);
  assert.equal((await stale.json()).outcome, "stale");

  const unchanged = await request(path);
  assert.equal(unchanged.status, 200);
  assert.equal((await unchanged.json()).stage.id, "b2");

  const refreshed = await htmlAt("10:00");
  assert.match(refreshed, /B2/);
  assert.doesNotMatch(refreshed, /B3/);

  assert.equal((await request(path, { method: "PUT" })).status, 405);
  assert.equal((await request(path, { method: "DELETE" })).status, 405);
});

test("coach screen renders one next action and no reversal control", async () => {
  const response = await request(
    `/live/coach?now=${encodeURIComponent("2026-09-03T10:00:00+09:00")}`,
    { headers: { accept: "text/html" } },
  );
  assert.equal(response.status, 200);
  const document = (await response.text()).split("</html>", 1)[0];
  assert.match(document, /Advance room to next state/);
  assert.match(document, /DISPLAY ASSISTANCE/);
  assert.match(document, /Current attendee action/);
  assert.match(document, /doctor.*inspect.*sample.*submission-init.*detect.*clip.*score.*report/is);
  assert.equal((document.match(/<button\b/g) ?? []).length, 1);
  assert.doesNotMatch(document, />\s*(?:Hold|Delay|Relock|Reverse)\b/i);
});

test("internal browser assets do not reveal future transfer guidance", async () => {
  const clientDir = fileURLToPath(new URL("../dist/client", import.meta.url));
  const entries = await readdir(clientDir, { recursive: true, withFileTypes: true });
  for (const entry of entries.filter((item) => item.isFile() && /\.(?:js|mjs|json)$/.test(item.name))) {
    const source = await readFile(`${entry.parentPath ?? entry.path}/${entry.name}`, "utf8");
    assert.doesNotMatch(source, /Transfer expectation: keep the command/i);
    assert.doesNotMatch(source, /189 matching samples.*14 merged candidates/i);
    assert.doesNotMatch(source, /SUBMISSION_FORM_URL|LIVE_COACH_TOKEN|intake\.sqlite3/i);
  }
});

test("static fallback is readable, script-free, and exposes no coach control", async () => {
  const fallback = await readFile(
    fileURLToPath(new URL("../public/session-fallback.html", import.meta.url)),
    "utf8",
  );
  assert.match(fallback, /Session fallback/);
  assert.match(fallback, /BY NOW YOU SHOULD HAVE/);
  assert.match(fallback, /IF YOU (?:DON.T|DON&#x27;T|DON&apos;T)/);
  assert.match(fallback, /latest valid on-time bundle for that dataset is authoritative/i);
  assert.match(fallback, /incomplete or invalid.*hash does not match.*repeated reference.*late receipt/is);
  assert.doesNotMatch(fallback, /<script|coach|advance|solution|Kashiwa/i);
});
