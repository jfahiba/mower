"""Composition musicale originale, écrite pour l'image (scoring to picture).

Aucune musique tierce : partition générée ici (MIDI) et rendue avec FluidSynth +
banque MuseScore General (licence MIT) ; percussions, montées, impacts et
whooshes synthétisés (numpy/scipy). Tout est calé sur la timeline :
120 BPM => 1 mesure = 2 s = 60 images ; les coupes du timelapse tombent sur les temps.

Forme (ré majeur) :
  A  0–12 s   timelapse : ostinato de piano, cordes en crescendo, pulsation qui
              s'intensifie (vi–IV–I–V), roulement + silence d'une croche avant…
  B  12 s     IMPACT sur la tonique (ré) : boom, timbale, tutti bref, puis halo
              tenu pendant le ralenti ; l'ambiance réelle et la voix arrivent.
  C  16–58 s  tapis sous la voix (I–V/3–vi–iii/5–IV–I/3–IV–V) : piano feutré,
              cordes, chœur ; célesta « Noël » à la révélation du souper ; montée
              douce sur « Les places partent… », cadence IV–V–I : la tonique
              arrive juste après « À très vite ! ».
  D  58–62,6 s carton final : accord épanoui, cloches, extinction.

Sorties (48 kHz, float) : work/audio/music_tl.wav, work/audio/sfx_tl.wav,
work/audio/stems/*.wav
"""
import json
import subprocess
from pathlib import Path

import mido
import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "work/audio"
STEMS = A / "stems"
MID = A / "midi"
for d in (A, STEMS, MID):
    d.mkdir(parents=True, exist_ok=True)

SR = 48000
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
SF2 = "/usr/share/sounds/sf2/MuseScore_General_Full.sf2"
rng = np.random.default_rng(2026)

TL = json.loads((ROOT / "remotion/src/data/timeline.json").read_text())
FPS = TL["fps"]
T_TOTAL = TL["durationInFrames"] / FPS
T_IMPACT = TL["impactFrame"] / FPS
T_VOICE = TL["message"]["audioStart"] / FPS
T_MATCH = TL["message"]["videoIn"] / FPS
T_EVENT = TL["moments"][1]["tlFrom"] / FPS
T_SIGNOFF = TL["moments"][2]["tlFrom"] / FPS
T_ENDCARD = TL["endCard"]["tlFrom"] / FPS
N = int((T_TOTAL + 0.5) * SR)

# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def n(name):
    """'F#4' -> numéro MIDI."""
    p, o = (name[:-1], int(name[-1]))
    return 12 * (o + 1) + NOTE[p]


def notes(*names):
    return [n(x) for x in names]


# Accords (voicings serrés, conduite des voix soignée)
CH = {
    # section A (ostinato : 4 notes)
    "Bm": dict(bass="B1", pad=notes("B2", "F#3", "B3", "D4", "F#4"), arp=notes("B3", "F#4", "B4", "D5")),
    "G": dict(bass="G1", pad=notes("G2", "D3", "G3", "B3", "D4"), arp=notes("G3", "D4", "G4", "B4")),
    "D": dict(bass="D2", pad=notes("D3", "A3", "D4", "F#4", "A4"), arp=notes("A3", "D4", "F#4", "A4")),
    "A": dict(bass="A1", pad=notes("A2", "E3", "A3", "C#4", "E4"), arp=notes("A3", "E4", "A4", "C#5")),
    "Asus": dict(bass="A1", pad=notes("A2", "E3", "A3", "D4", "E4"), arp=notes("A3", "E4", "A4", "D5")),
    # section C (tapis)
    "D9": dict(bass="D2", pad=notes("D3", "A3", "E4", "F#4", "A4"), arp=notes("D4", "F#4", "A4", "E5")),
    "A/C#": dict(bass="C#2", pad=notes("C#3", "A3", "C#4", "E4", "A4"), arp=notes("C#4", "E4", "A4", "C#5")),
    "Bm7": dict(bass="B1", pad=notes("B2", "F#3", "A3", "D4", "F#4"), arp=notes("B3", "D4", "F#4", "A4")),
    "F#m/A": dict(bass="A1", pad=notes("A2", "F#3", "A3", "C#4", "F#4"), arp=notes("A3", "C#4", "F#4", "A4")),
    "Gmaj7": dict(bass="G1", pad=notes("G2", "D3", "F#3", "B3", "D4"), arp=notes("G3", "B3", "D4", "F#4")),
    "D/F#": dict(bass="F#1", pad=notes("F#2", "D3", "A3", "D4", "F#4"), arp=notes("F#3", "A3", "D4", "F#4")),
    "G6": dict(bass="G1", pad=notes("G2", "D3", "E3", "B3", "D4"), arp=notes("G3", "B3", "E4", "G4")),
    "A7sus": dict(bass="A1", pad=notes("A2", "E3", "G3", "D4", "E4"), arp=notes("A3", "D4", "E4", "G4")),
    "A7": dict(bass="A1", pad=notes("A2", "E3", "G3", "C#4", "E4"), arp=notes("A3", "C#4", "E4", "G4")),
}

SEC_A = ["Bm", "G", "D", "A", "Bm", "G"]  # mesures 1–6 (0–12 s)
CYCLE = ["D9", "A/C#", "Bm7", "F#m/A", "Gmaj7", "D/F#", "G6", "A7sus"]
# mélodie originale du tapis : (temps dans la mesure, durée en temps, note)
MELODY_C1 = [
    [(0, 2, "A4"), (2, 2, "F#4")], [(0, 4, "E4")], [(0, 2, "D4"), (2, 2, "F#4")], [(0, 4, "C#4")],
    [(0, 2, "B3"), (2, 2, "D4")], [(0, 4, "A3")], [(0, 2, "B3"), (2, 2, "E4")], [(0, 3, "E4"), (3, 1, "D4")],
]
MELODY_C2 = [
    [(0, 1.5, "F#5"), (1.5, 0.5, "E5"), (2, 2, "D5")], [(0, 2, "E5"), (2, 2, "C#5")],
    [(0, 1.5, "D5"), (1.5, 0.5, "C#5"), (2, 2, "B4")], [(0, 4, "C#5")],
    [(0, 1.5, "B4"), (1.5, 0.5, "A4"), (2, 2, "B4")], [(0, 2, "A4"), (2, 2, "F#4")],
    [(0, 2, "G4"), (2, 2, "B4")], [(0, 4, "A4")],
]


class Track:
    def __init__(self, name, program, channel=0):
        self.name, self.program, self.channel = name, program, channel
        self.events = []  # (t, kind, a, b, c)

    def note(self, t, dur, pitch, vel):
        vel = int(max(1, min(127, vel)))
        self.events.append((t, "on", pitch, vel))
        self.events.append((t + dur, "off", pitch, 0))

    def cc(self, t, num, val):
        self.events.append((t, "cc", num, int(max(0, min(127, val)))))

    def ramp(self, t0, t1, num, v0, v1, steps=None):
        steps = steps or max(2, int((t1 - t0) * 20))
        for i in range(steps + 1):
            x = i / steps
            self.cc(t0 + (t1 - t0) * x, num, v0 + (v1 - v0) * x)

    def write(self, path, end_t):
        mid = mido.MidiFile(ticks_per_beat=480)
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        tr.append(mido.MetaMessage("set_tempo", tempo=int(60e6 / BPM), time=0))
        tr.append(mido.Message("program_change", program=self.program, channel=self.channel, time=0))
        tr.append(mido.Message("control_change", control=91, value=0, channel=self.channel, time=0))  # pas de reverb interne
        tr.append(mido.Message("control_change", control=93, value=0, channel=self.channel, time=0))  # pas de chorus
        order = {"off": 0, "cc": 1, "on": 2}
        ev = sorted(self.events, key=lambda e: (e[0], order[e[1]]))
        ev.append((end_t, "cc", 11, 0))
        last = 0
        for t, kind, a, b in ev:
            tick = int(round(t * 960))
            dt = max(0, tick - last)
            last = max(last, tick)
            if kind == "on":
                tr.append(mido.Message("note_on", note=a, velocity=b, channel=self.channel, time=dt))
            elif kind == "off":
                tr.append(mido.Message("note_off", note=a, velocity=0, channel=self.channel, time=dt))
            else:
                tr.append(mido.Message("control_change", control=a, value=b, channel=self.channel, time=dt))
        mid.save(path)


def render(track, gain=0.5):
    midp = MID / f"{track.name}.mid"
    wav = STEMS / f"{track.name}_dry.wav"
    track.write(midp, T_TOTAL + 0.4)
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", str(gain), "-r", str(SR), "-R", "0", "-C", "0",
                    "-F", str(wav), SF2, str(midp)], check=True, capture_output=True)
    x, sr = sf.read(wav, dtype="float32", always_2d=True)
    assert sr == SR
    out = np.zeros((N, 2), np.float32)
    m = min(N, len(x))
    out[:m] = x[:m]
    return out


# ---------------------------------------------------------------------------
# Écriture des parties
# ---------------------------------------------------------------------------
def bar_t(i):  # début de la mesure i (0 = 0 s)
    return i * BAR


def write_parts():
    piano = Track("piano", 0)
    strings = Track("strings", 49)  # Slow Strings
    stacc = Track("pizz", 45)  # Pizzicato
    basses = Track("basses", 43)  # Contrabass (arco)
    choir = Track("choir", 52)
    celesta = Track("celesta", 8)
    harp = Track("harp", 46)
    brass = Track("brass", 61)
    timp = Track("timpani", 47)

    # ---------------- Section A : mesures 1–6 (0–12 s) ----------------------
    strings.cc(0, 11, 38)
    strings.ramp(0, T_IMPACT - 0.3, 11, 38, 112)
    for i, c in enumerate(SEC_A):
        t0 = bar_t(i)
        ch = CH[c]
        # ostinato de piano en croches (8 par mesure) ; mesure 6 : G puis Asus/A
        pattern = [0, 1, 2, 3, 1, 2, 3, 2]
        for k in range(8):
            cc = c
            if i == 5 and k >= 4:
                cc = "Asus" if k < 6 else "A"
            arp = CH[cc]["arp"]
            t = t0 + k * BEAT / 2
            if t >= T_IMPACT - BEAT / 2:  # silence d'une croche avant l'impact
                continue
            vel = 54 + (12 if k % 2 == 0 else 0) + (8 if k == 0 else 0) + i * 4
            piano.note(t, BEAT / 2 * 0.95, arp[pattern[k]] + (12 if i >= 4 and k in (3, 6) else 0), vel)
        # main gauche : basse en blanches puis en noires
        if i < 4:
            piano.note(t0, BAR * 0.98, n(ch["bass"]) + 12, 50 + i * 3)
        else:
            for q in range(4):
                if t0 + q * BEAT < T_IMPACT - BEAT / 2:
                    b = CH["A"]["bass"] if (i == 5 and q >= 2) else ch["bass"]
                    piano.note(t0 + q * BEAT, BEAT * 0.9, n(b) + 12, 60)
        # cordes tenues
        pad = ch["pad"] if i < 5 else CH["G"]["pad"]
        for p in pad:
            strings.note(t0, (BAR if i < 5 else 2 * BEAT) * 1.0, p, 70)
        if i == 5:
            for p in CH["Asus"]["pad"]:
                strings.note(t0 + 2 * BEAT, BEAT, p, 80)
            for p in CH["A"]["pad"]:
                strings.note(t0 + 3 * BEAT, BEAT / 2 * 0.9, p, 88)
        # contrebasses : à partir de la mesure 3, pulsation en croches (mesures 5–6)
        if 2 <= i < 4:
            basses.note(t0, BAR * 0.98, n(ch["bass"]) + 12, 64)
        elif i >= 4:
            for k in range(8):
                t = t0 + k * BEAT / 2
                if t < T_IMPACT - BEAT / 2:
                    b = CH["A"]["bass"] if (i == 5 and k >= 4) else ch["bass"]
                    basses.note(t, BEAT / 2 * 0.7, n(b) + 12, 72 + (10 if k % 2 == 0 else 0))
        # pizzicati en noires (mesures 3–6)
        if i >= 2:
            for q in range(4):
                t = t0 + q * BEAT
                if t < T_IMPACT - BEAT / 2:
                    arp = CH[("Asus" if q == 2 else "A") if (i == 5 and q >= 2) else c]["arp"]
                    stacc.note(t, BEAT * 0.5, arp[(q * 2) % 4] + 12, 62 + 4 * i)

    # ---------------- Section B : impact (12 s) puis halo -------------------
    ti = T_IMPACT
    for p in notes("D2", "A2", "D3", "F#3", "A3", "D4"):
        brass.note(ti, 0.55, p, 112)
    brass.cc(0, 11, 110)
    timp.note(ti, 1.6, n("D2"), 124)
    timp.note(ti, 1.6, n("A1"), 100)
    piano.note(ti, 3.5, n("D1"), 100)
    piano.note(ti, 3.5, n("D2"), 96)
    piano.note(ti, 3.0, n("A3"), 70)
    piano.note(ti, 3.0, n("F#4"), 66)
    strings.cc(ti, 11, 112)
    for p in notes("D3", "A3", "E4", "F#4", "A4", "D5"):
        strings.note(ti, 4.0, p, 92)
    strings.ramp(ti + 0.2, ti + 3.6, 11, 112, 46)
    basses.note(ti, 3.8, n("D2"), 96)
    choir.cc(0, 11, 70)
    for p in notes("D4", "F#4", "A4"):
        choir.note(ti + 0.15, 3.6, p, 64)
    choir.ramp(ti + 0.2, ti + 3.6, 11, 90, 40)
    # étincelle au raccord (tableau de coquelicots)
    for k, p in enumerate(notes("A5", "D6", "F#6", "A6")):
        celesta.note(T_MATCH - 0.12 + k * 0.09, 1.2, p, 46 - k * 4)

    # ---------------- Section C : tapis (mesures 9–30) -----------------------
    strings.cc(16.0 - 0.01, 11, 52)
    choir.cc(16.0 - 0.01, 11, 0)
    bar0 = 8  # mesure 9 commence à 16 s
    end_bar = int(round(58.0 / BAR))  # résolution à 58 s
    for bi in range(bar0, end_bar):
        t0 = bar_t(bi)
        k = (bi - bar0) % 8
        cyc = (bi - bar0) // 8
        name = CYCLE[k]
        if bi == end_bar - 1:  # mesure 29 : cadence IV–V
            name = None
        if name:
            ch = CH[name]
            # piano : basse + accord brisé très doux
            piano.note(t0, BAR * 0.95, n(ch["bass"]) + 12, 40 + cyc * 4)
            arp = ch["arp"]
            if cyc == 0:
                piano.note(t0 + BEAT * 0.5, BEAT * 3.2, arp[1], 34)
                piano.note(t0 + BEAT * 1.0, BEAT * 2.8, arp[2], 32)
            else:
                for q, idx in enumerate([0, 1, 2, 3, 2, 1, 2, 3]):
                    piano.note(t0 + q * BEAT / 2, BEAT * 0.9, arp[idx], 32 + (4 if q % 2 == 0 else 0) + (cyc - 1) * 6)
            # mélodie (cycle 1 : discrète, cycle 2+ : plus chantante, octave au-dessus)
            mel = MELODY_C1[k] if cyc == 0 else MELODY_C2[k]
            for (bt, d, nn) in mel:
                piano.note(t0 + bt * BEAT, d * BEAT * 0.97, n(nn) + (12 if cyc == 0 else 0), 38 if cyc == 0 else 44)
            # cordes : accords tenus
            for p in ch["pad"]:
                strings.note(t0, BAR, p, 60 + 8 * cyc)
            if cyc >= 1:
                basses.note(t0, BAR * 0.98, n(ch["bass"]) + 12, 54 + 6 * cyc)
                for p in ch["pad"][2:]:
                    choir.note(t0, BAR, p + 12 if p < n("C4") else p, 50)
            # pulsation finale (cycle 3) : pizzicati en croches
            if bi >= 25:
                for q in range(8):
                    stacc.note(t0 + q * BEAT / 2, BEAT * 0.4, ch["arp"][q % 4] + 12, 46 + q % 2 * 6 + (bi - 24) * 3)
        else:
            # mesure 29 : G6 (temps 1–2) -> A7sus (3) -> A7 (4), crescendo
            for half, nm in ((0, "G6"), (2, "A7sus"), (3, "A7")):
                ch = CH[nm]
                d = 2 * BEAT if half == 0 else BEAT
                for p in ch["pad"]:
                    strings.note(t0 + half * BEAT, d, p, 84)
                    choir.note(t0 + half * BEAT, d, p + 12 if p < n("C4") else p, 58)
                piano.note(t0 + half * BEAT, d * 0.95, n(ch["bass"]) + 12, 56)
                for q in range(int(d / (BEAT / 2))):
                    stacc.note(t0 + half * BEAT + q * BEAT / 2, BEAT * 0.4, ch["arp"][q % 4] + 12, 66)
                basses.note(t0 + half * BEAT, d * 0.98, n(ch["bass"]) + 12, 74)
            piano.note(t0 + 2 * BEAT, BEAT * 1.9, n("E5"), 52)
            timp.note(t0 + 3 * BEAT, 0.25, n("A1"), 70)
            timp.note(t0 + 3.5 * BEAT, 0.25, n("A1"), 84)
    # crescendo d'expression des cordes sur la fin (les places partent…)
    strings.ramp(48.0, 58.0, 11, 56, 96)
    choir.cc(32.0, 11, 64)
    choir.ramp(48.0, 58.0, 11, 64, 92)
    # célesta + harpe à la révélation « le souper de Noël »
    te = T_EVENT
    for k, p in enumerate(notes("D5", "F#5", "A5", "D6", "E6", "F#6", "A6", "D7")):
        harp.note(te - 0.35 + k * 0.045, 2.5, p - 12, 60 - k * 2)
    for k, p in enumerate(notes("A5", "D6", "F#6", "A6", "D7")):
        celesta.note(te + k * 0.12, 1.6, p, 58 - k * 3)
    for k, p in enumerate(notes("F#6", "A6", "D7")):
        celesta.note(te + 1.2 + k * 0.16, 1.4, p, 44)

    # ---------------- Section D : résolution (58 s) + carton ----------------
    tr = end_bar * BAR  # 58 s
    for p in notes("D2", "A2", "D3", "F#3", "A3", "D4", "E4", "F#4", "A4", "D5"):
        strings.note(tr, T_TOTAL - tr + 0.2, p, 86)
    strings.ramp(tr + 0.3, T_TOTAL, 11, 96, 18)
    for p in notes("D4", "F#4", "A4", "D5"):
        choir.note(tr, T_TOTAL - tr, p, 60)
    choir.ramp(tr + 0.3, T_TOTAL, 11, 92, 10)
    basses.note(tr, T_TOTAL - tr, n("D2"), 70)
    piano.note(tr, 4.0, n("D2"), 62)
    piano.note(tr, 4.0, n("D3"), 56)
    for k, p in enumerate(notes("A4", "D5", "F#5", "A5")):
        piano.note(tr + 0.25 + k * 0.25, 3.5, p, 46 - k * 3)
    timp.note(tr, 1.5, n("D2"), 76)
    # cloches au carton final
    for k, p in enumerate(notes("D6", "A6", "F#6", "D7")):
        celesta.note(T_ENDCARD + 0.35 + k * 0.22, 2.2, p, 52 - k * 4)
    harp.note(T_ENDCARD + 0.3, 3, n("D4"), 50)
    harp.note(T_ENDCARD + 0.42, 3, n("A4"), 48)

    return dict(piano=piano, strings=strings, pizz=stacc, basses=basses, choir=choir,
                celesta=celesta, harp=harp, brass=brass, timpani=timp)


# ---------------------------------------------------------------------------
# DSP : filtres, réverbération à convolution, percussions et effets synthétisés
# ---------------------------------------------------------------------------
def bp(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x, axis=0)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x, axis=0)


def make_ir(rt60=2.4, predelay=0.022, length=3.6, seed=1):
    """Réponse impulsionnelle stéréo synthétique (salle chaleureuse) : bruit décorrélé,
    décroissance dépendant de la fréquence (aigus amortis plus vite) + premières réflexions."""
    r = np.random.default_rng(seed)
    L = int(length * SR)
    t = np.arange(L) / SR
    ir = np.zeros((L, 2), np.float32)
    bands = [(20, 250, rt60 * 1.10), (250, 1500, rt60), (1500, 5000, rt60 * 0.72), (5000, 16000, rt60 * 0.42)]
    for lo, hi, rt in bands:
        noise = r.standard_normal((L, 2))
        noise = bp(noise, lo, min(hi, SR / 2 - 100), 2)
        env = np.exp(-6.91 * t / rt)[:, None]
        ir += (noise * env).astype(np.float32)
    # montée douce (diffusion)
    ir *= (1 - np.exp(-t / 0.012))[:, None]
    pd = int(predelay * SR)
    ir = np.concatenate([np.zeros((pd, 2), np.float32), ir])
    for d, g, pan in [(0.011, 0.5, 0.2), (0.017, 0.4, 0.8), (0.023, 0.33, 0.35), (0.031, 0.28, 0.7)]:
        k = int(d * SR)
        ir[k, 0] += g * (1 - pan)
        ir[k, 1] += g * pan
    ir /= np.sqrt((ir ** 2).sum(axis=0, keepdims=True)) + 1e-9
    return ir


IR_HALL = make_ir(2.6, 0.025, 4.0, seed=3)
IR_ROOM = make_ir(1.1, 0.012, 1.8, seed=5)


def reverb(x, ir, wet):
    y = np.stack([fftconvolve(x[:, 0], ir[:, 0])[: len(x)], fftconvolve(x[:, 1], ir[:, 1])[: len(x)]], axis=1)
    return x + wet * y.astype(np.float32)


def place(buf, t, sig, gain=1.0, pan=0.0):
    """Ajoute un signal mono/stéréo à l'instant t (s), pan -1..1 (loi à puissance constante)."""
    i = int(round(t * SR))
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)], axis=1)
    j = min(len(buf), i + len(sig))
    if j > i >= 0:
        buf[i:j] += gain * sig[: j - i]


def env_exp(L, tau):
    return np.exp(-np.arange(L) / SR / tau)


def kick(vel=1.0):
    L = int(0.5 * SR)
    t = np.arange(L) / SR
    f = 48 + 120 * np.exp(-t / 0.032)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.30)
    click = hp(rng.standard_normal(L), 2500) * np.exp(-t / 0.004) * 0.25
    return np.tanh(1.6 * (body + click)) * 0.8 * vel


def clap(vel=1.0):
    L = int(0.35 * SR)
    t = np.arange(L) / SR
    nz = bp(rng.standard_normal(L), 900, 4200)
    env = np.zeros(L)
    for d in (0, 0.009, 0.019, 0.028):
        k = int(d * SR)
        env[k:] += np.exp(-(t[: L - k]) / 0.007)
    env += 0.6 * np.exp(-t / 0.11) * (t > 0.028)
    return nz * env / np.abs(nz * env).max() * 0.6 * vel


def shaker(vel=1.0):
    L = int(0.09 * SR)
    t = np.arange(L) / SR
    nz = hp(rng.standard_normal(L), 5500, 3)
    env = (1 - np.exp(-t / 0.006)) * np.exp(-t / 0.035)
    return nz * env * 0.22 * vel


def hat(vel=1.0):
    L = int(0.06 * SR)
    t = np.arange(L) / SR
    return hp(rng.standard_normal(L), 7500, 3) * np.exp(-t / 0.018) * 0.18 * vel


def tom(f0, vel=1.0):
    L = int(0.5 * SR)
    t = np.arange(L) / SR
    f = f0 * (1 + 0.5 * np.exp(-t / 0.05))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / 0.28) + 0.15 * bp(rng.standard_normal(L), 200, 2000) * np.exp(-t / 0.03)
    return np.tanh(1.3 * s) * 0.6 * vel


def snare(vel=1.0):
    L = int(0.25 * SR)
    t = np.arange(L) / SR
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05) * 0.5
    nz = bp(rng.standard_normal(L), 1200, 7000) * np.exp(-t / 0.075)
    return (body + nz) * 0.42 * vel


def sub_boom(dur=2.6):
    L = int(dur * SR)
    t = np.arange(L) / SR
    f = 30 + 34 * np.exp(-t / 0.35)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / 0.9)
    thump = lp(rng.standard_normal(L), 180, 2) * np.exp(-t / 0.06) * 0.8
    return np.tanh(1.4 * (s + thump)) * 0.9


def crack():
    L = int(0.5 * SR)
    t = np.arange(L) / SR
    return hp(rng.standard_normal(L), 2200, 2) * np.exp(-t / 0.05) * 0.5


def swept_noise(dur, f_start, f_peak, f_end, peak_pos=0.6, q=1.2):
    """Bruit filtré passe-bande à fréquence glissante (traitement par blocs)."""
    L = int(dur * SR)
    out = np.zeros(L)
    nz = rng.standard_normal(L)
    block = 256
    zi = None
    for s in range(0, L, block):
        x = s / L
        if x < peak_pos:
            f = f_start * (f_peak / f_start) ** (x / peak_pos)
        else:
            f = f_peak * (f_end / f_peak) ** ((x - peak_pos) / (1 - peak_pos))
        lo, hi = f / (1 + 0.5 / q), min(f * (1 + 0.5 / q), SR / 2 - 200)
        sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[s : s + block], zi = sosfilt(sos, nz[s : s + block], zi=zi)
    return out


def whoosh(dur=0.5, direction=1, bright=1.0):
    L = int(dur * SR)
    x = np.arange(L) / L
    s = swept_noise(dur, 350 * bright, 2600 * bright, 600 * bright, 0.58, 1.0)
    env = np.sin(np.pi * np.clip(x / 0.62, 0, 1) / 2) ** 2 * np.clip((1 - x) / 0.38, 0, 1) ** 1.5
    s = s * env
    s /= np.abs(s).max() + 1e-9
    pan = np.clip(-0.8 * direction + 1.6 * direction * x, -1, 1)
    a = (pan + 1) * np.pi / 4
    return np.stack([s * np.cos(a), s * np.sin(a)], axis=1) * 0.55


def riser(dur=2.0):
    L = int(dur * SR)
    t = np.arange(L) / SR
    x = t / dur
    nz = swept_noise(dur, 300, 9000, 9000, 1.0, 0.9)
    f = n_to_hz(n("D3")) * 2 ** (2 * x ** 1.6)  # glissando de deux octaves
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = sum(np.sin(k * ph) / k for k in range(1, 7)) * 0.25
    tone = lp(tone, 4000)
    trem = 0.7 + 0.3 * np.sin(2 * np.pi * np.cumsum(4 + 12 * x ** 2) / SR)
    s = (0.65 * nz / (np.abs(nz).max() + 1e-9) + 0.35 * tone) * trem * (x ** 2.2)
    return np.stack([s, np.roll(s, 37)], axis=1) * 0.5


def reverse_cymbal(dur=1.6):
    L = int(dur * SR)
    x = np.arange(L) / L
    nz = hp(rng.standard_normal((L, 2)), 3500, 2)
    nz = bp(nz, 3500, 14000, 1)
    return nz * (x ** 3)[:, None] * 0.35


def n_to_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def bell(freq, dur=3.0, vel=1.0):
    L = int(dur * SR)
    t = np.arange(L) / SR
    s = np.zeros(L)
    for ratio, amp, tau in [(1, 1.0, 1.4), (2.0, 0.45, 0.9), (2.76, 0.3, 0.55), (5.4, 0.18, 0.25), (8.93, 0.08, 0.12)]:
        s += amp * np.sin(2 * np.pi * freq * ratio * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    s *= 1 - np.exp(-t / 0.002)
    return s * 0.18 * vel


def shimmer(t0, buf):
    for k, m in enumerate([n("D6"), n("A6"), n("F#6"), n("D7"), n("A7")]):
        place(buf, t0 + k * 0.07, bell(n_to_hz(m), 3.2, 0.9 - k * 0.12), pan=(-0.5 + k * 0.25))


# ---------------------------------------------------------------------------
def percussion_and_sfx():
    buses = {k: np.zeros((N, 2), np.float32) for k in ("kick", "clap", "hats", "roll", "pulse")}
    sfx = np.zeros((N, 2), np.float32)
    ti = T_IMPACT
    cut = ti - BEAT / 2  # silence d'une croche avant l'impact
    for bi in range(6):
        t0 = bar_t(bi)
        for q in range(4):
            tq = t0 + q * BEAT
            if tq >= cut:
                continue
            # grosse caisse : 1 (m1), 1&3 (m2–4), tous les temps (m5–6)
            if (bi == 0 and q == 0) or (1 <= bi <= 3 and q in (0, 2)) or bi >= 4:
                place(buses["kick"], tq, kick(0.75 + 0.05 * bi))
            # clap sur 2 & 4 à partir de la mesure 3
            if bi >= 2 and q in (1, 3):
                place(buses["clap"], tq, clap(0.55 + 0.08 * (bi - 2)), pan=0.1)
        # shaker en croches, charleston en doubles croches (m5–6)
        for e in range(8):
            te = t0 + e * BEAT / 2
            if te < cut:
                place(buses["hats"], te, shaker(0.6 + (0.35 if e % 2 else 0)), pan=0.35)
        if bi >= 4:
            for s16 in range(16):
                ts = t0 + s16 * BEAT / 4
                if ts < cut:
                    place(buses["hats"], ts, hat(0.5 + (0.4 if s16 % 2 == 0 else 0)), pan=-0.3)
    # roulement de caisse claire + toms sur le dernier temps et demi avant l'impact
    t_roll0 = ti - 1.5 * BEAT * 2  # 1,5 s avant
    k = 0
    t = t_roll0
    while t < cut - 1e-6:
        prog = (t - t_roll0) / (cut - t_roll0)
        place(buses["roll"], t, snare(0.25 + 0.75 * prog ** 1.5), pan=0.05)
        step = BEAT / 4 if prog < 0.5 else BEAT / 8
        t += step
        k += 1
    for j, f0 in enumerate([150, 120, 95, 75]):
        place(buses["roll"], cut - BEAT + j * BEAT / 4, tom(f0, 0.8 + 0.05 * j), pan=-0.4 + 0.27 * j)
    # légère pulsation sur la montée finale (cycle 3) : grosse caisse douce sur 1 & 3
    for bi in range(25, 29):
        for q in (0, 2):
            place(buses["pulse"], bar_t(bi) + q * BEAT, kick(0.6 + 0.08 * (bi - 25)))
        for e in range(8):
            place(buses["pulse"], bar_t(bi) + e * BEAT / 2, shaker(0.25 + 0.04 * (bi - 25)) * 0.5, pan=0.3)

    # ------ effets (stem séparé) ------
    place(sfx, ti - 2.0, riser(2.0), gain=0.9)
    place(sfx, ti - 1.6, reverse_cymbal(1.6), gain=1.0)
    place(sfx, ti, sub_boom(2.8), gain=1.0)
    place(sfx, ti, crack(), gain=0.7)
    for s in TL["sfx"]:
        t = s["tl"] / FPS
        if s["type"] == "whoosh":
            place(sfx, t - 0.32, whoosh(0.52, direction=1 if int(t) % 4 == 0 else -1), gain=0.8)
        elif s["type"] == "swish":
            place(sfx, t - 0.2, whoosh(0.34, direction=1, bright=1.5), gain=0.55)
        elif s["type"] == "matchWhoosh":
            place(sfx, t - 0.42, whoosh(0.7, direction=-1, bright=0.7), gain=0.5)
        elif s["type"] == "shimmer":
            shimmer(t - 0.05, sfx)
    # carton final : cloche douce
    place(sfx, T_ENDCARD + 0.35, bell(n_to_hz(n("D6")), 4.0, 0.8), pan=0.0)
    return buses, sfx


# ---------------------------------------------------------------------------
# Gain staging automatique : cible RMS (dBFS) par piste et par section.
# Le RMS est mesuré sur les parties actives (> -60 dBFS) de chaque section ;
# les gains sont lissés (fondus de 0,25 s) entre sections.
# ---------------------------------------------------------------------------
SECTIONS = [  # (nom, début, fin)
    ("A1", 0.0, 8.0),             # timelapse courses
    ("A2", 8.0, T_IMPACT),        # timelapse bureau (plus dense)
    ("B", T_IMPACT, 16.0),        # impact + halo
    ("C1", 16.0, 32.0),           # tapis cycle 1 (sous la voix)
    ("C2", 32.0, 50.0),           # tapis cycle 2
    ("C3", 50.0, 56.0),           # montée douce
    ("CAD", 56.0, 58.0),          # cadence IV–V
    ("D", 58.0, T_TOTAL + 0.5),   # résolution + carton
]
TARGETS = {  # dBFS RMS ; None = piste muette dans la section
    "piano":   dict(A1=-20, A2=-20, B=-17, C1=-31, C2=-30, C3=-29, CAD=-27, D=-27),
    "strings": dict(A1=-25, A2=-22, B=-18, C1=-32, C2=-30, C3=-28, CAD=-25, D=-25),
    "pizz":    dict(A1=-30, A2=-27, B=None, C1=None, C2=None, C3=-33, CAD=-30, D=None),
    "basses":  dict(A1=-30, A2=-25, B=-22, C1=None, C2=-35, C3=-33, CAD=-29, D=-30),
    "choir":   dict(A1=None, A2=None, B=-27, C1=None, C2=-36, C3=-34, CAD=-31, D=-30),
    "celesta": dict(A1=None, A2=None, B=-30, C1=-31, C2=-31, C3=None, CAD=None, D=-29),
    "harp":    dict(A1=None, A2=None, B=None, C1=-31, C2=None, C3=None, CAD=None, D=-31),
    "brass":   dict(A1=None, A2=None, B=-16, C1=None, C2=None, C3=None, CAD=None, D=None),
    "timpani": dict(A1=None, A2=None, B=-16, C1=None, C2=None, C3=None, CAD=-30, D=-28),
    "kick":    dict(A1=-29, A2=-24, B=None, C1=None, C2=None, C3=None, CAD=None, D=None),
    "clap":    dict(A1=-33, A2=-29, B=None, C1=None, C2=None, C3=None, CAD=None, D=None),
    "hats":    dict(A1=-36, A2=-31, B=None, C1=None, C2=None, C3=None, CAD=None, D=None),
    "roll":    dict(A1=None, A2=-27, B=None, C1=None, C2=None, C3=None, CAD=None, D=None),
    "pulse":   dict(A1=None, A2=None, B=None, C1=None, C2=None, C3=-38, CAD=-35, D=None),
}


def active_rms_db(x):
    mono = x.mean(axis=1)
    hop = int(0.05 * SR)
    frames = [mono[i:i + hop] for i in range(0, len(mono) - hop, hop)]
    rms = np.array([np.sqrt((f ** 2).mean()) for f in frames]) if frames else np.array([0.0])
    act = rms[rms > 10 ** (-60 / 20)]
    if len(act) == 0:
        return None
    return 20 * np.log10(np.sqrt((act ** 2).mean()))


def gain_curve(x, targets, name):
    g = np.zeros(N, np.float32)
    report = []
    for sec, a, b in SECTIONS:
        i0, i1 = int(a * SR), min(N, int(b * SR))
        tgt = targets.get(sec)
        if tgt is None:
            continue
        m = active_rms_db(x[i0:i1])
        if m is None:
            continue
        gdb = float(np.clip(tgt - m, -30, 30))
        g[i0:i1] = 10 ** (gdb / 20)
        report.append(f"{sec}:{gdb:+.1f}")
    # lissage des transitions (0,25 s)
    k = int(0.25 * SR)
    ker = np.hanning(k)
    ker /= ker.sum()
    g = np.convolve(g, ker, mode="same").astype(np.float32)
    print(f"  gains {name:8s} " + " ".join(report), flush=True)
    return g


def main():
    parts = write_parts()
    stems = {}
    for name, tr in parts.items():
        stems[name] = render(tr, 0.5)
    buses, sfx = percussion_and_sfx()
    stems.update(buses)

    # couleur par piste
    stems["piano"] = hp(lp(stems["piano"], 6500), 60)  # piano « feutré »
    stems["strings"] = hp(stems["strings"], 45)
    stems["choir"] = lp(hp(stems["choir"], 180), 7000)
    stems["pizz"] = hp(stems["pizz"], 120)

    music = np.zeros((N, 2), np.float32)
    for k, v in stems.items():
        v = v.astype(np.float32) * gain_curve(v, TARGETS[k], k)[:, None]
        stems[k] = v
        sf.write(STEMS / f"{k}.wav", v, SR, subtype="FLOAT")
        music += v
    # réverbération : salle chaleureuse
    music = reverb(music, IR_HALL, 0.30)
    sfx = reverb(sfx.astype(np.float32), IR_HALL, 0.35)
    # limiteur doux de bus (aucun écrêtage dur)
    pk = np.abs(music).max()
    if pk > 0.9:
        music *= 0.9 / pk
    fade_len = int(2.6 * SR)
    end = int(T_TOTAL * SR)
    music[end - fade_len:end] *= np.linspace(1, 0, fade_len)[:, None] ** 1.5
    music = music[:end]
    sfx = sfx[:end]
    sf.write(A / "music_tl.wav", music, SR, subtype="FLOAT")
    sf.write(A / "sfx_tl.wav", sfx, SR, subtype="FLOAT")
    for nm, x in (("music", music), ("sfx", sfx)):
        print(f"{nm}: pic {20 * np.log10(np.abs(x).max() + 1e-9):.1f} dBFS, durée {len(x) / SR:.2f} s")


if __name__ == "__main__":
    main()
