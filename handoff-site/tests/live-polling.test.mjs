import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import test from "node:test";
import { JSDOM } from "jsdom";
import { act, createElement } from "react";
import { createRoot } from "react-dom/client";
import ts from "typescript";

// Transpile the shipped component; React and its effects run unchanged in a DOM.
const source = await readFile(new URL("../app/live/live-session.tsx", import.meta.url), "utf8");
const { outputText } = ts.transpileModule(source, {
  compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX,
  },
});
const componentModule = { exports: {} };
new Function("require", "module", "exports", outputText)(
  createRequire(import.meta.url), componentModule, componentModule.exports,
);
const { LiveSession } = componentModule.exports;

function snapshot(stageIndex, nowMs = 0) {
  return {
    nowMs,
    stageIndex,
    stage: {
      id: `stage-${stageIndex}`, time: "10:00", beat: `B${stageIndex}`,
      title: `Stage ${stageIndex}`, action: "Continue the exercise",
      shouldHave: "Current evidence", ifYouDont: "Use recovery guidance",
      expectation: "Current expectation", hint: "Current hint", tip: "Current tip",
    },
    unlockedGuidance: Array.from({ length: stageIndex }, (_, i) => `Guidance ${i + 1}`),
    nextStartMs: 60_000,
    advancedEarly: false,
  };
}

function deferred() {
  let resolve;
  const promise = new Promise((done) => { resolve = done; });
  return { promise, resolve };
}

async function mount(t, fetchImpl, controlledNow = "controlled time +09:00") {
  const dom = new JSDOM("<div id='root'></div>");
  t.mock.method(globalThis, "fetch", fetchImpl);
  const originals = ["window", "document", "IS_REACT_ACT_ENVIRONMENT"].map(
    (key) => [key, Object.getOwnPropertyDescriptor(globalThis, key)],
  );
  Object.assign(globalThis, {
    window: dom.window, document: dom.window.document, IS_REACT_ACT_ENVIRONMENT: true,
  });
  t.mock.timers.enable({ apis: ["setInterval", "Date"], now: 0 });
  dom.window.setInterval = globalThis.setInterval;
  dom.window.clearInterval = globalThis.clearInterval;
  const container = dom.window.document.getElementById("root");
  const root = createRoot(container);
  let unmounted = false;
  const unmount = async () => {
    if (!unmounted) {
      await act(() => root.unmount());
      unmounted = true;
    }
  };
  t.after(async () => {
    await unmount();
    dom.window.close();
    for (const [key, descriptor] of originals) {
      if (descriptor) Object.defineProperty(globalThis, key, descriptor);
      else delete globalThis[key];
    }
  });
  const render = async (clock = controlledNow) => {
    await act(() => root.render(createElement(LiveSession, {
      initialSnapshot: snapshot(1), controlledNow: clock, submissionFormUrl: null,
    })));
  };
  await render();
  return {
    container, render, unmount,
    tick: async (ms) => { await act(() => t.mock.timers.tick(ms)); },
  };
}

for (const [name, failure] of [
  ["rejected request", () => Promise.reject(new Error("network outage"))],
  ["non-200 response", () => Promise.resolve(new Response("unavailable", { status: 503 }))],
  ["malformed JSON", () => Promise.resolve(new Response("{broken"))],
]) {
  test(`${name} retains the last valid guidance and a later poll recovers`, async (t) => {
    let requests = 0;
    const view = await mount(t, async (path, options) => {
      assert.equal(path, "/api/live?now=controlled%20time%20%2B09%3A00");
      assert.deepEqual(options, { cache: "no-store" });
      requests += 1;
      if (requests === 1) return Response.json(snapshot(2, 10_000));
      if (requests <= 3) return failure();
      return Response.json(snapshot(3, 20_000));
    });
    assert.equal(view.container.querySelector("h1").textContent, "Stage 2");
    assert.equal(view.container.querySelector(".live-countdown b").textContent, "00:50");
    const guidance = view.container.querySelector("#guidance ol").textContent;
    for (let attempt = 0; attempt < 2; attempt += 1) {
      await view.tick(3_000);
      assert.equal(view.container.querySelector("h1").textContent, "Stage 2");
      assert.equal(view.container.querySelector("#guidance ol").textContent, guidance);
      assert.equal(view.container.querySelector(".live-countdown b").textContent, "00:50");
    }
    await view.tick(3_000);
    assert.equal(view.container.querySelector("h1").textContent, "Stage 3");
    assert.match(view.container.querySelector("#guidance ol").textContent, /Guidance 3/);
    assert.equal(view.container.querySelector(".live-countdown b").textContent, "00:40");
  });
}

test("an initial failure preserves server guidance while the normal clock keeps ticking", async (t) => {
  let requests = 0;
  const view = await mount(t, async (path) => {
    assert.equal(path, "/api/live");
    requests += 1;
    if (requests === 1) throw new Error("initial outage");
    return Response.json(snapshot(2, 30_000));
  }, null);
  assert.equal(view.container.querySelector("h1").textContent, "Stage 1");
  assert.match(view.container.querySelector("#guidance ol").textContent, /Guidance 1/);
  await view.tick(1_000);
  assert.equal(requests, 1);
  assert.equal(view.container.querySelector(".live-countdown b").textContent, "00:59");
  await view.tick(2_000);
  assert.equal(view.container.querySelector("h1").textContent, "Stage 2");
  assert.equal(view.container.querySelector(".live-countdown b").textContent, "00:57");
});

test("a decoded response from a cleaned-up effect cannot overwrite the new clock's snapshot", async (t) => {
  const decoding = deferred();
  let requests = 0;
  const view = await mount(t, async () => {
    requests += 1;
    if (requests === 1) return { ok: true, json: () => decoding.promise };
    return Response.json(snapshot(3, 20_000));
  });
  await view.render("new controlled clock");
  await act(() => decoding.resolve(snapshot(2, 10_000)));
  assert.equal(view.container.querySelector("h1").textContent, "Stage 3");
  assert.equal(view.container.querySelector(".live-countdown b").textContent, "00:40");
});

for (const phase of ["request", "decoding"]) {
  test(`unmount during ${phase} ignores the pending response and clears polling`, async (t) => {
    const pending = deferred();
    let requests = 0;
    const view = await mount(t, () => {
      requests += 1;
      return phase === "request" ? pending.promise : Promise.resolve({
        ok: true, json: () => pending.promise,
      });
    });
    await view.unmount();
    const lateSnapshot = snapshot(2);
    let snapshotReads = 0;
    Object.defineProperty(lateSnapshot, "nowMs", {
      get() { snapshotReads += 1; return 0; },
    });
    await act(() => pending.resolve(phase === "request" ? {
      ok: true, json: () => Promise.resolve(lateSnapshot),
    } : lateSnapshot));
    await view.tick(6_000);
    assert.equal(snapshotReads, 0);
    assert.equal(requests, 1);
    assert.equal(view.container.innerHTML, "");
  });
}
