// Prévisualisation : rend des images clés (bundle unique) puis une planche.
// Usage : node scripts/stills.mjs [scale] [frame ...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const scale = args.length ? Number(args[0]) : 0.25;
const frames = args.length > 1 ? args.slice(1).map(Number) : [
  30, 75, 118, 121, 178, 182, 238, 243, 270, 300, 352, 361, 364, 420, 452, 456, 460, 466,
  490, 560, 640, 720, 760, 930, 950, 975, 1100, 1300, 1450, 1600, 1735, 1760, 1790, 1830, 1870,
];
const out = path.resolve("out/stills");
fs.mkdirSync(out, { recursive: true });

const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "Film", inputProps: {} });
const t0 = Date.now();
for (const frame of frames) {
  await renderStill({
    composition,
    serveUrl,
    output: path.join(out, `f${String(frame).padStart(4, "0")}.jpg`),
    frame,
    imageFormat: "jpeg",
    jpegQuality: 90,
    scale,
    chromiumOptions: { gl: "swangle" },
  });
  process.stdout.write(`${frame} `);
}
console.log(`\n${frames.length} images en ${((Date.now() - t0) / 1000).toFixed(1)} s`);
