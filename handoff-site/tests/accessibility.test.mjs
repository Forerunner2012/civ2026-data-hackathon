import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { fileURLToPath } from "node:url";

const exportRoot = fileURLToPath(new URL("../tmp/participant-static", import.meta.url));
const pages = [
  "index.html",
  "participants/index.html",
  "session-fallback.html",
  "desk/brief.html",
  "desk/help-card.html",
  "desk/warmup-trace.html",
];
const expectedPrimaryHeadings = new Map([["desk/help-card.html", 2]]);

function visibleText(fragment) {
  return fragment
    .replace(/<[^>]+>/g, " ")
    .replace(/&(?:nbsp|#160);/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

test("static participant pages preserve the structural accessibility contract", async () => {
  for (const relative of pages) {
    const html = await readFile(`${exportRoot}/${relative}`, "utf8");
    assert.match(html, /<html[^>]+lang="en"/i, `${relative} needs a language`);
    assert.match(html, /<title>[^<]+<\/title>/i, `${relative} needs a title`);
    assert.equal(
      html.match(/<h1\b/gi)?.length ?? 0,
      expectedPrimaryHeadings.get(relative) ?? 1,
      `${relative} has the wrong number of primary headings`,
    );

    const headingLevels = [...html.matchAll(/<h([1-6])\b/gi)].map((match) => Number(match[1]));
    for (let index = 1; index < headingLevels.length; index += 1) {
      assert.ok(
        headingLevels[index] <= headingLevels[index - 1] + 1,
        `${relative} skips a heading level`,
      );
    }

    for (const match of html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi)) {
      const attributes = match[1];
      const name = visibleText(match[2]);
      assert.ok(
        name || /aria-label="[^"]+"/i.test(attributes),
        `${relative} contains an unnamed link`,
      );
    }
    assert.doesNotMatch(html, /<img\b(?![^>]*\balt=)[^>]*>/i, `${relative} has an image without alt`);
  }
});

test("the participant navigation and signal graphic expose accessible names", async () => {
  const participants = await readFile(`${exportRoot}/participants/index.html`, "utf8");
  const trace = await readFile(`${exportRoot}/desk/warmup-trace.html`, "utf8");

  assert.match(participants, /<nav[^>]+aria-label="Page sections"/i);
  assert.match(trace, /<svg[^>]+role="img"[^>]+aria-labelledby=/i);
  assert.match(trace, /<title\b[^>]*>[^<]+<\/title>/i);
  assert.match(trace, /<desc\b[^>]*>[^<]+<\/desc>/i);
});
