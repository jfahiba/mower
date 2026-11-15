import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import { FONTS } from "./theme";

// Polices locales (SIL OFL 1.1) — loadFont() bloque le rendu jusqu'au chargement.
export const fontsReady = Promise.all([
  loadFont({
    family: FONTS.sans,
    url: staticFile("fonts/inter-latin-wght-normal.woff2"),
    weight: "100 900",
    style: "normal",
  }),
  loadFont({
    family: FONTS.serif,
    url: staticFile("fonts/instrument-serif-latin-400-normal.woff2"),
    weight: "400",
    style: "normal",
  }),
  loadFont({
    family: FONTS.serif,
    url: staticFile("fonts/instrument-serif-latin-400-italic.woff2"),
    weight: "400",
    style: "italic",
  }),
]);
