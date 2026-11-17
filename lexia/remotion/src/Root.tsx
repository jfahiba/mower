import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, Composition, staticFile } from "remotion";
import { Bug, ChapterFlash, EndCard, Finish, Photos, QuestionCards, TitleCard } from "./components/Overlays";
import { Subtitles } from "./components/Subtitles";
import { Talk } from "./components/Talk";
import { capsuleById, DATA } from "./lib/data";
import "./lib/fonts";

// Capsules verticales 9:16 « Me Rania Arbi répond à vos questions » (Lexia Notaires),
// 2160x3840 à 30 i/s. Données : src/data/capsules.json (../pipeline/build_capsules.py).
export const Capsule: React.FC<{ capsuleId: string; burnSubtitles: boolean }> = ({ capsuleId, burnSubtitles }) => {
  const cap = capsuleById(capsuleId);
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Talk cap={cap} />
      <Finish cap={cap} />
      <Bug cap={cap} />
      <TitleCard cap={cap} />
      <QuestionCards cap={cap} />
      {burnSubtitles ? <Subtitles cap={cap} /> : null}
      <Photos cap={cap} />
      <EndCard cap={cap} />
      <ChapterFlash cap={cap} />
      <Audio src={staticFile(`audio/${cap.id}.wav`)} />
    </AbsoluteFill>
  );
};

export const RemotionRoot: React.FC = () => (
  <>
    {DATA.capsules.map((c) => (
      <Composition key={c.id} id={c.id} component={Capsule} durationInFrames={c.durationInFrames} fps={30} width={2160} height={3840}
        defaultProps={{ capsuleId: c.id, burnSubtitles: true }} />
    ))}
  </>
);
