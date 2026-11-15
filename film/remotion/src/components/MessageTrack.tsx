import { Video } from "@remotion/media";
import { blur } from "@remotion/effects/blur";
import { zoomBlur } from "@remotion/effects/zoom-blur";
import React from "react";
import { AbsoluteFill, Freeze, Sequence, staticFile, useCurrentFrame } from "remotion";
import { clamp01, easeInOut, easeOut, mix, prog } from "../lib/anim";
import { TL } from "../lib/timeline";

const MATCH_IN = 11; // images de l'entrée par zoom depuis le tableau

// Ancrage de chaque cadrage sur la position moyenne du visage pendant sa durée
// (constante par plan : aucun tremblement de recadrage).
const ANCHORS = TL.framing.map((fr, i) => {
  const end = i + 1 < TL.framing.length ? TL.framing[i + 1].tlFrom : TL.durationInFrames;
  const pts = TL.faceTrack.filter((p) => p.tl >= fr.tlFrom && p.tl < end);
  const cx = pts.length ? pts.reduce((a, p) => a + p.cx, 0) / pts.length : 0.55;
  const cy = pts.length ? pts.reduce((a, p) => a + p.cy, 0) / pts.length : 0.3;
  return { cx, cy, end };
});

type Frame = { scale: number; origin: [number, number]; dx: number };

/** Cadrage (punch-in + push lent + recentrage horizontal borné) à l'image f. */
const framingAt = (f: number): Frame => {
  let i = 0;
  for (let k = 0; k < TL.framing.length; k++) if (TL.framing[k].tlFrom <= f) i = k;
  const fr = TL.framing[i];
  const an = ANCHORS[i];
  const p = clamp01((f - fr.tlFrom) / Math.max(1, an.end - fr.tlFrom));
  const s = fr.scale * (1 + fr.push * p);
  const ox = an.cx;
  const oy = an.cy;
  // recentrer le visage vers x = 0,5 sans jamais découvrir les bords
  const dxMin = (1 - ox) * (1 - s);
  const dxMax = ox * (s - 1);
  const dx = Math.min(dxMax, Math.max(dxMin, (0.5 - ox) * 0.85));
  return { scale: s, origin: [ox, oy], dx };
};

export const MessageTrack: React.FC = () => {
  const f = useCurrentFrame();
  const { videoIn, segments, end } = TL.message;
  if (f < videoIn) return null;

  // cadrage + entrée « match zoom » depuis le tableau de coquelicots
  const fr = framingAt(f);
  const pm = prog(f, videoIn, MATCH_IN, easeOut);
  const pa = TL.paintingAnchorMsg;
  const scale = mix(1.38, fr.scale, pm);
  const origin: [number, number] = [mix(pa[0], fr.origin[0], pm), mix(pa[1], fr.origin[1], pm)];
  const dx = mix(0, fr.dx, pm);
  const zAmount = mix(170, 0, pm);

  // flou progressif sous le carton final, calculé au quart de la résolution
  // (effectsOutputSize) : rendu identique pour un flou aussi fort, ~60x moins coûteux.
  const endBlur = 70 * prog(f, TL.endCard.tlFrom, 24, easeInOut);
  const lowRes = endBlur > 0.5 && zAmount <= 0.5;

  const effects = [
    ...(zAmount > 0.5 ? [zoomBlur({ amount: zAmount, center: pa, samples: 32 })] : []),
    ...(endBlur > 0.5 ? [blur({ radius: lowRes ? endBlur / 4 : endBlur })] : []),
  ];
  const effectsOutputSize = lowRes ? { width: 540, height: 960 } : undefined;

  const last = segments[segments.length - 1];
  return (
    <AbsoluteFill
      style={{
        transform: `translate(${dx * 100}%, 0) scale(${scale})`,
        transformOrigin: `${origin[0] * 100}% ${origin[1] * 100}%`,
      }}
    >
      {segments.map((s, i) => {
        const vFrom = Math.max(s.tlFrom, videoIn);
        const dur = s.tlTo - vFrom;
        if (dur <= 0) return null;
        return (
          <Sequence key={i} from={vFrom} durationInFrames={dur} name={`message · segment ${i + 1}`}>
            <Video
              src={staticFile(TL.message.file)}
              trimBefore={s.srcFrom + (vFrom - s.tlFrom)}
              muted
              objectFit="cover"
              style={{ width: "100%", height: "100%" }}
              effects={effects}
              effectsOutputSize={effectsOutputSize}
            />
          </Sequence>
        );
      })}
      {/* après la fin du message : dernière image figée (sous le carton, floutée) */}
      <Sequence from={end} durationInFrames={Math.max(1, TL.durationInFrames - end)} name="message · image figée">
        <Freeze frame={0}>
          <Video
            src={staticFile(TL.message.file)}
            trimBefore={last.srcTo - 1}
            muted
            objectFit="cover"
            style={{ width: "100%", height: "100%" }}
            effects={effects}
            effectsOutputSize={effectsOutputSize}
          />
        </Freeze>
      </Sequence>
    </AbsoluteFill>
  );
};
