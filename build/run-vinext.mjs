import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { patchVinextWindowsStaticPaths } from "./patch-vinext-windows.mjs";

const allowedCommands = new Set(["dev", "build", "start"]);
const command = process.argv[2];

if (!allowedCommands.has(command)) {
  console.error("Usage: node build/run-vinext.mjs <dev|build|start>");
  process.exit(2);
}

const executable = process.execPath;
if (command === "start" && patchVinextWindowsStaticPaths()) {
  console.log("Applied the vinext Windows static-asset compatibility patch.");
}
const cli = fileURLToPath(new URL("../node_modules/vinext/dist/cli.js", import.meta.url));
const result = spawnSync(executable, [cli, command, ...process.argv.slice(3)], {
  stdio: "inherit",
  env: {
    ...process.env,
    WRANGLER_LOG_PATH: ".wrangler/wrangler.log",
  },
  shell: false,
});

if (result.error) {
  console.error(result.error.message);
  process.exit(1);
}

process.exit(result.status ?? 1);
