import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { easeIn, easeOut, inOut, mix, prog, rand } from "../lib/anim";
import { Capsule, DATA } from "../lib/data";
import { COLORS, FONTS, TEXT_SHADOW, W } from "../lib/theme";

const Glass: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      background: "linear-gradient(160deg, rgba(11,26,46,0.82), rgba(19,43,72,0.74))",
      border: "3px solid rgba(56,168,236,0.55)",
      borderRadius: 48,
      boxShadow: "0 30px 80px rgba(2,8,18,0.45), inset 0 0 60px rgba(56,168,236,0.10)",
      padding: "56px 72px",
      ...style,
    }}
  >
    {children}
  </div>
);

const Kicker: React.FC<{ text: string; color?: string; size?: number }> = ({ text, color = COLORS.ice, size = 50 }) => (
  <div style={{ fontFamily: FONTS.sans, fontWeight: 600, fontSize: size, letterSpacing: "0.3em", textTransform: "uppercase", color }}>{text}</div>
);

/** Cartons titre (haut de cadre) : un par capsule, ou un par chapitre dans le montage complet. */
export const TitleCard: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const f = useCurrentFrame();
  const chapters = cap.chapters ?? [{ n: 0, tlFrom: 0, title: cap.title }];
  const total = cap.chapters ? cap.chapters.length : 0;
  return (
    <>
      {chapters.map((ch) => {
        const qEnd = Math.max(0, ...cap.questions.filter((q) => q.tlFrom >= ch.tlFrom && q.tlFrom < ch.tlFrom + 30).map((q) => Math.min(q.tlTo, ch.tlFrom + 150)));
        const from = ch.tlFrom + 4;
        const to = Math.max(ch.tlFrom + 100, qEnd);
        const o = inOut(f, from, to, 14, 12);
        if (o <= 0) return null;
        const p = prog(f, from, 18);
        return (
          <AbsoluteFill key={ch.tlFrom} style={{ alignItems: "center", top: 300 }}>
            <div style={{ opacity: o, transform: `translateY(${mix(-40, 0, p)}px)`, width: W - 240 }}>
              <Glass style={{ textAlign: "center" }}>
                <Kicker text={total ? `Me Rania Arbi répond · ${String(ch.n).padStart(2, "0")}/${String(total).padStart(2, "0")}` : "Me Rania Arbi répond à vos questions"} size={44} />
                <div style={{ height: 22 }} />
                <div style={{ fontFamily: FONTS.serif, fontStyle: "italic", fontSize: 128, lineHeight: 1.08, color: COLORS.white, textShadow: TEXT_SHADOW }}>{ch.title}</div>
              </Glass>
            </div>
          </AbsoluteFill>
        );
      })}
    </>
  );
};

/** Flash lumineux aux changements de chapitre (montage complet). */
export const ChapterFlash: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const f = useCurrentFrame();
  const b = (cap.chapters ?? []).find((c) => c.tlFrom > 0 && f >= c.tlFrom - 1 && f < c.tlFrom + 8);
  if (!b) return null;
  const o = 0.55 * (1 - prog(f, b.tlFrom - 1, 8, easeOut));
  return <AbsoluteFill style={{ backgroundColor: "#EAF6FF", mixBlendMode: "screen", opacity: o }} />;
};

/** Question posée hors champ : carton en bas de cadre pendant la question. */
export const QuestionCards: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const f = useCurrentFrame();
  return (
    <>
      {cap.questions.map((q, k) => {
        const o = inOut(f, q.tlFrom, q.tlTo + 6, 10, 10);
        if (o <= 0) return null;
        return (
          <AbsoluteFill key={k} style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: 720 }}>
            <div style={{ opacity: o, transform: `translateY(${mix(30, 0, prog(f, q.tlFrom, 14))}px)`, width: W - 260 }}>
              <Glass>
                <Kicker text="Question" color={COLORS.azure} size={48} />
                <div style={{ height: 18 }} />
                <div style={{ fontFamily: FONTS.sans, fontWeight: 600, fontSize: q.text.length > 60 ? 76 : 96, lineHeight: 1.22, color: COLORS.white }}>
                  {q.text}
                </div>
              </Glass>
            </div>
          </AbsoluteFill>
        );
      })}
    </>
  );
};

/** Logo discret en haut à gauche pendant la capsule. */
export const Bug: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const f = useCurrentFrame();
  // masqué pendant les cartons de chapitre (montage complet)
  const hide = Math.max(0, ...(cap.chapters ?? []).filter((c) => c.tlFrom > 0).map((c) => inOut(f, c.tlFrom - 2, c.tlFrom + 112, 8, 12)));
  const o = inOut(f, 96, cap.bodyEnd - 8, 16, 12) * 0.92 * (1 - hide);
  if (o <= 0) return null;
  return <Img src={staticFile("brand/lexia_logo_x3.png")} style={{ position: "absolute", left: 90, top: 300, width: 300, height: 300, opacity: o, filter: "drop-shadow(0 8px 24px rgba(0,0,0,0.35))" }} />;
};

/** Photo de Me Arbi incrustée avec déclic : éclair blanc + tirage photo qui se pose. */
export const Photos: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const f = useCurrentFrame();
  return (
    <>
      {cap.photos.map((p, k) => {
        const t = f - p.tlFrom;
        if (t < -1 || t > p.dur + 2) return null;
        const flash = t >= 0 && t < 6 ? 0.9 * (1 - t / 6) : 0;
        const pin = prog(t, 0, 10, easeOut);
        const pout = prog(t, p.dur - 9, 9, easeIn);
        const rot = (k % 2 ? 3 : -3) * (1 - pout * 0.5) + (rand(k + 3) - 0.5);
        return (
          <AbsoluteFill key={k}>
            <AbsoluteFill style={{ backgroundColor: `rgba(6,14,26,${0.35 * pin * (1 - pout)})` }} />
            <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 560 }}>
              <div
                style={{
                  width: 1340,
                  background: "#FAFAF7",
                  padding: "36px 36px 130px",
                  boxShadow: "0 40px 100px rgba(0,0,0,0.5)",
                  transform: `translateY(${mix(-60, 0, pin) + pout * 220}px) rotate(${rot}deg) scale(${mix(1.1, 1, pin)})`,
                  opacity: pin * (1 - pout),
                }}
              >
                <div style={{ width: 1268, height: 1690, overflow: "hidden" }}>
                  <Img src={staticFile(p.file)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1 + 0.05 * (t / p.dur)})` }} />
                </div>
                <div style={{ fontFamily: FONTS.serif, fontStyle: "italic", fontSize: 76, color: COLORS.navy2, textAlign: "center", marginTop: 34 }}>
                  Me Rania Arbi, notaire
                </div>
              </div>
            </AbsoluteFill>
            {flash > 0 ? <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} /> : null}
          </AbsoluteFill>
        );
      })}
    </>
  );
};

/** Carton final : logo, notaire, coordonnées, bureaux. */
export const EndCard: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const f = useCurrentFrame();
  const from = cap.bodyEnd - 12;
  if (f < from) return null;
  const c = DATA.contact;
  const veil = prog(f, from, 20);
  const pl = prog(f, from + 4, 22, easeOut);
  const p = (d: number) => prog(f, from + d, 14);
  const line = (d: number): React.CSSProperties => ({ opacity: p(d), transform: `translateY(${mix(20, 0, p(d))}px)` });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: veil, background: "radial-gradient(ellipse 95% 65% at 50% 42%, rgba(19,43,72,0.80) 0%, rgba(11,26,46,0.92) 60%, rgba(5,12,22,0.97) 100%)" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: 260, textAlign: "center" }}>
        <Img src={staticFile("brand/lexia_logo_x3.png")} style={{ width: 760, height: 760, opacity: pl, transform: `scale(${mix(0.86, 1, pl)})`, filter: "drop-shadow(0 20px 60px rgba(56,168,236,0.35))" }} />
        <div style={{ height: 60 }} />
        <div style={{ ...line(14), fontFamily: FONTS.serif, fontStyle: "italic", fontSize: 128, color: COLORS.white, textShadow: TEXT_SHADOW }}>{c.person}</div>
        <div style={{ height: 50 }} />
        <div style={{ ...line(22) }}><Kicker text="Pour en savoir plus" color={COLORS.ice} size={50} /></div>
        <div style={{ height: 34 }} />
        <div style={{ ...line(26), fontFamily: FONTS.sans, fontWeight: 650, fontSize: 92, color: COLORS.white }}>{c.email}</div>
        <div style={{ height: 14 }} />
        <div style={{ ...line(30), fontFamily: FONTS.sans, fontWeight: 650, fontSize: 104, color: COLORS.azure, letterSpacing: "0.03em" }}>{c.phone}</div>
        <div style={{ height: 70 }} />
        <div style={{ ...line(36) }}><Kicker text="Nos bureaux" color={COLORS.ice} size={44} /></div>
        <div style={{ height: 20 }} />
        {c.offices.map((o, k) => (
          <div key={k} style={{ ...line(40 + k * 4), fontFamily: FONTS.sans, fontWeight: 500, fontSize: 62, lineHeight: 1.45, color: COLORS.silver }}>{o}</div>
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Finish: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const f = useCurrentFrame();
  const tile = Math.floor(rand(f * 1.7) * 4);
  const fin = 1 - prog(f, 0, 8, easeOut);
  const fout = prog(f, cap.durationInFrames - 14, 13, easeIn);
  const shade = prog(f, 0, 10) * (1 - prog(f, cap.bodyEnd - 12, 14));
  return (
    <>
      <AbsoluteFill style={{ opacity: shade, background: "linear-gradient(180deg, rgba(5,12,22,0) 52%, rgba(5,12,22,0.30) 70%, rgba(5,12,22,0.5) 100%)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 78% 62% at 50% 42%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.36) 100%)" }} />
      <AbsoluteFill style={{ overflow: "hidden", mixBlendMode: "overlay", opacity: 0.06 }}>
        <Img src={staticFile(`grain/grain_full${tile}.jpg`)} style={{ position: "absolute", left: -Math.floor(rand(f * 3.3 + 1) * 144), top: -Math.floor(rand(f * 5.1 + 2) * 128), width: 2304, height: 3968 }} />
      </AbsoluteFill>
      {Math.max(fin, fout) > 0.001 ? <AbsoluteFill style={{ backgroundColor: "black", opacity: Math.max(fin, fout) }} /> : null}
    </>
  );
};
