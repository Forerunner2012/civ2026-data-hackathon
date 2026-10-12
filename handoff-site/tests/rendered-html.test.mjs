import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import test from "node:test";
import { JSDOM } from "jsdom";
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
  /JURY-PACK-INTERNAL/i,
  /Never average away a disagreement/i,
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
  assert.match(body, /Investigate an incomplete report of vehicle behaviour/);
  assert.match(body, /test your reasoning on a different recording/i);
  assert.match(body, /recommend a next action/i);
  assert.match(body, /href="https:\/\/github\.com\/Forerunner2012\/civ2026-data-hackathon\/blob\/main\/kit\/ATTRIBUTION\.md"/);
  assert.match(body, /A fleet recorded several passages/);
  assert.match(body, /How the jury reads your work/);
  assert.match(body, /Write an EventSpec and run it across the supplied recordings/);
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
  assert.match(body, /docs\/quickstart\.md/);
  assert.match(body, /viewer\/README\.md/);
  assert.match(body, /\/desk\/warmup-trace\.html/);
  assert.match(body, /\/desk\/help-card\.html/);
  assert.match(body, /\/desk\/brief\.html/);
  assert.match(body, /Bounded agent with a useful trace.*10/i);
  assert.match(body, /advanced multimodal, data-quality or external-resource method.*5/i);
  assert.match(body, /Regression test built from a failure.*5/i);
  assert.match(body, /extension\/manifest\.json/);
  assert.match(body, /intake validates but never runs/i);
  // The ranking rule is published to participants even though the answer key is not.
  assert.match(body, /held-back test set/i);
  // Rules that change behaviour, so they must survive a redesign of the page.
  assert.match(body, /Submit as often as you like/i);
  assert.match(body, /scored by AI agents/i);
  assert.match(body, /your clips stay on your machine/i);
  assert.doesNotMatch(body, /tally\.so|SUBMISSION_FORM_URL|intake-local/i);
  assert.match(body, /fallback material or pair with someone if blocked/i);
});

test("optional extension is offered, scored, and never scheduled", async () => {
  const body = await html("/participants");
  assert.match(body, /outside both the recording and kit/i);
  assert.match(body, /no reserved session time/i);
  assert.match(body, /continue afterwards/i);
  assert.match(body, /examples\/reims\/cave-zones\.json/);
  assert.match(body, /examples\/reims\/cave-encounter\.yaml/);
  assert.match(body, /coordinates are illustrative/i);
  assert.match(body, /docs\/extension\.md/);
  assert.match(body, /core submission reproducing first/i);
  assert.match(body, /href="#scoring">Scoring/);
  assert.match(body, /does not automatically earn all bonus points/i);
  assert.match(body, /No paid model, API key, or GPU is required/i);
  // The zone coordinates are the exercise. Publishing any of them would hand over the answer.
  assert.doesNotMatch(body, /49\.2[0-9]{3}|4\.0[0-9]{3}/);
  assert.doesNotMatch(body, /martel|pommery|ruinart|taittinger|clicquot/i);
  // No chunk is named, so the page cannot say where the encounters are.
  assert.doesNotMatch(body, /RMS-CHUNK-[24]/);
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

test("organizer operations and jury pack is absent from the public artifact", async () => {
  const response = await render("/organizers/pack");
  assert.equal(response.status, 404);
  const body = await response.text();
  assert.doesNotMatch(body, /JURY-PACK-INTERNAL|artifact-verifiable anchors|coachProtocol/i);
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
  assert.doesNotMatch(serverBundle, /pattern:\s*"\/organizers\/pack"/);
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

test("simplified sections preserve workflow, kit paths and usable destinations", async () => {
  const document = new JSDOM(await html("/participants")).window.document;
  const toolkit = document.querySelector("#toolkit");
  assert.deepEqual(
    [...toolkit.querySelectorAll(".workflow-list li > b")].map((row) => row.textContent),
    ["Inspect", "Detect", "Check evidence", "Submit"],
  );
  assert.equal(toolkit.querySelectorAll(".pipeline > div").length, 6);
  assert.equal(toolkit.querySelector(".command-list"), null);
  assert.doesNotMatch(toolkit.textContent, /DATA FLOW/);
  const kit = document.querySelector("#kit");
  const paths = [...kit.querySelectorAll(".kit-guide-list code")].map((entry) => entry.textContent);
  assert.deepEqual(paths, ["README.md", "viewer/README.md", "docs/quickstart.md"]);
  assert.equal(kit.querySelectorAll("a[href^='http']").length, 0);
  assert.equal(kit.querySelectorAll(".kit-grid, .viewer-links, .extension-note").length, 0);
  const inventory = await readFile(new URL("../../src/civ_workshop/kit_inventory.py", import.meta.url), "utf8");
  for (const path of [...paths, "docs/extension.md", "examples/reims/cave-zones.json", "examples/reims/cave-encounter.yaml"]) {
    assert.ok(inventory.includes(`"${path}"`), `${path} must be a tracked kit asset`);
    const source = path === "README.md" || path.startsWith("viewer/") ? `kit/${path}` : path;
    assert.ok((await readFile(new URL(`../../${source}`, import.meta.url))).length > 0);
  }
  assert.equal(document.querySelectorAll("#extension .extension-steps > li").length, 3);
  assert.equal(document.querySelectorAll("#ready ol > li").length, 4);
  assert.doesNotMatch(document.querySelector("#ready").textContent, /Docker|WSL2|fully offline|SSDs|drop-ins/i);
  assert.equal(document.querySelector("#scoring h3.recognition-heading").textContent, "What is recognised at 15:00");
  for (const anchor of document.querySelectorAll("a[href^='#']")) {
    assert.ok(document.getElementById(anchor.getAttribute("href").slice(1)), "in-page link must resolve");
  }
  for (const anchor of kit.querySelectorAll(".desk-links a")) {
    assert.ok((await readFile(new URL(`../public${anchor.getAttribute("href")}`, import.meta.url))).length > 0);
  }
});

test("participant opening is concise and the brief holds the shared instructions", async () => {
  const document = new JSDOM(await html("/participants")).window.document;
  const opening = document.querySelector("#top .lede").textContent;
  assert.match(opening, /Investigate an incomplete report/);
  assert.match(opening, /Inspect the recordings, write an EventSpec/);
  assert.match(opening, /recommend a next action/);
  assert.doesNotMatch(opening, /docs\/quickstart\.md|Start with the participant page/);
  const brief = document.querySelector("#brief .brief-card").textContent;
  assert.ok(brief.includes(opening));
  assert.match(brief, /Start with the participant page and kit README/);
  assert.match(brief, /docs\/quickstart\.md/);
  assert.match(brief, /reproducible metadata-only bundle/);
  assert.match(brief, /Recordings and evidence clips stay local/);
  assert.match(brief, /A fleet recorded several passages/);
});

test("participant navigation exposes all ten native destinations and a numeric counter", async () => {
  for (const route of ["/", "/participants"]) {
    const document = new JSDOM(await html(route)).window.document;
    const header = document.querySelector("[data-participant-navigation]");
    assert.ok(header);
    const links = [...header.querySelectorAll("nav a")];
    assert.deepEqual(links.map((link) => link.getAttribute("href")),
      ["#top", "#brief", "#hours", "#responsibilities", "#deliver", "#scoring", "#toolkit", "#kit", "#extension", "#ready"]);
    for (const link of links) assert.ok(document.querySelector(link.getAttribute("href")));
    assert.match(header.querySelector("[data-section-position]").textContent, /^1\/10$/);
    assert.ok(header.querySelector(".participant-section-controls").hasAttribute("hidden"));
    assert.ok(header.querySelector("[data-section-previous]").disabled);
    assert.equal(document.querySelectorAll("script[src='/participant-navigation.js']").length, 1);
  }
});
