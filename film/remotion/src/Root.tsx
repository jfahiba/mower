import { Composition } from "remotion";
import { Film, filmSchema } from "./Film";
import { TL } from "./lib/timeline";

// Film vertical 9:16 — 2160x3840 (4K UHD vertical), 30 i/s.
// La timeline (plans, coupes, sous-titres, cadrages) est générée par
// ../pipeline/build_timeline.py dans src/data/timeline.json.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Film"
        component={Film}
        schema={filmSchema}
        durationInFrames={TL.durationInFrames}
        fps={TL.fps}
        width={TL.width}
        height={TL.height}
        defaultProps={{
          burnSubtitles: true,
          audio: "mix" as const,
          grain: 0.07,
          vignette: 1,
          endCard: {
            kicker: "Souper annuel · 2026",
            title: "Le souper de Noël",
            tagline: "Femme entrepreneure · Femme battante · Femme de foi",
            cta: "Les places partent rapidement — inscris-toi.",
            details: "",
          },
        }}
      />
      <Composition
        id="FilmSansSousTitres"
        component={Film}
        schema={filmSchema}
        durationInFrames={TL.durationInFrames}
        fps={TL.fps}
        width={TL.width}
        height={TL.height}
        defaultProps={{
          burnSubtitles: false,
          audio: "mix" as const,
          grain: 0.07,
          vignette: 1,
          endCard: {
            kicker: "Souper annuel · 2026",
            title: "Le souper de Noël",
            tagline: "Femme entrepreneure · Femme battante · Femme de foi",
            cta: "Les places partent rapidement — inscris-toi.",
            details: "",
          },
        }}
      />
    </>
  );
};
