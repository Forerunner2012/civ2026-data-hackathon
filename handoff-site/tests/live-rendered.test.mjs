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
  assert.match(b1, /BY NOW YOU SHOULD HAVE/);
  assert.match(b1, /IF YOU (?:DON.T|DON&#x27;T|DON&apos;T)/);
  assert.match(b1, /20:00/);
  assert.match(await htmlAt("10:05"), /15:00/);

  assert.match(await htmlAt("10:40"), /headings 1 and 2/i);
  const transfer = await htmlAt("11:00");
  assert.match(transfer, /transfer expectation/i);
  assert.match(transfer, /unlocked so far/i);
  assert.doesNotMatch(transfer, /Kashiwa|right turn|left turn|0\.08|4 m\/s|>=|<=/i);
  assert.match(await htmlAt("11:45"), /headings 3 and 4/i);
  assert.match(await htmlAt("12:10"), /heading 5/i);
  assert.match(await htmlAt("12:30"), /Submissions closed/i);
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
  assert.equal((document.match(/<button\b/g) ?? []).length, 1);
  assert.doesNotMatch(document, />\s*(?:Hold|Delay|Relock|Reverse)\b/i);
});

test("internal browser assets do not reveal future transfer guidance", async () => {
  const clientDir = fileURLToPath(new URL("../dist/client", import.meta.url));
  const entries = await readdir(clientDir, { recursive: true, withFileTypes: true });
  for (const entry of entries.filter((item) => item.isFile() && /\.(?:js|mjs|json)$/.test(item.name))) {
    const source = await readFile(`${entry.parentPath ?? entry.path}/${entry.name}`, "utf8");
    assert.doesNotMatch(source, /Transfer expectation: keep the command/i);
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
  assert.doesNotMatch(fallback, /<script|coach|advance|solution|Kashiwa/i);
});
