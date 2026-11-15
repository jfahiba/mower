import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [id, ...frames] = process.argv.slice(2);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id, inputProps: {} });
for (const f of frames.map(Number)) {
  await renderStill({ composition, serveUrl, frame: f, output: path.resolve(`out/dbg_${id}_${f}.png`), scale: 0.25 });
}
console.log("ok");
