// Types de la timeline générée par pipeline/build_timeline.py (src/data/timeline.json).
import data from "../data/timeline.json";

export type Shot = {
  id: string;
  src: string;
  file: string;
  from_: number;
  durationInFrames: number;
  transIn: "open" | "cut" | "whip" | "zoom" | "impact";
  avgSpeed: number;
  note: string;
};

export type Segment = { srcFrom: number; srcTo: number; tlFrom: number; tlTo: number };
export type Framing = { tlFrom: number; scale: number; push: number; srcT: number; note: string };
export type Word = { text: string; start: number; end: number };
export type Cue = {
  text: string;
  words: Word[];
  start: number;
  end: number;
  displayStart: number;
  displayEnd: number;
  emphasis: boolean[];
  lineBreak?: number;
};
export type TriadLine = { a: string; b: string; tl: number };
export type Moment = {
  kind: "triad" | "event" | "signoff";
  tlFrom: number;
  tlTo: number;
  lines?: TriadLine[];
  kicker?: string;
  title?: string;
};
export type Chapter = { kicker: string; title: string; tlFrom: number; tlTo: number };
export type EndCard = {
  duration: number;
  kicker: string;
  title: string;
  tagline: string;
  cta: string;
  details: string;
  tlFrom: number;
  tlTo: number;
};

export type Timeline = {
  fps: number;
  width: number;
  height: number;
  bpm: number;
  durationInFrames: number;
  timelapse: Shot[];
  timelapseEnd: number;
  impactFrame: number;
  message: { file: string; videoIn: number; audioStart: number; segments: Segment[]; end: number };
  framing: Framing[];
  faceTrack: { tl: number; cx: number; cy: number }[];
  paintingAnchorA1: [number, number];
  paintingAnchorMsg: [number, number];
  chapters: Chapter[];
  moments: Moment[];
  cues: Cue[];
  endCard: EndCard;
  sfx: { type: string; tl: number; toTl?: number }[];
};

export const TL = data as unknown as Timeline;
