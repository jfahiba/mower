import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { z } from "zod";
import { EndCard } from "./components/EndCard";
import { BottomShade, Fades, Flashes, Grain, Vignette } from "./components/Finish";
import { MessageTrack } from "./components/MessageTrack";
import { Subtitles } from "./components/Subtitles";
import { Timelapse } from "./components/Timelapse";
import { ChapterLabels, EventTitle, Signoff, Triad } from "./components/Typography";
import "./lib/fonts";

export const filmSchema = z.object({
  burnSubtitles: z.boolean().describe("Sous-titres incrustés"),
  audio: z.enum(["mix", "stems", "none"]).describe("mix = mixage masterisé ; stems = pistes séparées"),
  grain: z.number().min(0).max(0.3).step(0.005).describe("Grain argentique"),
  vignette: z.number().min(0).max(1).step(0.05).describe("Vignettage"),
  endCard: z.object({
    kicker: z.string(),
    title: z.string(),
    tagline: z.string(),
    cta: z.string(),
    details: z.string().describe("Date, lieu, lien… (vide = non affiché)"),
  }),
});

export type FilmProps = z.infer<typeof filmSchema>;

export const Film: React.FC<FilmProps> = ({ burnSubtitles, audio, grain, vignette, endCard }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {/* 1. images */}
      <Timelapse />
      <MessageTrack />
      {/* 2. finitions image */}
      <BottomShade />
      <Vignette amount={vignette} />
      <Grain opacity={grain} />
      {/* 3. typographie */}
      <ChapterLabels />
      <Triad />
      <EventTitle />
      <Signoff />
      {burnSubtitles ? <Subtitles /> : null}
      <EndCard text={endCard} />
      {/* 4. lumière et fondus */}
      <Flashes />
      <Fades />
      {/* 5. son */}
      {audio === "mix" ? <Audio src={staticFile("audio/mix.wav")} /> : null}
      {audio === "stems" ? (
        <>
          <Audio src={staticFile("audio/stems/voice.wav")} />
          <Audio src={staticFile("audio/stems/music.wav")} />
          <Audio src={staticFile("audio/stems/sfx.wav")} />
          <Audio src={staticFile("audio/stems/amb.wav")} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};
