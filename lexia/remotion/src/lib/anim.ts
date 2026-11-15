import { Easing, interpolate } from "remotion";

export const clamp01 = (x: number) => Math.min(1, Math.max(0, x));

// Courbes de mouvement « éditoriales » : départs nets, arrivées très douces.
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeIn = Easing.bezier(0.7, 0, 0.84, 0);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

/** Progression 0→1 entre `start` et `start + dur` (images), bornée. */
export const prog = (
  frame: number,
  start: number,
  dur: number,
  easing: (t: number) => number = easeOut,
) =>
  interpolate(frame, [start, start + Math.max(1e-3, dur)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

/** Enveloppe d'apparition/disparition : 0 → 1 → 0. */
export const inOut = (
  frame: number,
  from: number,
  to: number,
  fadeIn = 8,
  fadeOut = 8,
) => {
  const a = prog(frame, from, fadeIn, easeOut);
  const b = 1 - prog(frame, to - fadeOut, fadeOut, easeIn);
  return Math.min(a, b);
};

export const mix = (a: number, b: number, t: number) => a + (b - a) * t;

/** Pseudo-aléatoire déterministe (rendu reproductible image par image). */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};
