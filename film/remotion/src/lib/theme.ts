// Direction artistique : « premium éditorial » chaud — bordeaux, or champagne, crème.
export const W = 2160;
export const H = 3840;

export const COLORS = {
  white: "#FFFFFF",
  cream: "#F7EFE4",
  gold: "#EBC98F", // accent champagne (contraste ≥ 7:1 sur le bordeaux de la robe)
  goldDeep: "#C9995A",
  ink: "#120709",
  burgundy: "#2B0B13",
};

export const FONTS = {
  serif: "Instrument Serif",
  sans: "Inter",
};

// Zones de sécurité verticales (interfaces TikTok / Reels / Shorts)
export const SAFE = {
  side: Math.round(W * 0.09),
  top: Math.round(H * 0.1),
  bottom: Math.round(H * 0.2),
};

// Lisibilité des textes posés sur l'image
export const TEXT_SHADOW =
  "0 4px 24px rgba(10,3,5,0.55), 0 2px 6px rgba(10,3,5,0.45)";
