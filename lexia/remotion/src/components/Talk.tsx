import { Video } from "@remotion/media";
import { blur } from "@remotion/effects/blur";
import { zoomBlur } from "@remotion/effects/zoom-blur";
import React from "react";
import { AbsoluteFill, Freeze, Sequence, staticFile, useCurrentFrame } from "remotion";
import { clamp01, easeInOut, easeOut, mix, prog } from "../lib/anim";
import { Capsule } from "../lib/data";

// Me Arbi face caméra : jump cuts exacts à l'image, punch-ins « deux caméras »
// ancrés sur le visage, push-in lent, flou doux sous le carton final.
export const Talk: React.FC<{ cap: Capsule }> = ({ cap }) => {
  const f = useCurrentFrame();
  let i = 0;
  cap.framing.forEach((fr, k) => {
    if (fr.tlFrom <= f) i = k;
  });
  const fr = cap.framing[i];
  const end = i + 1 < cap.framing.length ? cap.framing[i + 1].tlFrom : cap.durationInFrames;
  const seg = cap.segments.find((s) => s.tlFrom <= f && f < s.tlTo) ?? cap.segments[cap.segments.length - 1];
  const s = fr.scale * (1 + fr.push * clamp01((f - fr.tlFrom) / Math.max(1, end - fr.tlFrom))) * mix(1.06, 1, prog(f, 0, 24, easeOut));
  // transition « punch » aux changements de chapitre : zoom flouté sortant puis entrant
  const ch = (cap.chapters ?? []).find((c) => c.tlFrom > 0 && f >= c.tlFrom - 6 && f < c.tlFrom + 10);
  let punch = 1;
  let zb = 0;
  if (ch) {
    if (f < ch.tlFrom) {
      const q = prog(f, ch.tlFrom - 6, 6, (x) => x * x);
      punch = mix(1, 1.25, q);
      zb = 150 * q;
    } else {
      const q = prog(f, ch.tlFrom, 10, easeOut);
      punch = mix(1.2, 1, q);
      zb = mix(150, 0, q);
    }
  }
  const sp = s * punch;
  const ox = seg.cx;
  const oy = seg.cy;
  const dx = Math.min(ox * (sp - 1), Math.max((1 - ox) * (1 - sp), (0.5 - ox) * 0.85));
  const endBlur = 70 * prog(f, cap.bodyEnd - 12, 22, easeInOut);
  const effects = endBlur > 0.5 ? [blur({ radius: endBlur / 4 })] : zb > 0.5 ? [zoomBlur({ amount: zb, center: [seg.cx, seg.cy], samples: 24 })] : [];
  const eos = endBlur > 0.5 ? { width: 540, height: 960 } : undefined;
  const last = cap.segments[cap.segments.length - 1];
  return (
    <AbsoluteFill style={{ transform: `translate(${dx * 100}%, 0) scale(${sp})`, transformOrigin: `${ox * 100}% ${oy * 100}%` }}>
      {cap.segments.map((sg, k) => (
        <Sequence key={k} from={sg.tlFrom} durationInFrames={sg.tlTo - sg.tlFrom} name={`${sg.src} ${sg.srcFrom}-${sg.srcTo}`}>
          <Video src={staticFile(`media/${sg.src}.mp4`)} trimBefore={sg.srcFrom} muted objectFit="cover"
            style={{ width: "100%", height: "100%" }} effects={effects} effectsOutputSize={eos} />
        </Sequence>
      ))}
      <Sequence from={cap.bodyEnd} durationInFrames={Math.max(1, cap.durationInFrames - cap.bodyEnd)} name="image figée">
        <Freeze frame={0}>
          <Video src={staticFile(`media/${last.src}.mp4`)} trimBefore={last.srcTo - 1} muted objectFit="cover"
            style={{ width: "100%", height: "100%" }} effects={effects} effectsOutputSize={eos} />
        </Freeze>
      </Sequence>
    </AbsoluteFill>
  );
};
