import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { easeIn, easeOut, prog, rand } from "../lib/anim";
import { TL } from "../lib/timeline";

/** Dégradé bas de cadre (lisibilité des sous-titres) pendant le message. */
export const BottomShade: React.FC = () => {
  const f = useCurrentFrame();
  const o = prog(f, TL.message.videoIn - 6, 14) * (1 - prog(f, TL.endCard.tlFrom, 16, easeIn));
  if (o <= 0) return null;
  return (
    <AbsoluteFill
      style={{
        opacity: o,
        background:
          "linear-gradient(180deg, rgba(12,4,7,0) 50%, rgba(12,4,7,0.28) 68%, rgba(12,4,7,0.46) 86%, rgba(12,4,7,0.52) 100%)",
      }}
    />
  );
};

/** Vignettage doux (profondeur, regard guidé vers le centre). */
export const Vignette: React.FC<{ amount: number }> = ({ amount }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse 78% 62% at 50% 44%, rgba(0,0,0,0) 56%, rgba(0,0,0,${0.42 * amount}) 100%)`,
    }}
  />
);

/** Grain argentique fin, animé (texture organique, masque le lissage de l'agrandissement).
 *  4 textures pleine image (2304x3968) décalées aléatoirement à chaque image. */
export const Grain: React.FC<{ opacity: number }> = ({ opacity }) => {
  const f = useCurrentFrame();
  if (opacity <= 0) return null;
  const tile = Math.floor(rand(f * 1.7) * 4);
  const ox = Math.floor(rand(f * 3.3 + 1) * 144);
  const oy = Math.floor(rand(f * 5.1 + 2) * 128);
  return (
    <AbsoluteFill style={{ overflow: "hidden", mixBlendMode: "overlay", opacity }}>
      <Img
        src={staticFile(`grain/grain_full${tile}.jpg`)}
        style={{ position: "absolute", left: -ox, top: -oy, width: 2304, height: 3968 }}
      />
    </AbsoluteFill>
  );
};

/** Flashs lumineux : impact (blanc chaud) et raccord (halo léger). */
export const Flashes: React.FC = () => {
  const f = useCurrentFrame();
  const fi = TL.impactFrame;
  const fm = TL.message.videoIn;
  const impact = f >= fi && f < fi + 9 ? 0.72 * (1 - prog(f, fi, 8, easeOut)) : 0;
  const match = f >= fm - 1 && f < fm + 10 ? 0.22 * (1 - prog(f, fm - 1, 10, easeOut)) : 0;
  const o = Math.max(impact, match);
  if (o <= 0.001) return null;
  return <AbsoluteFill style={{ backgroundColor: "#FFF1DC", mixBlendMode: "screen", opacity: o }} />;
};

/** Ouverture au noir et fermeture au noir. */
export const Fades: React.FC = () => {
  const f = useCurrentFrame();
  const fin = 1 - prog(f, 0, 10, easeOut);
  const fout = prog(f, TL.durationInFrames - 16, 15, easeIn);
  const o = Math.max(fin, fout);
  if (o <= 0.001) return null;
  return <AbsoluteFill style={{ backgroundColor: "black", opacity: o }} />;
};
