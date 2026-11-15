"""Voix (WA0048) : traitement broadcast + montage synchronisé sur la timeline.

Chaîne FFmpeg (voix mono, bande AAC limitée à ~14 kHz, plancher de bruit -65 dB) :
  passe-haut 75 Hz (24 dB/oct) -> débruitage FFT très léger -> EQ : -1,5 dB @180 Hz,
  -3 dB @320 Hz (« carton » du micro de téléphone), +3 dB @3,2 kHz (présence/intelligibilité),
  +1,5 dB plateau aigu 8 kHz -> de-esser -> compression 3:1 douce -> limiteur de sécurité.
Puis découpe aux segments du montage (images source -> échantillons : 1 image = 1600 éch.
à 48 kHz), fondus de 5 ms aux raccords, placement à l'échantillon près.

Sorties : work/audio/voice_proc.wav (voix traitée, temps source)
          work/audio/voice_tl.wav   (voix montée, temps timeline, stéréo double mono)
          work/audio/amb_tl.wav     (ambiance réelle du bureau sur la fin du ralenti)
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "work/audio"
A.mkdir(parents=True, exist_ok=True)
SR = 48000
SPF = SR // 30  # échantillons par image

VOICE_CHAIN = ",".join([
    "pan=mono|c0=0.5*c0+0.5*c1",
    "highpass=f=75:poles=2", "highpass=f=75:poles=2",
    "afftdn=nr=6:nf=-62:tn=1",
    "equalizer=f=180:t=q:w=1.0:g=-1.5",
    "equalizer=f=320:t=q:w=1.1:g=-3",
    "equalizer=f=3200:t=q:w=0.9:g=3",
    "highshelf=f=8000:g=1.5",
    "deesser=i=0.35:m=0.5:f=0.55:s=o",
    "acompressor=threshold=-24dB:ratio=3:attack=6:release=140:knee=6:makeup=3dB",
    "alimiter=limit=0.89:attack=3:release=60:level=false",
])


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return r


def loudness(path):
    r = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    lines = [l.strip() for l in r.stderr.splitlines()]
    out = {}
    for l in lines:
        if l.startswith("I:"):
            out["I"] = l
        if l.startswith("Peak:"):
            out["TP"] = l
    return out


def fade(x, n):
    n = min(n, len(x) // 2)
    if n <= 0:
        return x
    w = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))
    x = x.copy()
    x[:n] *= w
    x[-n:] *= w[::-1]
    return x


def main():
    tl = json.loads((ROOT / "remotion/src/data/timeline.json").read_text())
    total = tl["durationInFrames"] * SPF

    src = ROOT / "analysis/audio/WA0048_48k.wav"
    proc = A / "voice_proc.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", VOICE_CHAIN, "-ar", str(SR), "-c:a", "pcm_f32le", str(proc)])
    print("voix traitée :", loudness(proc))

    v, sr = sf.read(proc, dtype="float32")
    assert sr == SR
    # Compensation de latence : certains filtres (limiteur à anticipation, débruiteur
    # FFT) retardent le signal de quelques dizaines de ms. On mesure le retard par
    # intercorrélation avec la source et on le retire (synchro labiale exacte).
    ref, _ = sf.read(src, dtype="float32")
    ref = ref.mean(axis=1) if ref.ndim > 1 else ref
    a, b = ref[: 30 * SR], v[: 30 * SR]
    nfft = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, nfft) * np.conj(np.fft.rfft(a, nfft)), nfft)
    m = int(0.2 * SR)
    lag = int(np.argmax(np.abs(np.concatenate([c[-m:], c[: m + 1]])))) - m
    if lag > 0:
        v = np.concatenate([v[lag:], np.zeros(lag, np.float32)])
    elif lag < 0:
        v = np.concatenate([np.zeros(-lag, np.float32), v[:lag]])
    print(f"latence de la chaîne voix compensée : {lag} échantillons ({lag / SR * 1000:.1f} ms)")
    out = np.zeros(total, np.float32)
    for s in tl["message"]["segments"]:
        a, b = s["srcFrom"] * SPF, s["srcTo"] * SPF
        seg = fade(v[a:b], int(0.005 * SR))
        o = s["tlFrom"] * SPF
        out[o:o + len(seg)] += seg
    st = np.stack([out, out], axis=1)
    sf.write(A / "voice_tl.wav", st, SR, subtype="FLOAT")
    print("voix montée :", loudness(A / "voice_tl.wav"))

    # Ambiance réelle du bureau (WA0049) sur la partie 1x de A1 : le son ambiant
    # « apparaît naturellement » avant la voix. A1 commence à l'impact ; sa partie
    # 1x couvre les ~1,8 dernières secondes (source 55,03 -> 56,83 s).
    amb_src = ROOT / "analysis/audio/WA0049_48k.wav"
    amb, _ = sf.read(amb_src, dtype="float32")
    amb = amb.mean(axis=1) if amb.ndim > 1 else amb
    a1 = next(s for s in tl["timelapse"] if s["id"] == "A1")
    a1_end = a1["from_"] + a1["durationInFrames"]  # = début image du message
    src_end = 56.83
    dur = 2.4  # s : démarre pendant la fin du ralenti
    seg = amb[int((src_end - dur) * SR): int(src_end * SR)].copy()
    # passe-haut léger, puis enveloppe : fondu d'entrée 0,9 s, sortie 0,6 s sous la voix
    seg = np.asarray(seg, np.float32)
    n_in, n_out = int(0.9 * SR), int(0.6 * SR)
    env = np.ones(len(seg), np.float32)
    env[:n_in] = np.linspace(0, 1, n_in) ** 1.5
    env[-n_out:] = np.linspace(1, 0, n_out)
    seg *= env
    amb_tl = np.zeros(total, np.float32)
    o = a1_end * SPF - len(seg)
    amb_tl[o:o + len(seg)] = seg
    sf.write(A / "amb_tl.wav", np.stack([amb_tl, amb_tl], axis=1), SR, subtype="FLOAT")
    print("ambiance bureau placée de", round(o / SR, 2), "à", round((o + len(seg)) / SR, 2), "s")


if __name__ == "__main__":
    main()
