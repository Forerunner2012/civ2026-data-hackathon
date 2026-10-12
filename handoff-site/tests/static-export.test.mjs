import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { fileURLToPath } from "node:url";

const exportRoot = fileURLToPath(new URL("../tmp/participant-static", import.meta.url));

test("static attendee export is script-free and navigable from disk", async () => {
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
  assert.doesNotMatch(`${root}\n${participants}\n${fallback}`, /<script\b|\/organizers|\/live\/coach/i);
});
