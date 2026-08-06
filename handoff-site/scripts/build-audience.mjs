import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const audience = process.argv[2];
if (audience !== "internal" && audience !== "public") {
  throw new Error("usage: build-audience.mjs internal|public");
}

const cli = fileURLToPath(new URL("../node_modules/vinext/dist/cli.js", import.meta.url));
const exitCode = await new Promise((resolve, reject) => {
  const child = spawn(process.execPath, [cli, "build"], {
    env: { ...process.env, CIV_BUILD_AUDIENCE: audience },
    stdio: "inherit",
  });
  child.on("error", reject);
  child.on("exit", (code, signal) => resolve(code ?? signal));
});

if (exitCode !== 0) {
  throw new Error(`vinext build exited with ${exitCode}`);
}
