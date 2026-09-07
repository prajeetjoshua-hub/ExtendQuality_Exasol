import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

export function patchVinextWindowsStaticPaths() {
  if (process.platform !== "win32") return false;

  const target = path.resolve("node_modules/vinext/dist/server/static-file-cache.js");
  const source = readFileSync(target, "utf8");
  const vulnerable = "relativePath: path.relative(base, batch[j]),";
  const fixed = 'relativePath: path.relative(base, batch[j]).split(path.sep).join("/"),';
  if (source.includes(fixed)) return false;
  if (!source.includes(vulnerable)) {
    throw new Error("Unsupported vinext static-file cache version; Windows compatibility patch was not applied.");
  }
  writeFileSync(target, source.replace(vulnerable, fixed), "utf8");
  return true;
}
