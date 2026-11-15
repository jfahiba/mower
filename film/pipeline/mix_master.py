"""Mixage final + mastering (broadcast / plateformes).

Entrées (work/audio, temps timeline) : voice_tl, amb_tl, music_tl, sfx_tl.
  - voix prioritaire : la musique est atténuée (ducking) d'après l'enveloppe de la
    voix (anticipation 60 ms, attaque 60 ms, relâche 450 ms, profondeur 8 dB) ;
  - effets : scintillement de la révélation baissé sous la voix ;
  - bus master : passe-haut 25 Hz, normalisation à -14 LUFS intégrés
    (ITU-R BS.1770-4, pyloudnorm), limiteur à anticipation, true-peak -1 dBTP
    (détection suréchantillonnée x4).
Sorties : remotion/public/audio/mix.wav (48 kHz, 24 bits) + stems ajustés
          remotion/public/audio/stems/{voice,music,sfx,amb}.wav
"""
import json
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy.signal import butter, resample_poly, sosfilt

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "work/audio"
OUT = ROOT / "remotion/public/audio"
(OUT / "stems").mkdir(parents=True, exist_ok=True)
SR = 48000
TARGET_LUFS = -14.0
CEILING_DBTP = -1.0

TL = json.loads((ROOT / "remotion/src/data/timeline.json").read_text())
FPS = TL["fps"]


def load(name):
    x, sr = sf.read(A / name, dtype="float32", always_2d=True)
    assert sr == SR
    return x


def smooth_gain(target, attack_s, release_s):
    """Lissage asymétrique (descente = attaque, remontée = relâche) d'une courbe de gain."""
    a = np.exp(-1 / (attack_s * SR))
    r = np.exp(-1 / (release_s * SR))
    out = np.empty_like(target)
    g = target[0]
    # traitement par blocs de 32 échantillons pour la vitesse (précision suffisante)
    B = 32
    for i in range(0, len(target), B):
        tgt = target[i:i + B].min()
        coef = a ** B if tgt < g else r ** B
        g = tgt + (g - tgt) * coef
        out[i:i + B] = g
    return out


def voice_activity_gain(voice, depth_db=8.0, lookahead_s=0.06):
    mono = np.abs(voice.mean(axis=1))
    win = int(0.03 * SR)
    env = np.sqrt(np.convolve(mono ** 2, np.ones(win) / win, mode="same"))
    env_db = 20 * np.log10(env + 1e-9)
    # activité : -50 dBFS (voix) -> 0 ; transition douce sur 10 dB
    act = np.clip((env_db + 52) / 10, 0, 1)
    la = int(lookahead_s * SR)
    act = np.concatenate([act[la:], np.zeros(la)])  # anticipation
    target = 10 ** (-depth_db * act / 20)
    return smooth_gain(target.astype(np.float32), 0.06, 0.45)


def true_peak_limiter(x, ceiling_db, lookahead_s=0.005, release_s=0.08):
    ceil = 10 ** (ceiling_db / 20)
    up = resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(axis=1)
    pk = pk.reshape(-1, 4).max(axis=1)[: len(x)]  # pic true-peak par échantillon
    need = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    la = int(lookahead_s * SR)
    # minimum glissant sur la fenêtre d'anticipation
    from scipy.ndimage import minimum_filter1d
    need = minimum_filter1d(need, size=2 * la + 1, mode="nearest")
    need = np.concatenate([need[la:], np.ones(la)])
    g = smooth_gain(need.astype(np.float32), 0.0015, release_s)
    g = np.minimum(g, need)  # garantie stricte
    return x * g[:, None], float(20 * np.log10(g.min()))


def true_peak_db(x):
    up = resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.abs(up).max() + 1e-12)


def main():
    voice = load("voice_tl.wav")
    amb = load("amb_tl.wav")
    music = load("music_tl.wav")
    sfx = load("sfx_tl.wav")
    n = min(len(voice), len(music), len(sfx), len(amb))
    voice, amb, music, sfx = voice[:n], amb[:n], music[:n], sfx[:n]
    meter = pyln.Meter(SR)

    # niveaux relatifs (avant mastering) — la voix sert de référence
    v_l = meter.integrated_loudness(voice)
    voice *= 10 ** ((-17.0 - v_l) / 20)  # voix ≈ -17 LUFS avant master

    # scintillement de la révélation : -10 dB (il précède « le souper de Noël »)
    t_sh = TL["moments"][1]["tlFrom"] / FPS
    i0, i1 = int((t_sh - 0.4) * SR), int((t_sh + 4.0) * SR)
    sfx[i0:i1] *= 10 ** (-10 / 20)
    # whooshes et impact : niveau global des effets
    sfx *= 10 ** (-4 / 20)

    # ambiance réelle du bureau : présente mais discrète
    a_act = amb[np.abs(amb).max(axis=1) > 1e-4]
    if len(a_act):
        a_rms = 20 * np.log10(np.sqrt((a_act ** 2).mean()) + 1e-9)
        amb *= 10 ** ((-40 - a_rms) / 20)

    # musique : niveau global puis ducking sous la voix
    music *= 10 ** (2.0 / 20)
    duck = voice_activity_gain(voice)
    music_d = music * duck[:, None]

    mix = voice + amb + music_d + sfx
    mix = sosfilt(butter(2, 25, btype="high", fs=SR, output="sos"), mix, axis=0).astype(np.float32)

    # normalisation + limiteur true-peak (itératif : le limiteur retire un peu d'énergie)
    for it in range(3):
        L = meter.integrated_loudness(mix)
        mix *= 10 ** ((TARGET_LUFS - L) / 20)
        mix, gr = true_peak_limiter(mix, CEILING_DBTP - 0.1)
    L = meter.integrated_loudness(mix)
    tp = true_peak_db(mix)
    print(f"master : {L:.2f} LUFS intégrés, true-peak {tp:.2f} dBTP, réduction max limiteur {gr:.1f} dB")

    # loudness court terme sur les moments clés
    def st(a, b):
        seg = mix[int(a * SR):int(b * SR)]
        return meter.integrated_loudness(seg) if len(seg) > SR // 2 else float("nan")
    print(f"  timelapse 0–12 s     : {st(0, 11.8):.1f} LUFS")
    print(f"  impact 12–14 s       : {st(12, 14):.1f} LUFS")
    print(f"  message 16–57 s      : {st(16, 57):.1f} LUFS")
    print(f"  carton 59–62 s       : {st(59, 62.4):.1f} LUFS")

    # musique seule pendant la voix (vérifie l'écart voix/musique)
    gain_total = 10 ** ((L - meter.integrated_loudness(mix)) / 20)
    sf.write(OUT / "mix.wav", mix, SR, subtype="PCM_24")
    # stems (mêmes gains que dans le mix, avant normalisation finale)
    for nm, x in (("voice", voice), ("music", music_d), ("sfx", sfx), ("amb", amb)):
        sf.write(OUT / "stems" / f"{nm}.wav", x, SR, subtype="PCM_24")
    vm = meter.integrated_loudness(voice[int(16 * SR):int(57 * SR)])
    mm = meter.integrated_loudness(music_d[int(16 * SR):int(57 * SR)])
    print(f"  écart voix/musique (16–57 s) : {vm - mm:.1f} LU (voix {vm:.1f}, musique {mm:.1f})")
    del gain_total


if __name__ == "__main__":
    main()
