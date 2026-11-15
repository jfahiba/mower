// Images clés : node scripts/stills.mjs <ID> <scale> <frame...>
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
const [id, scale, ...frames] = process.argv.slice(2);
fs.mkdirSync("out/stills", { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id, inputProps: {} });
for (const f of frames.map(Number)) {
  await renderStill({ composition, serveUrl, frame: f, output: path.resolve(`out/stills/${id}_${f}.jpg`), imageFormat: "jpeg", jpegQuality: 90, scale: Number(scale) });
}
fs.rmSync(serveUrl, { recursive: true, force: true });
console.log("ok");
