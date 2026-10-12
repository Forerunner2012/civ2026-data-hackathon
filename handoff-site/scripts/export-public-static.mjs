import { cp, mkdir, readdir, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const outputArgument = process.argv[2];
if (!outputArgument) {
  throw new Error("usage: export-public-static.mjs OUTPUT_DIRECTORY");
}

const projectRoot = fileURLToPath(new URL("..", import.meta.url));
const outputRoot = path.resolve(process.cwd(), outputArgument);
try {
  await stat(outputRoot);
  throw new Error("static export output must not already exist");
} catch (error) {
  if (error?.code !== "ENOENT") throw error;
}

const workerUrl = pathToFileURL(path.join(projectRoot, "dist/server/index.js"));
workerUrl.searchParams.set("static-export", `${process.pid}`);
const { default: worker } = await import(workerUrl.href);

async function render(route) {
  const response = await worker.fetch(
    new Request(`http://localhost${route}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
  if (response.status !== 200) throw new Error(`${route} rendered ${response.status}`);
  return response.text();
}

function staticHtml(source, prefix, participantTarget) {
  return source
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, "")
    .replace(/<link\b[^>]*rel=["'](?:modulepreload|preload)["'][^>]*>/gi, "")
    .replaceAll('href="/assets/', `href="${prefix}assets/`)
    .replaceAll('href="/desk/', `href="${prefix}desk/`)
    .replaceAll('href="/favicon.svg"', `href="${prefix}favicon.svg"`)
    .replaceAll('href="/participants"', `href="${participantTarget}"`)
    .replaceAll('href="/"', `href="${prefix}index.html"`)
    .replace('</body>', `<script defer src="${prefix}participant-navigation.js" data-participant-navigation-script data-offline-navigation></script></body>`);
}

await mkdir(outputRoot, { recursive: false });
const clientRoot = path.join(projectRoot, "dist/client");
for (const name of ["assets", "desk", "favicon.svg", "session-fallback.html", "participant-navigation.js"]) {
  await cp(path.join(clientRoot, name), path.join(outputRoot, name), { recursive: true, filter: (source) => name !== "assets" || !/\.(?:[cm]?js|map)$/i.test(source) });
}

const rootHtml = staticHtml(await render("/"), "", "participants/index.html");
const participantHtml = staticHtml(await render("/participants"), "../", "index.html");
await writeFile(path.join(outputRoot, "index.html"), rootHtml, "utf8");
await mkdir(path.join(outputRoot, "participants"));
await writeFile(path.join(outputRoot, "participants/index.html"), participantHtml, "utf8");

const files = [];
async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) await walk(absolute);
    else files.push(path.relative(outputRoot, absolute).replaceAll(path.sep, "/"));
  }
}
await walk(outputRoot);
files.sort();
await writeFile(path.join(outputRoot, "STATIC-FILES.txt"), `${files.join("\n")}\n`, "utf8");
