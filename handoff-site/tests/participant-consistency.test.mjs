import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { JSDOM } from "jsdom";

const canonical = async (name) => readFile(new URL(`../../docs/${name}`, import.meta.url), "utf8");
const exported = async (name) => new JSDOM(await readFile(new URL(`../tmp/participant-static/${name}`, import.meta.url), "utf8")).window.document;

test("desk commands and eight-step pipeline match the canonical quickstart", async () => {
  const quickstart = await canonical("quickstart.md");
  const card = await exported("desk/help-card.html");
  const commands = [...card.querySelectorAll(".up code")].map((entry) => entry.textContent);
  const expected = ["doctor", "inspect"].map((command) => quickstart.split("\n").find((line) => line.startsWith(`civ ${command} `)));
  assert.deepEqual(commands, expected);
  const sequence = [...quickstart.matchAll(/^\| \d \| `civ ([a-z-]+)`/gm)].map((match) => match[1]);
  const brief = await exported("desk/brief.html");
  assert.equal(sequence.length, 8);
  assert.deepEqual([...brief.querySelectorAll(".pipeline span")].map((entry) => entry.textContent), sequence);
});

test("published score totals match the canonical scoring reference", async () => {
  const reference = await canonical("reference/scoring.md");
  const split = reference.match(/fixed (\d+) machine \/ (\d+) jury rubric; up to (\d+) optional bonus points/);
  assert.ok(split, "canonical reference must state its approved point allocation");
  const document = await exported("participants/index.html");
  const totals = [...document.querySelectorAll("#scoring tr.score-total .score-points")].map((entry) => Number(entry.textContent));
  assert.deepEqual(totals, [Number(split[1]) + Number(split[2]), Number(split[3])]);
  const brief = await exported("desk/brief.html");
  assert.match(brief.body.textContent, new RegExp(`${split[1]} points are machine-scored`));
  assert.match(brief.body.textContent, new RegExp(`AI agents score the ${split[2]} report points`));
});

test("static participant guidance does not promise live state or a partial scoring key", async () => {
  const setup = await canonical("setup.md");
  assert.match(setup, /site\/index\.html.*static participant page/);
  for (const page of ["index.html", "participants/index.html"]) {
    const document = await exported(page);
    const hours = document.querySelector("#hours").textContent;
    assert.match(hours, /static guides/);
    assert.match(hours, /separate live page/);
    assert.doesNotMatch(hours, /Start your container|It moves on a schedule/);
    const responsibilities = document.querySelector("#responsibilities").textContent;
    assert.match(responsibilities, /Complete reviewed practice labels.*exact source.*when supplied/);
    assert.doesNotMatch(responsibilities, /answer key for two or three|SSDs in the room/);
  }
});
