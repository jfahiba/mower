import { Video } from "@remotion/media";
import { blur } from "@remotion/effects/blur";
import { zoomBlur } from "@remotion/effects/zoom-blur";
import React from "react";
import { AbsoluteFill, Sequence, staticFile, useCurrentFrame } from "remotion";
import { easeIn, easeOut, mix, prog, rand } from "../lib/anim";
import { Shot, TL } from "../lib/timeline";

// Transitions « cut-based » : l'effet de sortie s'applique aux dernières images
// du plan sortant, l'effet d'entrée aux premières images du plan entrant ;
// aucune image n'est superposée (lecture nette, motivée par le mouvement).
const WHIP_OUT = 5;
const WHIP_IN = 6;
const WHIP_SHIFT = 0.09; // fraction de la largeur
const WHIP_BLUR = 110; // px (canvas 2160 de large)
const ZOOM_OUT = 6;
const ZOOM_IN = 9;
const MATCH_OUT = 8;

type FX = {
  tx: number; // translation horizontale (fraction de la largeur)
  ty: number; // translation verticale (fraction de la hauteur)
  scale: number;
  origin: [number, number];
  hBlur: number;
  zBlur: number;
  zCenter: [number, number];
};

const neutral = (): FX => ({
  tx: 0,
  ty: 0,
  scale: 1,
  origin: [0.5, 0.5],
  hBlur: 0,
  zBlur: 0,
  zCenter: [0.5, 0.5],
});

const shotFx = (shot: Shot, next: Shot | undefined, f: number): FX => {
  const fx = neutral();
  const d = shot.durationInFrames;

  // ---------- entrée ----------
  switch (shot.transIn) {
    case "open": {
      // ouverture : léger recul de caméra numérique, très doux
      fx.scale *= mix(1.07, 1.0, prog(f, 0, 45, easeOut));
      break;
    }
    case "cut": {
      // coupe sur le temps : micro « punch » de 3 % qui retombe (accent rythmique)
      fx.scale *= mix(1.03, 1.0, prog(f, 0, 8, easeOut));
      break;
    }
    case "whip": {
      const p = prog(f, 0, WHIP_IN, easeOut);
      fx.tx += mix(WHIP_SHIFT, 0, p);
      fx.scale *= mix(1.2, 1.0, p);
      fx.hBlur = Math.max(fx.hBlur, mix(WHIP_BLUR, 0, p));
      break;
    }
    case "zoom": {
      const p = prog(f, 0, ZOOM_IN, easeOut);
      fx.scale *= mix(1.28, 1.0, p);
      fx.zBlur = Math.max(fx.zBlur, mix(150, 0, p));
      break;
    }
    case "impact": {
      // impact : recul rapide + flou radial + secousse amortie
      const p = prog(f, 0, 12, easeOut);
      fx.scale *= mix(1.14, 1.0, p);
      fx.zBlur = Math.max(fx.zBlur, mix(130, 0, prog(f, 0, 8, easeOut)));
      const amp = Math.max(0, 1 - f / 10);
      fx.tx += (rand(f * 3.1 + 1) - 0.5) * 0.012 * amp;
      fx.ty += (rand(f * 5.7 + 2) - 0.5) * 0.008 * amp;
      break;
    }
  }

  // ---------- sortie (selon l'entrée du plan suivant) ----------
  if (next) {
    if (next.transIn === "whip") {
      const p = prog(f, d - WHIP_OUT, WHIP_OUT, easeIn);
      fx.tx -= WHIP_SHIFT * p;
      fx.scale *= mix(1.0, 1.2, p);
      fx.hBlur = Math.max(fx.hBlur, WHIP_BLUR * p);
    } else if (next.transIn === "zoom") {
      const p = prog(f, d - ZOOM_OUT, ZOOM_OUT, easeIn);
      fx.scale *= mix(1.0, 1.35, p);
      fx.origin = [0.5, 0.42];
      fx.zBlur = Math.max(fx.zBlur, 150 * p);
      fx.zCenter = [0.5, 0.42];
    } else if (next.transIn === "impact") {
      fx.scale *= mix(1.0, 1.05, prog(f, d - 3, 3, easeIn));
    }
  } else {
    // dernier plan (A1) : zoom de raccord vers le tableau de coquelicots
    const p = prog(f, d - MATCH_OUT, MATCH_OUT, (t) => t * t);
    const a = TL.paintingAnchorA1;
    if (p > 0) {
      fx.origin = a;
      fx.scale *= mix(1.0, 1.55, p);
      fx.zBlur = Math.max(fx.zBlur, 170 * p);
      fx.zCenter = a;
    }
  }
  return fx;
};

const ShotInner: React.FC<{ shot: Shot; next?: Shot }> = ({ shot, next }) => {
  const f = useCurrentFrame();
  const fx = shotFx(shot, next, f);
  const effects = [
    ...(fx.hBlur > 0.5 ? [blur({ radius: fx.hBlur, vertical: false })] : []),
    ...(fx.zBlur > 0.5 ? [zoomBlur({ amount: fx.zBlur, center: fx.zCenter, samples: 32 })] : []),
  ];
  return (
    <AbsoluteFill
      style={{
        transform: `translate(${fx.tx * 100}%, ${fx.ty * 100}%) scale(${fx.scale})`,
        transformOrigin: `${fx.origin[0] * 100}% ${fx.origin[1] * 100}%`,
      }}
    >
      <Video
        src={staticFile(shot.file)}
        muted
        objectFit="cover"
        style={{ width: "100%", height: "100%" }}
        effects={effects}
      />
    </AbsoluteFill>
  );
};

export const Timelapse: React.FC = () => {
  const shots = TL.timelapse;
  return (
    <>
      {shots.map((s, i) => (
        <Sequence key={s.id} from={s.from_} durationInFrames={s.durationInFrames} name={`${s.id} · ${s.note}`}>
          <ShotInner shot={s} next={shots[i + 1]} />
        </Sequence>
      ))}
    </>
  );
};
