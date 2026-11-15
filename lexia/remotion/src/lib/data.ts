import data from "../data/capsules.json";

export type Word = { text: string; start: number; end: number };
export type Cue = {
  text: string;
  words: Word[];
  start: number;
  end: number;
  displayStart: number;
  displayEnd: number;
  emphasis: boolean[];
  lineBreak: number;
};
export type Segment = { src: string; srcFrom: number; srcTo: number; tlFrom: number; tlTo: number; cx: number; cy: number };
export type Capsule = {
  id: string;
  title: string;
  short: string;
  segments: Segment[];
  bodyEnd: number;
  durationInFrames: number;
  questions: { tlFrom: number; tlTo: number; text: string }[];
  cues: Cue[];
  photos: { file: string; tlFrom: number; dur: number }[];
  framing: { tlFrom: number; scale: number; push: number }[];
};
export type Contact = { firm: string; firm2: string; person: string; email: string; phone: string; offices: string[] };

export const DATA = data as unknown as { fps: number; width: number; height: number; contact: Contact; outroPhoto: string; capsules: Capsule[] };
export const capsuleById = (id: string) => DATA.capsules.find((c) => c.id === id)!;
