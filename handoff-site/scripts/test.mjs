import { spawn } from "node:child_process";

const testEnvironment = {
  ...process.env,
  LIVE_ALLOW_CONTROLLED_CLOCK: "true",
  LIVE_COACH_TOKEN: "test-coach-token",
  POST_EVENT_SOLUTIONS_RELEASED: "true",
  SUBMISSION_FORM_URL: "https://forms.example.test/civ-phase1",
};
const noFormEnvironment = { ...testEnvironment };
delete noFormEnvironment.SUBMISSION_FORM_URL;

function run(arguments_, environment = process.env) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, arguments_, {
      env: environment,
      stdio: "inherit",
    });
    child.on("error", reject);
    child.on("exit", (code, signal) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(new Error(`node ${arguments_.join(" ")} exited with ${code ?? signal}`));
    });
  });
}

await run(["scripts/build-audience.mjs", "internal"], testEnvironment);
await run(
  [
    "--experimental-strip-types",
    "--test",
    "tests/live-state.test.ts",
    "tests/live-rendered.test.mjs",
    "tests/organizer-pack-rendered.test.mjs",
  ],
  testEnvironment,
);
await run(["scripts/build-audience.mjs", "internal"], noFormEnvironment);
await run(
  ["--experimental-strip-types", "--test", "tests/live-rendered.test.mjs", "tests/organizer-pack-rendered.test.mjs"],
  noFormEnvironment,
);
await run(["scripts/build-audience.mjs", "public"]);
await run(["--test", "tests/rendered-html.test.mjs", "tests/print-materials.test.mjs"]);
