import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { easeIn, easeOut, inOut, mix, prog, rand } from "../lib/anim";
import { COLORS, FONTS, TEXT_SHADOW, W } from "../lib/theme";
import { TL } from "../lib/timeline";

// ---------------------------------------------------------------------------
// Petits éléments partagés
// ---------------------------------------------------------------------------
const Kicker: React.FC<{ text: string; size?: number; color?: string; tracking?: number; style?: React.CSSProperties }> = ({
  text,
  size = 62,
  color = "rgba(255,255,255,0.92)",
  tracking = 0.42,
  style,
}) => (
  <div
    style={{
      fontFamily: FONTS.sans,
      fontWeight: 600,
      fontSize: size,
      letterSpacing: `${tracking}em`,
      paddingLeft: `${tracking}em`, // compense l'espacement final (centrage optique)
      textTransform: "uppercase",
      color,
      textShadow: TEXT_SHADOW,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {text}
  </div>
);

const Rule: React.FC<{ width: number; opacity?: number }> = ({ width, opacity = 1 }) => (
  <div
    style={{
      width,
      height: 3,
      background: `linear-gradient(90deg, rgba(235,201,143,0), ${COLORS.gold} 20%, ${COLORS.gold} 80%, rgba(235,201,143,0))`,
      opacity,
      boxShadow: "0 0 18px rgba(235,201,143,0.45)",
    }}
  />
);

/** Révélation lettre par lettre (opacité + montée + flou), décalage de `stagger` images. */
export const StaggerText: React.FC<{
  text: string;
  start: number;
  frame: number;
  stagger?: number;
  dur?: number;
  style?: React.CSSProperties;
}> = ({ text, start, frame, stagger = 1.1, dur = 14, style }) => (
  <span style={{ display: "inline-block", whiteSpace: "pre", ...style }}>
    {Array.from(text).map((ch, i) => {
      const p = prog(frame, start + i * stagger, dur, easeOut);
      return (
        <span
          key={i}
          style={{
            display: "inline-block",
            opacity: p,
            transform: `translateY(${mix(0.28, 0, p)}em)`,
            filter: p < 0.999 ? `blur(${mix(14, 0, p)}px)` : undefined,
          }}
        >
          {ch}
        </span>
      );
    })}
  </span>
);

/** Particules dorées scintillantes (déterministes). */
export const Sparkles: React.FC<{
  frame: number;
  from: number;
  to: number;
  count?: number;
  area: { x: number; y: number; w: number; h: number };
  seed?: number;
  intensity?: number;
}> = ({ frame, from, to, count = 34, area, seed = 1, intensity = 1 }) => {
  if (frame < from - 2 || frame > to + 12) return null;
  const env = inOut(frame, from, to, 14, 14) * intensity;
  return (
    <>
      {Array.from({ length: count }).map((_, i) => {
        const r1 = rand(seed * 100 + i * 7.13);
        const r2 = rand(seed * 200 + i * 3.71);
        const r3 = rand(seed * 300 + i * 9.29);
        const r4 = rand(seed * 400 + i * 1.97);
        const t = frame - from;
        const x = area.x + r1 * area.w + Math.sin(t / 22 + r4 * 6.28) * 14;
        const y = area.y + r2 * area.h - t * (0.6 + r3 * 1.4);
        const size = 10 + r3 * 22;
        const tw = 0.5 + 0.5 * Math.sin(t / (5 + r4 * 6) + r1 * 6.28);
        const delay = r4 * 18;
        const op = env * prog(frame, from + delay, 10) * (0.25 + 0.75 * tw);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: "radial-gradient(circle, #FFF6E2 0%, rgba(235,201,143,0.95) 35%, rgba(235,201,143,0) 72%)",
              boxShadow: `0 0 ${size * 1.6}px rgba(235,201,143,0.55)`,
              opacity: op,
            }}
          />
        );
      })}
    </>
  );
};

// ---------------------------------------------------------------------------
// Étiquettes de chapitre du timelapse : « Tu as porté / ta famille »
// ---------------------------------------------------------------------------
export const ChapterLabels: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {TL.chapters.map((c, i) => {
        if (f < c.tlFrom - 2 || f > c.tlTo + 14) return null;
        const pk = prog(f, c.tlFrom, 12);
        const pl = prog(f, c.tlFrom + 4, 16);
        const pt = prog(f, c.tlFrom + 7, 18);
        const out = prog(f, c.tlTo - 10, 12, easeIn);
        return (
          <AbsoluteFill key={i} style={{ alignItems: "center", top: 2420 }}>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                opacity: 1 - out,
                filter: out > 0.001 ? `blur(${out * 12}px)` : undefined,
                transform: `translateY(${-out * 26}px)`,
              }}
            >
              <Kicker text={c.kicker} style={{ opacity: pk, transform: `translateY(${mix(22, 0, pk)}px)` }} />
              <div style={{ height: 34 }} />
              <Rule width={mix(0, 200, pl)} />
              <div style={{ height: 22 }} />
              <div
                style={{
                  fontFamily: FONTS.serif,
                  fontStyle: "italic",
                  fontSize: 236,
                  lineHeight: 1.05,
                  color: COLORS.white,
                  textShadow: TEXT_SHADOW,
                  clipPath: `inset(${mix(100, -20, pt)}% -10% -20% -10%)`,
                  transform: `translateY(${mix(46, 0, pt)}px)`,
                  filter: pt < 0.999 ? `blur(${mix(10, 0, pt)}px)` : undefined,
                  whiteSpace: "nowrap",
                }}
              >
                {c.title}
              </div>
            </div>
          </AbsoluteFill>
        );
      })}
    </>
  );
};

// ---------------------------------------------------------------------------
// Triptyque d'ouverture du message : « Femme entrepreneur / battante / de foi »
// ---------------------------------------------------------------------------
export const Triad: React.FC = () => {
  const f = useCurrentFrame();
  const m = TL.moments.find((x) => x.kind === "triad");
  if (!m || !m.lines || f < m.tlFrom - 4 || f > m.tlTo + 16) return null;
  const out = prog(f, m.tlTo - 6, 14, easeIn);
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 2350 }}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 8,
          opacity: 1 - out,
          filter: out > 0.001 ? `blur(${out * 14}px)` : undefined,
          transform: `translateY(${-out * 30}px)`,
        }}
      >
        {m.lines.map((ln, i) => {
          const p = prog(f, ln.tl - 3, 13);
          // les lignes déjà dites s'apaisent légèrement quand la suivante arrive
          const next = m.lines![i + 1];
          const dim = next ? prog(f, next.tl - 3, 12) : 0;
          return (
            <div
              key={i}
              style={{
                fontFamily: FONTS.serif,
                fontSize: 180,
                lineHeight: 1.08,
                whiteSpace: "nowrap",
                textShadow: TEXT_SHADOW,
                opacity: p * mix(1, 0.78, dim),
                transform: `translateY(${mix(38, 0, p)}px)`,
                filter: p < 0.999 ? `blur(${mix(12, 0, p)}px)` : undefined,
              }}
            >
              <span style={{ color: COLORS.white }}>{ln.a} </span>
              <span style={{ fontStyle: "italic", color: COLORS.gold }}>{ln.b}</span>
              <span style={{ color: COLORS.white }}>{i < 2 ? "," : "."}</span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Révélation « Le souper de Noël »
// ---------------------------------------------------------------------------
export const EventTitle: React.FC = () => {
  const f = useCurrentFrame();
  const m = TL.moments.find((x) => x.kind === "event");
  if (!m) return null;
  // se retire dès que le sous-titre suivant apparaît
  const ci = TL.cues.findIndex((c) => c.text.toLowerCase().startsWith("le souper de noël"));
  const end = ci >= 0 && TL.cues[ci + 1] ? Math.min(m.tlTo, TL.cues[ci + 1].displayStart + 2) : m.tlTo;
  if (f < m.tlFrom - 4 || f > end + 16) return null;
  const pk = prog(f, m.tlFrom, 14);
  const pl = prog(f, m.tlFrom + 6, 18);
  const out = prog(f, end - 8, 14, easeIn);
  return (
    <AbsoluteFill>
      <Sparkles frame={f} from={m.tlFrom} to={end} count={46} area={{ x: 200, y: 2120, w: W - 400, h: 900 }} seed={7} />
      <AbsoluteFill style={{ alignItems: "center", top: 2330 }}>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            opacity: 1 - out,
            filter: out > 0.001 ? `blur(${out * 14}px)` : undefined,
            transform: `translateY(${-out * 30}px)`,
          }}
        >
          <Kicker
            text={m.kicker ?? ""}
            size={66}
            color={COLORS.gold}
            tracking={mix(0.62, 0.38, pk)}
            style={{ opacity: pk }}
          />
          <div style={{ height: 30 }} />
          <Rule width={mix(0, 280, pl)} />
          <div style={{ height: 18 }} />
          <div
            style={{
              fontFamily: FONTS.serif,
              fontStyle: "italic",
              fontSize: 240,
              lineHeight: 1.04,
              color: COLORS.white,
              textShadow: `${TEXT_SHADOW}, 0 0 60px rgba(235,201,143,0.25)`,
            }}
          >
            <StaggerText text={m.title ?? ""} start={m.tlFrom + 5} frame={f} stagger={1.15} dur={16} />
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Signature « À très vite ! »
// ---------------------------------------------------------------------------
export const Signoff: React.FC = () => {
  const f = useCurrentFrame();
  const m = TL.moments.find((x) => x.kind === "signoff");
  if (!m) return null;
  const end = TL.endCard.tlFrom + 4;
  if (f < m.tlFrom - 4 || f > end + 14) return null;
  const p = prog(f, m.tlFrom - 2, 16);
  const out = prog(f, end - 6, 12, easeIn);
  const title = (m.title ?? "").replace(/\s*!$/, "");
  const words = title.split(" ");
  const lastWord = words.pop();
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 2440 }}>
      <div
        style={{
          fontFamily: FONTS.serif,
          fontStyle: "italic",
          fontSize: 252,
          lineHeight: 1,
          whiteSpace: "nowrap",
          textShadow: TEXT_SHADOW,
          opacity: p * (1 - out),
          transform: `translateY(${mix(40, 0, p) - out * 24}px) scale(${mix(0.96, 1, p)})`,
          filter: p < 0.999 || out > 0.001 ? `blur(${mix(12, 0, p) + out * 12}px)` : undefined,
        }}
      >
        <span style={{ color: COLORS.white }}>{words.join(" ")} </span>
        <span style={{ color: COLORS.gold }}>{lastWord}</span>
        <span style={{ color: COLORS.gold }}>{" !"}</span>
      </div>
    </AbsoluteFill>
  );
};
