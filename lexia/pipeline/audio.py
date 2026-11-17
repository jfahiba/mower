"""Son des capsules Lexia : voix traitée + musique originale + déclics photo + mix.

Réutilise les outils du film précédent (film/pipeline) :
  - chaîne voix broadcast (audio_voice.VOICE_CHAIN) + compensation de latence ;
  - instruments MuseScore General (licence MIT) via FluidSynth, réverbération à
    convolution, synthèse (compose_music) ;
  - ducking, normalisation -14 LUFS (BS.1770), limiteur true-peak -1 dBTP (mix_master).
Thème original « Lexia » (I–V–vi–IV en croches de piano feutré, cordes tenues),
une tonalité par capsule ; carillon sur le carton final ; déclic d'obturateur
synthétisé à chaque photo.
Sortie : remotion/public/audio/<ID>.wav
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, "/home/user/mower/film/pipeline")
import audio_voice as AV  # noqa: E402
import compose_music as CM  # noqa: E402
import mix_master as MM  # noqa: E402
import pyloudnorm as pyln  # noqa: E402

SR = 48000
SPF = SR // 30
W = ROOT / "work/audio"
W.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "remotion/public/audio"
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((ROOT / "remotion/src/data/capsules.json").read_text())
KEYS = {"C01": 2, "C02": 7, "C03": 0, "C04": 5, "C05": 9, "C06": 3, "C07": 10, "C08": 4, "C09": 7, "C10": 2, "FULL": 2}
BPM = 92
BEAT = 60 / BPM


def voice(src):
    p = W / f"{src}_voice.wav"
    if p.exists():
        return sf.read(p, dtype="float32")[0]
    raw = ROOT / f"analysis/audio/{src}_48k.wav"
    tmp = W / f"{src}_tmp.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", AV.VOICE_CHAIN, "-ar", str(SR),
                    "-c:a", "pcm_f32le", str(tmp)], check=True)
    v = sf.read(tmp, dtype="float32")[0]
    ref = sf.read(raw, dtype="float32")[0]
    ref = ref.mean(axis=1) if ref.ndim > 1 else ref
    a, b = ref[: 20 * SR], v[: 20 * SR]
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    m = int(0.2 * SR)
    lag = int(np.argmax(np.abs(np.concatenate([c[-m:], c[: m + 1]])))) - m
    v = np.concatenate([v[lag:], np.zeros(max(lag, 0), np.float32)]) if lag >= 0 else np.concatenate([np.zeros(-lag, np.float32), v[:lag]])
    sf.write(p, v, SR, subtype="FLOAT")
    print(f"voix {src} : latence compensée {lag / SR * 1000:.1f} ms", flush=True)
    return v


def shutter():
    """Déclic d'appareil photo : rideau (2 claquements brefs) + miroir + légère résonance."""
    L = int(0.35 * SR)
    t = np.arange(L) / SR
    rng = np.random.default_rng(5)
    out = np.zeros(L)
    for t0, g, f in [(0.0, 1.0, 3500), (0.045, 0.75, 2600), (0.11, 0.35, 1800)]:
        i = int(t0 * SR)
        n = CM.bp(rng.standard_normal(L - i), f * 0.5, min(f * 2.2, 20000), 2) * np.exp(-t[: L - i] / 0.006)
        thump = np.sin(2 * np.pi * 180 * t[: L - i]) * np.exp(-t[: L - i] / 0.012) * 0.4
        out[i:] += g * (n / (np.abs(n).max() + 1e-9) + thump)
    out = out / np.abs(out).max() * 0.5
    return np.stack([out, np.roll(out, 24)], axis=1)


def music(cap, total_s, key):
    """Thème Lexia : I–V–vi–IV (croches de piano feutré + cordes), transposé."""
    N = int((total_s + 0.5) * SR)
    CM.N = N
    CM.T_TOTAL = total_s
    tr = key - 2  # thème écrit en ré
    piano, strings, celesta, basses = CM.Track("piano", 0), CM.Track("strings", 49), CM.Track("celesta", 8), CM.Track("basses", 43)
    prog = ["D", "A", "Bm", "G"]
    chords = {"D": ["D3", "A3", "D4", "F#4", "A4"], "A": ["A2", "E3", "A3", "C#4", "E4"],
              "Bm": ["B2", "F#3", "B3", "D4", "F#4"], "G": ["G2", "D3", "G3", "B3", "D4"]}
    arps = {"D": ["D4", "F#4", "A4", "D5"], "A": ["C#4", "E4", "A4", "C#5"], "Bm": ["B3", "D4", "F#4", "B4"], "G": ["B3", "D4", "G4", "B4"]}
    bar = 4 * BEAT
    body_s = cap["bodyEnd"] / 30
    nb = int(np.ceil(total_s / bar)) + 1
    strings.cc(0, 11, 30)
    strings.ramp(0, 2.0, 11, 30, 70)
    for b in range(nb):
        t0 = b * bar
        if t0 > total_s:
            break
        c = prog[b % 4]
        final = t0 >= body_s - 0.2
        if final:
            c = "D"
        for p in chords[c]:
            strings.note(t0, bar, CM.n(p) + tr, 62)
        basses.note(t0, bar * 0.98, CM.n(chords[c][0]) + tr, 50)
        pattern = [0, 1, 2, 3, 2, 1, 2, 3]
        for k in range(8):
            piano.note(t0 + k * BEAT / 2, BEAT * 0.45, CM.n(arps[c][pattern[k]]) + tr, 40 + (8 if k % 2 == 0 else 0))
    strings.ramp(body_s - 0.5, total_s, 11, 70, 20)
    for k, p in enumerate(["A5", "D6", "F#6", "A6"]):
        celesta.note(body_s + 0.25 + k * 0.16, 2.0, CM.n(p) + tr, 56 - 4 * k)
    stems = {}
    for name, trk, g in [("piano", piano, 0.5), ("strings", strings, 0.5), ("celesta", celesta, 0.5), ("basses", basses, 0.5)]:
        trk.name = f"{cap['id']}_{name}"
        stems[name] = CM.render(trk, g)
    stems["piano"] = CM.hp(CM.lp(stems["piano"], 6000), 60)
    stems["strings"] = CM.hp(stems["strings"], 50)
    targets = {"piano": -27, "strings": -29, "celesta": -30, "basses": -34}
    mix = np.zeros((N, 2), np.float32)
    for k, v in stems.items():
        r = CM.active_rms_db(v)
        if r is not None:
            mix += (v * 10 ** ((targets[k] - r) / 20)).astype(np.float32)
    mix = CM.reverb(mix, CM.IR_HALL, 0.3)
    fi, fo = int(0.6 * SR), int(1.6 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    end = int(total_s * SR)
    mix[end - fo:end] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    return mix[:end]


def build(cap):
    total = cap["durationInFrames"]
    n = total * SPF
    v = np.zeros(n, np.float32)
    for s in cap["segments"]:
        src = voice(s["src"])
        seg = AV.fade(src[s["srcFrom"] * SPF: s["srcTo"] * SPF], int(0.006 * SR))
        o = s["tlFrom"] * SPF
        v[o:o + len(seg)] += seg
    vs = np.stack([v, v], axis=1)
    meter = pyln.Meter(SR)
    vs *= 10 ** ((-17 - meter.integrated_loudness(vs)) / 20)
    m = music(cap, total / 30, KEYS[cap["id"]])
    m = np.pad(m, ((0, max(0, n - len(m))), (0, 0)))[:n]
    duck = MM.voice_activity_gain(vs, depth_db=9.0)
    sfx = np.zeros((n, 2), np.float32)
    sh = shutter()
    for p in cap["photos"]:
        CM.place(sfx, p["tlFrom"] / 30 - 0.02, sh, gain=0.55)
    for chp in cap.get("chapters", []):
        if chp["tlFrom"] > 0:  # whoosh sur la transition de chapitre
            CM.place(sfx, chp["tlFrom"] / 30 - 0.3, CM.whoosh(0.5, direction=1), gain=0.45)
    mix = vs + m * duck[:, None] * 10 ** (1.5 / 20) + sfx
    for _ in range(3):
        L = meter.integrated_loudness(mix)
        mix *= 10 ** ((-14 - L) / 20)
        mix, _gr = MM.true_peak_limiter(mix, -1.1)
    sf.write(OUT / f"{cap['id']}.wav", mix, SR, subtype="PCM_24")
    print(f"{cap['id']}: {meter.integrated_loudness(mix):.2f} LUFS, TP {MM.true_peak_db(mix):.2f} dBTP", flush=True)


if __name__ == "__main__":
    ids = set(sys.argv[1:])
    for c in DATA["capsules"]:
        if not ids or c["id"] in ids:
            build(c)
