import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { easeIn, easeOut, mix, prog } from "../lib/anim";
import { COLORS, FONTS, TEXT_SHADOW, W } from "../lib/theme";
import { Cue, TL } from "../lib/timeline";

// Sous-titres FR incrustés : phrase entière visible, lecture progressive
// (mot prononcé = 100 %, mots à venir = 55 %), mots-clés en serif italique doré
// avec une légère impulsion au moment où ils sont dits.
// Position : bas de cadre (≈ 70–77 % de la hauteur), sous le visage (≈ 30 %),
// au-dessus de la zone d'interface des réseaux sociaux.

const BOTTOM = 740; // px depuis le bas (2160x3840)
const SIZE = 120; // ≈ 5,6 % de la largeur : lisible sur téléphone comme sur grand écran

// Indices des sous-titres remplacés par un moment typographique (mêmes mots).
const suppressed = (() => {
  const s = new Set<number>();
  [0, 1, 2].forEach((i) => s.add(i)); // triptyque
  const ev = TL.cues.findIndex((c) => c.text.toLowerCase().startsWith("le souper de noël"));
  if (ev >= 0) s.add(ev);
  s.add(TL.cues.length - 1); // « À très vite ! »
  return s;
})();

const CueView: React.FC<{ cue: Cue; frame: number }> = ({ cue, frame }) => {
  const pin = prog(frame, cue.displayStart, 7, easeOut);
  const pout = prog(frame, cue.displayEnd - 5, 6, easeIn);
  const op = pin * (1 - pout);
  if (op <= 0.001) return null;
  // lignes éditoriales calculées par le pipeline (coupure après virgule, etc.)
  const br = cue.lineBreak ?? -1;
  const idx = cue.words.map((_, i) => i);
  const lines = br > 0 ? [idx.slice(0, br), idx.slice(br)] : [idx];
  const longest = Math.max(...lines.map((l) => l.map((i) => cue.words[i].text).join(" ").length));
  const fit = Math.min(1, 26 / Math.max(1, longest)); // réduit les lignes très longues (≥ 0,85)
  const renderWord = (i: number) => {
    const w = cue.words[i];
    const spoken = frame >= w.start - 1;
    const emph = cue.emphasis[i];
    const pop = emph ? prog(frame, w.start - 1, 8, easeOut) : 1;
    const style: React.CSSProperties = emph
      ? {
          fontFamily: FONTS.serif,
          fontStyle: "italic",
          fontWeight: 400,
          fontSize: "1.2em",
          letterSpacing: "0",
          color: COLORS.gold,
          transform: `scale(${spoken ? mix(1.07, 1, pop) : 1})`,
        }
      : {};
    return (
      <span key={i} style={{ display: "inline-block", whiteSpace: "nowrap", opacity: spoken ? 1 : 0.55, ...style }}>
        {w.text}
      </span>
    );
  };
  return (
    <div
      style={{
        position: "absolute",
        left: (W - 1900) / 2,
        width: 1900,
        bottom: BOTTOM,
        textAlign: "center",
        fontFamily: FONTS.sans,
        fontWeight: 650,
        fontSize: SIZE * Math.max(0.85, fit),
        lineHeight: 1.2,
        letterSpacing: "-0.012em",
        color: COLORS.white,
        textShadow: TEXT_SHADOW,
        opacity: op,
        transform: `translateY(${mix(20, 0, pin)}px)`,
      }}
    >
      {lines.map((l, li) => (
        <div key={li} style={{ whiteSpace: "nowrap" }}>
          {l.map((i, k) => (
            <React.Fragment key={i}>
              {renderWord(i)}
              {k < l.length - 1 ? " " : ""}
            </React.Fragment>
          ))}
        </div>
      ))}
    </div>
  );
};

export const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      {TL.cues.map((c, i) =>
        suppressed.has(i) || frame < c.displayStart - 1 || frame > c.displayEnd + 1 ? null : (
          <CueView key={i} cue={c} frame={frame} />
        ),
      )}
    </AbsoluteFill>
  );
};
