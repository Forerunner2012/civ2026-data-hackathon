import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { mkdir, mkdtemp, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

// Optional test infrastructure, never a participant runtime dependency.
const site = fileURLToPath(new URL("..", import.meta.url));
const browser = process.env.CIV_BROWSER_EXECUTABLE ?? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const output = path.join(site, "tmp/navigation-browser");
await mkdir(output, { recursive: true });
const profile = await mkdtemp(path.join(output, "profile-"));
const { default: worker } = await import(pathToFileURL(path.join(site, "dist/server/index.js")));
const clientRoot = path.join(site, "dist/client");
const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url, "http://localhost");
    if (url.pathname.startsWith("/assets/") || url.pathname === "/participant-navigation.js") {
      const file = path.resolve(clientRoot, "." + url.pathname);
      assert.ok(file.startsWith(clientRoot + path.sep));
      const bytes = await readFile(file);
      response.writeHead(200, { "Content-Type": file.endsWith(".css") ? "text/css" : "application/javascript" });
      response.end(bytes);
    } else {
      const rendered = await worker.fetch(new Request(url), { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, { waitUntil() {}, passThroughOnException() {} });
      response.writeHead(rendered.status, Object.fromEntries(rendered.headers));
      response.end(Buffer.from(await rendered.arrayBuffer()));
    }
  } catch (error) { response.writeHead(500); response.end(String(error)); }
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const origin = "http://127.0.0.1:" + server.address().port;
const child = spawn(browser, ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--remote-debugging-port=0", "--user-data-dir=" + profile, "about:blank"], { windowsHide: true, stdio: "ignore" });
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
let socket;
let send;
const results = [];
try {
  let port;
  for (let attempt = 0; attempt < 100; attempt++) {
    try { port = (await readFile(path.join(profile, "DevToolsActivePort"), "utf8")).split("\n")[0]; break; } catch { await delay(100); }
  }
  assert.ok(port, "owned browser must start");
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket = new WebSocket(targets.find((target) => target.type === "page").webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  const pending = new Map();
  let sequence = 0;
  send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(method + " timed out")); }, 10000);
    pending.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const runtimeErrors = [];
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.method === "Runtime.exceptionThrown") runtimeErrors.push(message.params);
    const request = pending.get(message.id);
    if (!request) return;
    clearTimeout(request.timer);
    pending.delete(message.id);
    if (message.error) request.reject(new Error(JSON.stringify(message.error)));
    else request.resolve(message.result);
  };
  const evaluate = async (expression) => {
    const reply = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
    if (reply.exceptionDetails) throw new Error(JSON.stringify(reply.exceptionDetails));
    return reply.result.value;
  };
  const waitFor = async (expression) => {
    for (let attempt = 0; attempt < 500; attempt++) { if (await evaluate(expression)) return; await delay(20); }
    await writeFile(path.join(output, "runtime-errors.json"), JSON.stringify({runtimeErrors, html:await evaluate("document.documentElement.outerHTML.slice(0,2500)")}, null, 2));
    throw new Error("Browser condition timed out: " + expression);
  };
  const snapshot = () => evaluate(`(()=>{const header=document.querySelector('[data-participant-navigation]');return {counter:header.querySelector('[data-section-position]').textContent, hash:location.hash, focus:document.activeElement.closest('section')?.id, focusTag:document.activeElement.tagName, sticky:Math.round(header.getBoundingClientRect().top), height:header.offsetHeight, history:history.length, current:header.querySelector('[aria-current="location"]').hash, previous:header.querySelector('[data-section-previous]').disabled, next:header.querySelector('[data-section-next]').disabled, scrollX:scrollX, width:document.documentElement.clientWidth, scrollWidth:document.documentElement.scrollWidth};})()`);
  const key = async (keyName, extras = {}) => {
    await send("Input.dispatchKeyEvent", { type: "keyDown", key: keyName, code: keyName, windowsVirtualKeyCode: keyName === "ArrowRight" ? 39 : 37, ...extras });
    await send("Input.dispatchKeyEvent", { type: "keyUp", key: keyName, code: keyName, windowsVirtualKeyCode: keyName === "ArrowRight" ? 39 : 37 });
    await delay(80);
  };
  const ids = ["top", "brief", "hours", "responsibilities", "deliver", "scoring", "toolkit", "kit", "extension", "ready"];
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
  const routes = [origin + "/", origin + "/participants", pathToFileURL(path.join(site, "tmp/participant-static/index.html")).href, pathToFileURL(path.join(site, "tmp/participant-static/participants/index.html")).href];
  for (const [screen, width, height] of [["desktop", 1440, 1000], ["mobile", 390, 844]]) {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: screen === "mobile" });
    for (const route of routes) {
      await send("Page.navigate", { url: route + "#top" });
      await waitFor("document.querySelector('[data-participant-navigation]')?.dataset.navigationReady === 'true'");
      await delay(1000);
      assert.equal((await snapshot()).counter, "1/10");
      assert.ok((await snapshot()).previous);
      for (let index = 0; index < ids.length; index++) {
        await evaluate(`document.querySelector('nav a[href="#${ids[index]}"]').click()`);
        await delay(350);
        const state = await snapshot();
        await writeFile(path.join(output, "last-state.json"), JSON.stringify({screen, route, index, state, runtimeErrors}, null, 2));
        assert.equal(state.counter, `${index + 1}/10`);
        assert.equal(state.hash, "#" + ids[index]);
        assert.equal(state.focus, ids[index]);
        assert.ok(await evaluate("parseFloat(getComputedStyle(document.activeElement).outlineWidth) >= 3"), "destination focus must be visible");
        assert.equal(state.current, "#" + ids[index]);
        assert.equal(state.sticky, 0);
        assert.ok(state.scrollWidth <= state.width, "document must not overflow");
        assert.ok(await evaluate("document.activeElement.getBoundingClientRect().top >= document.querySelector('header').getBoundingClientRect().bottom - 1"), "heading must remain visible below header");
      }
      assert.ok((await snapshot()).next);
      assert.equal(await evaluate("[...document.querySelectorAll('h1[tabindex],h2[tabindex],h3[tabindex]')].every(h=>h.tabIndex===-1)"), true);
      await evaluate("document.querySelector('.brand').focus()");
      for (let step = 0; step < 12; step++) {
        await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        assert.ok(await evaluate("/^(A|BUTTON)$/.test(document.activeElement.tagName)"), "normal Tab order must omit destination headings");
      }
      // Manual scrolling updates position only, retaining focus, fragment and history.
      const before = await snapshot();
      await evaluate("scrollTo({top:0,behavior:'instant'})");
      await delay(200);
      const manual = await snapshot();
      assert.equal(manual.counter, "1/10");
      assert.equal(manual.focus, before.focus);
      assert.equal(manual.history, before.history);
      assert.equal(manual.hash, before.hash);
      await evaluate("document.querySelector('nav a[href=\"#scoring\"]').click()");
      await delay(350);
      await evaluate("document.querySelector('[data-section-next]').click()");
      await delay(350);
      assert.equal((await snapshot()).hash, "#toolkit");
      await evaluate("history.back()");
      await waitFor("location.hash === '#scoring'");
      await delay(350);
      assert.equal((await snapshot()).counter, "6/10");
      await evaluate("history.forward()");
      await waitFor("location.hash === '#toolkit'");
      await delay(350);
      assert.equal((await snapshot()).counter, "7/10");
      // An eligible real key focuses the destination; held keys and modifiers do not jump.
      await evaluate("document.querySelector('#toolkit h2').focus()");
      await key("ArrowRight");
      assert.equal((await snapshot()).hash, "#kit");
      for (const extras of [{ autoRepeat: true }, { modifiers: 1 }, { modifiers: 2 }, { modifiers: 4 }, { modifiers: 8 }]) {
        await key("ArrowRight", extras);
        assert.equal((await snapshot()).hash, "#kit");
      }
      // Real focused inputs, editable content and viewer-like widgets retain arrows.
      for (const markup of ['<input>', '<textarea></textarea>', '<select><option>a</option><option>b</option></select>', '<div contenteditable="true">edit</div>', '<button>button</button>', '<a href="#kit">link</a>', '<div role="slider" tabindex="0">viewer</div>', '<div style="width:80px;overflow-x:auto" tabindex="0"><div style="width:400px">scroll</div></div>']) {
        await evaluate(`(()=>{const holder=document.createElement('div');holder.id='keyboard-probe';holder.innerHTML=${JSON.stringify(markup)};document.querySelector('#kit').append(holder);holder.firstElementChild.focus();})()`);
        await key("ArrowRight");
        assert.equal((await snapshot()).hash, "#kit");
        await evaluate("document.getElementById('keyboard-probe').remove()");
      }
      // Selection, composition and consumed events are guarded by the shipped handler.
      await evaluate("document.querySelector('#kit h2').focus();const range=document.createRange();range.selectNodeContents(document.querySelector('#kit h2'));getSelection().removeAllRanges();getSelection().addRange(range)");
      await key("ArrowRight");
      assert.equal((await snapshot()).hash, "#kit");
      await evaluate("getSelection().removeAllRanges()");
      for (const extra of ['isComposing:true', 'repeat:true']) {
        await evaluate(`document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true,cancelable:true,${extra}}))`);
        assert.equal((await snapshot()).hash, "#kit");
      }
      await evaluate("(()=>{const e=new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true,cancelable:true});e.preventDefault();document.activeElement.dispatchEvent(e)})()");
      assert.equal((await snapshot()).hash, "#kit");
      // Deep fragment restoration and bottom-of-document indication.
      await send("Page.navigate", { url: route + "#extension" });
      await waitFor("document.querySelector('[data-participant-navigation]')?.dataset.navigationReady === 'true'");
      await delay(350);
      assert.equal((await snapshot()).counter, "9/10");
      await evaluate("scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'})");
      await delay(200);
      assert.equal((await snapshot()).counter, "10/10");
      const screenshot = await send("Page.captureScreenshot", { format: "png" });
      await writeFile(path.join(output, screen + "-" + routes.indexOf(route) + ".png"), Buffer.from(screenshot.data, "base64"));
      results.push({ screen, route: route.startsWith("file:") ? "disk-" + routes.indexOf(route) : "online-" + routes.indexOf(route), status: "PASS" });
    }
  }
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "no-preference" }] });
  await send("Page.navigate", { url: routes[0] + "#top" });
  await waitFor("document.querySelector('[data-participant-navigation]')?.dataset.navigationReady === 'true'");
  await evaluate("document.querySelector('nav a[href=\"#brief\"]').click()");
  await delay(900);
  assert.equal((await snapshot()).counter, "2/10");
  assert.equal((await snapshot()).focus, "brief");
  results.push({ route: "online-smooth-motion", status: "PASS" });
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
  // Ordinary named anchors and sticky CSS work with no JavaScript.
  await send("Page.navigate", { url: "about:blank" });
  await delay(100);
  await send("Emulation.setScriptExecutionDisabled", { value: true });
  await send("Page.navigate", { url: routes[3] + "#scoring" });
  await delay(400);
  assert.equal(await evaluate("document.querySelector('.participant-section-controls').hidden"), true);
  assert.equal(await evaluate("getComputedStyle(document.querySelector('header')).position"), "sticky");
  assert.equal(await evaluate("document.querySelector('nav a[href=\"#scoring\"]').hash"), "#scoring");
  const nativeLink = await evaluate("(()=>{const link=document.querySelector('nav a[href=\"#kit\"]');link.scrollIntoView({block:'nearest',inline:'center',behavior:'instant'});const r=link.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()");
  await send("Input.dispatchMouseEvent", { type: "mousePressed", button: "left", clickCount: 1, ...nativeLink });
  await send("Input.dispatchMouseEvent", { type: "mouseReleased", button: "left", clickCount: 1, ...nativeLink });
  await delay(200);
  assert.equal(await evaluate("location.hash"), "#kit");
  assert.ok(await evaluate("document.querySelector('#kit h2').getBoundingClientRect().top >= document.querySelector('header').getBoundingClientRect().bottom"));
  await send("Emulation.setScriptExecutionDisabled", { value: false });
  results.push({ route: "disk-no-javascript", status: "PASS" });
  await writeFile(path.join(output, "results.json"), JSON.stringify(results, null, 2));
  console.log(`PASS: ${results.length} real-browser routes/viewports, focus/history/guards and no-JavaScript fallback`);
} finally {
  if (send) { try { await send("Browser.close"); } catch { /* Browser exit can close its socket first. */ } }
  socket?.close();
  child.kill();
  server.closeAllConnections();
  server.close();
}
