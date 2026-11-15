import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { easeInOut, mix, prog } from "../lib/anim";
import { COLORS, FONTS, TEXT_SHADOW, W } from "../lib/theme";
import { TL } from "../lib/timeline";
import { Sparkles, StaggerText } from "./Typography";

export type EndCardText = {
  kicker: string;
  title: string;
  tagline: string;
  cta: string;
  details: string;
};

// Carton final : l'image du message se floute sous un voile bordeaux, puis le
// titre de l'événement, la devise et l'appel à l'inscription apparaissent.
export const EndCard: React.FC<{ text: EndCardText }> = ({ text }) => {
  const f = useCurrentFrame();
  const from = TL.endCard.tlFrom;
  if (f < from) return null;
  const veil = prog(f, from, 22, easeInOut);
  const pk = prog(f, from + 8, 14);
  const pl = prog(f, from + 14, 18);
  const pt = prog(f, from + 30, 14);
  const pc = prog(f, from + 40, 16);
  const pd = prog(f, from + 48, 14);
  const [ctaA, ctaB] = text.cta.includes("—") ? text.cta.split("—").map((s) => s.trim()) : [text.cta, ""];
  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          opacity: veil,
          background:
            "radial-gradient(ellipse 90% 60% at 50% 46%, rgba(58,16,26,0.62) 0%, rgba(30,8,14,0.82) 55%, rgba(12,4,7,0.94) 100%)",
        }}
      />
      <Sparkles frame={f} from={from + 10} to={TL.durationInFrames + 20} count={42} area={{ x: 200, y: 1200, w: W - 400, h: 1500 }} seed={21} intensity={0.85} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: 120 }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center" }}>
          <div
            style={{
              fontFamily: FONTS.sans,
              fontWeight: 600,
              fontSize: 66,
              letterSpacing: `${mix(0.6, 0.4, pk)}em`,
              paddingLeft: "0.4em",
              textTransform: "uppercase",
              color: COLORS.gold,
              opacity: pk,
              textShadow: TEXT_SHADOW,
            }}
          >
            {text.kicker}
          </div>
          <div style={{ height: 30 }} />
          <div
            style={{
              fontFamily: FONTS.serif,
              fontStyle: "italic",
              fontSize: 282,
              lineHeight: 1.04,
              color: COLORS.white,
              textShadow: `${TEXT_SHADOW}, 0 0 70px rgba(235,201,143,0.28)`,
              whiteSpace: "nowrap",
            }}
          >
            <StaggerText text={text.title} start={from + 12} frame={f} stagger={1.1} dur={16} />
          </div>
          <div style={{ height: 26 }} />
          <div
            style={{
              width: mix(0, 300, pl),
              height: 3,
              background: `linear-gradient(90deg, rgba(235,201,143,0), ${COLORS.gold} 20%, ${COLORS.gold} 80%, rgba(235,201,143,0))`,
              boxShadow: "0 0 18px rgba(235,201,143,0.45)",
            }}
          />
          <div style={{ height: 44 }} />
          <div
            style={{
              fontFamily: FONTS.sans,
              fontWeight: 500,
              fontSize: 60,
              letterSpacing: "0.03em",
              color: COLORS.cream,
              opacity: pt * 0.92,
              transform: `translateY(${mix(18, 0, pt)}px)`,
              textShadow: TEXT_SHADOW,
              whiteSpace: "nowrap",
            }}
          >
            {text.tagline}
          </div>
          <div style={{ height: 120 }} />
          <div
            style={{
              fontFamily: FONTS.serif,
              fontSize: 124,
              lineHeight: 1.16,
              color: COLORS.cream,
              opacity: pc,
              transform: `translateY(${mix(22, 0, pc)}px)`,
              textShadow: TEXT_SHADOW,
            }}
          >
            {ctaA}
            {ctaB ? (
              <>
                <br />
                <span style={{ fontStyle: "italic", color: COLORS.gold }}>{ctaB}</span>
              </>
            ) : null}
          </div>
          {text.details ? (
            <>
              <div style={{ height: 50 }} />
              <div
                style={{
                  fontFamily: FONTS.sans,
                  fontWeight: 600,
                  fontSize: 54,
                  letterSpacing: "0.06em",
                  color: COLORS.white,
                  opacity: pd,
                  textShadow: TEXT_SHADOW,
                }}
              >
                {text.details}
              </div>
            </>
          ) : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
