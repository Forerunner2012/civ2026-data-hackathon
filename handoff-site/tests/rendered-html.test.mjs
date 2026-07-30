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

async function render(path) {
  const worker = await loadWorker();
  return worker.fetch(
    new Request(`http://localhost${path}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

async function html(path) {
  const response = await render(path);
  assert.equal(response.status, 200, `${path} should render`);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const body = await response.text();
  assert.doesNotMatch(body, /codex-preview|SkeletonPreview|react-loading-skeleton/i);
  return body;
}

/**
 * Organizer-only material. None of this may appear in the participant route,
 * on the entry door, or anywhere in the client bundle. Add a phrase here
 * whenever new internal content lands in `app/_content/organizers.server.ts`.
 */
const ORGANIZER_ONLY = [
  /URT-Kashiwa/i,
  // The scenario is revealed at the event, not before: §4.3's brief is
  // deliberately an *incomplete* incident report.
  /unprotected right turn/i,
  /\bURT\b/,
  /grilling/i,
  /clean[- ]room/i,
  /sealed ground truth/i,
  /hidden label/i,
  /decision queue/i,
  /vertical slice/i,
  /mini-hackathon/i,
  /coach guide/i,
  /DESIGN EARLY/,
  /non-goals/i,
  /driving force/i,
  /source precedence/i,
  /quality defect/i,
];

test("entry door offers both views without leaking either", async () => {
  const body = await html("/");
  assert.match(body, /Data Hackathon 2026/);
  assert.match(body, /href="\/participants"/);
  assert.match(body, /href="\/organizers"/);
  for (const pattern of ORGANIZER_ONLY) {
    assert.doesNotMatch(body, pattern, `entry door leaks ${pattern}`);
  }
});

test("participant view states the contract", async () => {
  const body = await html("/participants");
  assert.match(body, /From raw bag/);
  assert.match(body, /defensible proof/);
  assert.match(body, /The rule ladder/);
  assert.match(body, /A fleet recorded several passages/);
  assert.match(body, /How the jury reads your work/);
  assert.match(body, /civ detect/);
  assert.match(body, /events\.jsonl/);
  // The ranking rule is published to participants even though the labels are not.
  assert.match(body, /sealed test set/i);
});

test("participant view contains no organizer material", async () => {
  const body = await html("/participants");
  for (const pattern of ORGANIZER_ONLY) {
    assert.doesNotMatch(body, pattern, `participant view leaks ${pattern}`);
  }
});

test("organizer view carries the internal planning", async () => {
  const body = await html("/organizers");
  assert.match(body, /Grilling complete/);
  assert.match(body, /URT-Kashiwa/);
  assert.match(body, /Six phases, six gates/);
  assert.match(body, /The part participants never see/);
  assert.match(body, /sealed ground truth/i);
  assert.match(body, /DESIGN EARLY/);
  assert.match(body, /not for participants/i);
});

test("organizer view groups the resolved decisions", async () => {
  const body = await html("/organizers");
  for (const group of ["Challenge", "Toolchain", "Process"]) {
    assert.match(body, new RegExp(group), `missing decision group ${group}`);
  }
  // Decisions by their answers rather than their labels.
  assert.match(body, /unprotected right turns/i);
  assert.match(body, /Container-first, BYOD only/);
  assert.match(body, /hero dataset/);
  assert.match(body, /right-turn manoeuvre interval/);
});

test("organizer view is marked non-indexable", async () => {
  const body = await html("/organizers");
  assert.match(body, /<meta name="robots" content="[^"]*noindex/i);
});

/**
 * The strongest guarantee: organizer text must never be compiled into an asset
 * a browser can download, whichever route requested it.
 */
test("client bundle contains no organizer material", async () => {
  const clientDir = fileURLToPath(new URL("../dist/client", import.meta.url));
  const entries = await readdir(clientDir, { recursive: true, withFileTypes: true });
  const assets = entries.filter(
    (entry) => entry.isFile() && /\.(js|mjs|css|json)$/.test(entry.name),
  );

  assert.ok(assets.length > 0, "expected a built client bundle to scan");

  for (const entry of assets) {
    const source = await readFile(`${entry.parentPath ?? entry.path}/${entry.name}`, "utf8");
    for (const pattern of ORGANIZER_ONLY) {
      assert.doesNotMatch(source, pattern, `${entry.name} leaks ${pattern}`);
    }
  }
});
