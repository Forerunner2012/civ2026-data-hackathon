import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { JSDOM } from "jsdom";
import { fileURLToPath } from "node:url";

const exportRoot = fileURLToPath(new URL("../tmp/participant-static", import.meta.url));

test("static attendee export permits only the local navigation script", async () => {
  const root = await readFile(`${exportRoot}/index.html`, "utf8");
  const participants = await readFile(`${exportRoot}/participants/index.html`, "utf8");
  const fallback = await readFile(`${exportRoot}/session-fallback.html`, "utf8");
  assert.match(root, /From raw bag/);
  assert.match(participants, /The rule ladder/);
  assert.match(participants, /docs\/quickstart\.md/);
  assert.match(participants, /viewer\/README\.md/);
  assert.match(participants, /docs\/extension\.md/);
  assert.match(root, /href="index\.html"/);
  assert.match(participants, /href="\.\.\/index\.html"/);
  assert.match(participants, /href="\.\.\/assets\//);
  for (const [html, src] of [[root, "participant-navigation.js"], [participants, "../participant-navigation.js"]]) {
    const document = new JSDOM(html).window.document;
    const scripts = [...document.querySelectorAll("script")];
    assert.equal(scripts.length, 1);
    assert.equal(scripts[0].getAttribute("src"), src);
    assert.equal(scripts[0].getAttribute("type"), null);
    assert.equal(scripts[0].textContent, "");
    assert.ok(scripts[0].hasAttribute("defer"));
  }
  assert.doesNotMatch(fallback, /<script/i);
  assert.doesNotMatch(`${root}\n${participants}\n${fallback}`, /\/organizers|\/live\/coach/i);
  const files = (await readFile(`${exportRoot}/STATIC-FILES.txt`, "utf8")).trim().split("\n");
  assert.deepEqual(files.filter((file) => /\.[cm]?js$/.test(file)), ["participant-navigation.js"]);
  assert.equal(await readFile(`${exportRoot}/participant-navigation.js`, "utf8"),
    await readFile(new URL("../public/participant-navigation.js", import.meta.url), "utf8"));
});
