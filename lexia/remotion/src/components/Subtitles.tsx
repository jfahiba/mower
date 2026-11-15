import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { easeIn, easeOut, mix, prog } from "../lib/anim";
import { Capsule, Cue } from "../lib/data";
import { COLORS, FONTS, TEXT_SHADOW, W } from "../lib/theme";

// Sous-titres FR incrustés : lecture progressive, mots-clés en serif italique azur.
const CueView: React.FC<{ cue: Cue; frame: number; hidden: boolean }> = ({ cue, frame, hidden }) => {
  const pin = prog(frame, cue.displayStart, 7, easeOut);
  const pout = prog(frame, cue.displayEnd - 5, 6, easeIn);
  const op = pin * (1 - pout) * (hidden ? 0 : 1);
  if (op <= 0.001) return null;
  const br = cue.lineBreak;
  const idx = cue.words.map((_, i) => i);
  const lines = br > 0 ? [idx.slice(0, br), idx.slice(br)] : [idx];
  const longest = Math.max(...lines.map((l) => l.map((i) => cue.words[i].text).join(" ").length));
  const fit = Math.max(0.82, Math.min(1, 26 / longest));
  return (
    <div style={{ position: "absolute", left: (W - 1900) / 2, width: 1900, bottom: 740, textAlign: "center", fontFamily: FONTS.sans, fontWeight: 650,
      fontSize: 120 * fit, lineHeight: 1.2, letterSpacing: "-0.012em", color: COLORS.white, textShadow: TEXT_SHADOW, opacity: op, transform: `translateY(${mix(20, 0, pin)}px)` }}>
      {lines.map((l, li) => (
        <div key={li} style={{ whiteSpace: "nowrap" }}>
          {l.map((i, k) => {
            const w = cue.words[i];
            const spoken = frame >= w.start - 1;
            const emph = cue.emphasis[i];
            const pop = emph ? prog(frame, w.start - 1, 8, easeOut) : 1;
            return (
              <React.Fragment key={i}>
                <span style={{ display: "inline-block", whiteSpace: "nowrap", opacity: spoken ? 1 : 0.55,
                  ...(emph ? { fontFamily: FONTS.serif, fontStyle: "italic", fontWeight: 400, fontSize: "1.2em", letterSpacing: 0, color: COLORS.ice,
                    transform: `scale(${spoken ? mix(1.07, 1, pop) : 1})` } : {}) }}>
                  {w.text}
                </span>
                {k < l.length - 1 ? " " : ""}
              </React.Fragment>
            );
          })}
        </div>
      ))}
    </div>
  );
};

export const Subtitles: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      {cap.cues.map((c, i) => (frame < c.displayStart - 1 || frame > c.displayEnd + 1 ? null : <CueView key={i} cue={c} frame={frame} hidden={false} />))}
    </AbsoluteFill>
  );
};
