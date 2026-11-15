"""Contrôle labial INDICATIF (heuristique) — les mesures décisives sont dans qc.py.

Limite constatée : la corrélation bouche/voix est faible (~0,1) et bimodale
(pics à 0 et à environ −8 images, soit une période syllabique) ; elle ne permet
pas de trancher seule. La synchronisation est démontrée par qc.py : alignement de
l'image sur la source (signature de mouvement, corrélation > 0,9) + alignement
de la voix sur la source (intercorrélation, < 0,5 ms) + audio final = mix.

Activité de la bouche (différence d'images dans la zone de la bouche, repères
YuNet) corrélée à l'enveloppe de la voix (RMS à 30 i/s). Le décalage au maximum
de corrélation est mesuré sur la source WA0048 (référence) et sur le film monté
(partie message) : s'ils sont égaux à ±1 image, la synchronisation est intacte.

Usage : python lipsync_check.py <film.mp4> [film_t0_s film_t1_s]
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL = str(ROOT / "work/models/yunet.onnx")


def mouth_activity(video, t0, t1, w=540, h=960):
    det = cv2.FaceDetectorYN.create(MODEL, "", (w, h), 0.6, 0.3, 5000)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", str(video),
                          "-vf", f"fps=30,scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         stdout=subprocess.PIPE)
    prev = None
    act = []
    while True:
        b = p.stdout.read(w * h * 3)
        if len(b) < w * h * 3:
            break
        img = np.frombuffer(b, np.uint8).reshape(h, w, 3)
        _, faces = det.detect(img)
        val = 0.0
        if faces is not None and len(faces):
            f = max(faces, key=lambda r: r[2] * r[3])
            # repères : 10-11 coin droit bouche, 12-13 coin gauche bouche
            mx = (f[10] + f[12]) / 2
            my = (f[11] + f[13]) / 2
            fw = f[2]
            x0, x1 = int(mx - 0.45 * fw), int(mx + 0.45 * fw)
            y0, y1 = int(my - 0.25 * fw), int(my + 0.30 * fw)
            g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            roi = cv2.resize(g[max(0, y0):y1, max(0, x0):x1], (64, 40)).astype(np.float32)
            if prev is not None:
                val = float(np.abs(roi - prev).mean())
            prev = roi
        else:
            prev = None
        act.append(val)
    return np.array(act)


def voice_env(video, t0, t1):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", str(video),
                        "-map", "0:a:0", "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, np.float32)
    hop = 1600
    return np.array([np.sqrt((a[i:i + hop] ** 2).mean()) for i in range(0, len(a) - hop + 1, hop)])


def suppress_cuts(act, t0, cut_frames):
    """Neutralise les images de coupe/recadrage (sauts de cadre sans rapport avec
    l'articulation) : elles biaiseraient la corrélation vers les attaques de phrase."""
    a = act.copy()
    med = float(np.median(a[a > 0])) if (a > 0).any() else 0.0
    f0 = int(round(t0 * 30))
    for cf in cut_frames:
        k = cf - f0
        for j in range(k - 1, k + 3):
            if 0 <= j < len(a):
                a[j] = med
    return a


def best_lag(act, env, max_lag=15):
    n = min(len(act), len(env))
    a = act[:n] - act[:n].mean()
    e = np.diff(np.concatenate([[env[0]], env[:n]]))  # variations d'énergie ~ mouvements d'articulation
    e = np.abs(e) - np.abs(e).mean()
    best = None
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            c = np.corrcoef(a[lag:], e[: n - lag])[0, 1]
        else:
            c = np.corrcoef(a[: n + lag], e[-lag:])[0, 1]
        if best is None or c > best[1]:
            best = (lag, c)
    return best


def main():
    film = sys.argv[1]
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 16.0
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 58.0
    src = ROOT / "sources/WA0048.mp4"
    ref = best_lag(mouth_activity(src, 2.0, 45.0), voice_env(src, 2.0, 45.0))
    import json
    tl = json.loads((ROOT / "remotion/src/data/timeline.json").read_text())
    cuts = sorted({f["tlFrom"] for f in tl["framing"]} | {sg["tlFrom"] for sg in tl["message"]["segments"]})
    # NB : l'enveloppe est prise sur la voix isolée du film (stem, même timeline) :
    # la musique et son ducking, liés aux attaques de phrase, fausseraient la mesure.
    stem = ROOT / "remotion/public/audio/stems/voice.wav"
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", str(stem), "-ac", "1",
                        "-ar", "48000", "-f", "f32le", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, np.float32)
    env = np.array([np.sqrt((a[i:i + 1600] ** 2).mean()) for i in range(0, len(a) - 1600 + 1, 1600)])
    out = best_lag(suppress_cuts(mouth_activity(film, t0, t1), t0, cuts), env)
    print(f"source WA0048 : décalage {ref[0]:+d} image(s) (corrélation {ref[1]:.3f})")
    print(f"film monté    : décalage {out[0]:+d} image(s) (corrélation {out[1]:.3f})")
    ok = abs(out[0] - ref[0]) <= 1
    print("indication :", "identique à la source ±1 image" if ok else
          "pic principal différent de la source (métrique bimodale) — se référer aux mesures directes de qc.py")


if __name__ == "__main__":
    main()
