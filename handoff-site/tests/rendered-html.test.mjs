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
  // Map two's internal vocabulary. "held-back", "answer key" and "worked
  // example" are deliberately NOT here — participants are told those.
  /pace car/i,
  /\bdecoy\b/i,
  /hard braking/i,
  /boundary convention/i,
  /sealed label/i,
];

const LIVE_INTERNAL_ONLY = [
  /\/api\/live/,
  /LIVE_COACH_TOKEN/,
  /Advance room to next state/i,
  /Transfer expectation: keep the command/i,
];

test("public root is the participant view", async () => {
  const body = await html("/");
  assert.match(body, /From raw bag/);
  assert.match(body, /defensible proof/);
  assert.doesNotMatch(body, /href="\/organizers"/);
  assert.doesNotMatch(body, /internal handoff|organizer/i);
  for (const pattern of ORGANIZER_ONLY) {
    assert.doesNotMatch(body, pattern, `public root leaks ${pattern}`);
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
  assert.match(body, /solo or duo/i);
  assert.match(body, /different sensor stack/i);
  assert.match(body, /55 points are machine-scored/i);
  assert.match(body, /15 points on the first held-back set and 10 on the transfer set/i);
  assert.match(body, /one-page report/i);
  assert.match(body, /civ submission-init working --shell powershell/i);
  assert.match(body, /same participant or team identity/i);
  assert.match(body, /server receipt time is authoritative/i);
  assert.match(body, /later valid on-time bundle for the same dataset is authoritative/i);
  assert.match(body, /Incomplete or invalid/);
  assert.match(body, /Hash mismatch/);
  assert.match(body, /Duplicate reference/);
  assert.match(body, /Late/);
  assert.match(body, /KSH-64ac27cd029b-signals\.mcap/);
  assert.match(body, /RMS-CHUNK-0-0a0817b3afc8-signals\.mcap/);
  assert.match(body, /layouts\/kashiwa-right-turn\.pj4\.xml/);
  assert.match(body, /layouts\/reims-left-turn\.pj4\.xml/);
  assert.match(body, /Optional extension.*scored, but not scheduled/is);
  assert.match(body, /\/desk\/warmup-trace\.html/);
  assert.match(body, /\/desk\/help-card\.html/);
  assert.match(body, /\/desk\/brief\.html/);
  const commandList = body.match(/<div class="command-list">([\s\S]+?)<\/div>/)?.[1] ?? "";
  const commandOffsets = ["civ doctor", "civ inspect", "civ sample", "civ detect", "civ clip", "civ score", "civ report"].map((command) => commandList.indexOf(command));
  assert.ok(commandOffsets.every((offset) => offset >= 0));
  assert.deepEqual(commandOffsets, [...commandOffsets].sort((a, b) => a - b));
  // The ranking rule is published to participants even though the answer key is not.
  assert.match(body, /held-back test set/i);
  // Rules that change behaviour, so they must survive a redesign of the page.
  assert.match(body, /Submit as often as you like/i);
  assert.match(body, /scored by AI agents/i);
  assert.match(body, /your clips stay on your machine/i);
  assert.doesNotMatch(body, /tally\.so|SUBMISSION_FORM_URL|intake-local/i);
  assert.match(body, /pairing up on the day is normal/i);
});

test("participant view contains no organizer material", async () => {
  const body = await html("/participants");
  for (const pattern of ORGANIZER_ONLY) {
    assert.doesNotMatch(body, pattern, `participant view leaks ${pattern}`);
  }
});

test("organizer view is absent from the public artifact", async () => {
  const response = await render("/organizers");
  assert.equal(response.status, 404);
  const body = await response.text();
  for (const pattern of ORGANIZER_ONLY) {
    assert.doesNotMatch(body, pattern, `public 404 leaks ${pattern}`);
  }
});

/**
 * The live session page carries hints and, eventually, worked solutions. It is
 * served from the organizer's machine on the day — never from the public site.
 */
test("live session page is absent from the public artifact", async () => {
  const response = await render("/live");
  assert.equal(response.status, 404);
  const body = await response.text();
  for (const pattern of ORGANIZER_ONLY) {
    assert.doesNotMatch(body, pattern, `public 404 leaks ${pattern}`);
  }
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
    for (const pattern of LIVE_INTERNAL_ONLY) {
      assert.doesNotMatch(source, pattern, `${entry.name} leaks live-only ${pattern}`);
    }
  }
});

test("controlled solutions are absent from the public artifact", async () => {
  const response = await render("/solutions");
  assert.equal(response.status, 404);
  const body = await response.text();
  assert.doesNotMatch(body, /worked approaches|189 matching samples/i);
});

test("public artifact retains the participant-safe static fallback", async () => {
  const fallback = await readFile(
    fileURLToPath(new URL("../dist/client/session-fallback.html", import.meta.url)),
    "utf8",
  );
  assert.match(fallback, /Session fallback/);
  assert.doesNotMatch(fallback, /<script|coach|advance|solution|Kashiwa/i);
});

test("server bundle contains no organizer route or material", async () => {
  const serverBundle = await readFile(
    fileURLToPath(new URL("../dist/server/index.js", import.meta.url)),
    "utf8",
  );

  assert.doesNotMatch(serverBundle, /pattern:\s*"\/organizers"/);
  assert.doesNotMatch(serverBundle, /pattern:\s*"\/live"/);
  assert.doesNotMatch(serverBundle, /pattern:\s*"\/live\/coach"/);
  assert.doesNotMatch(serverBundle, /pattern:\s*"\/api\/live"/);
  assert.doesNotMatch(serverBundle, /pattern:\s*"\/solutions"/);
  for (const pattern of ORGANIZER_ONLY) {
    assert.doesNotMatch(serverBundle, pattern, `server bundle leaks ${pattern}`);
  }
  for (const pattern of LIVE_INTERNAL_ONLY) {
    assert.doesNotMatch(serverBundle, pattern, `server bundle leaks live-only ${pattern}`);
  }
});
