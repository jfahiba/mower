"""Analyse image par image des sources : netteté, mouvement caméra, colorimétrie.

Usage: python analyze_video.py <out_json> <video> [<video> ...]

Pour chaque image (décodée en 180x320 niveaux de gris + YUV moyen) :
  - sharp  : variance du Laplacien (netteté relative ; flou de bouger -> faible)
  - dx, dy : translation globale estimée par corrélation de phase (pixels @180x320)
  - y,u,v  : moyennes YUV (exposition / balance des blancs)
Résume par seconde et par clip ; sert à choisir les passages du timelapse et
à harmoniser l'étalonnage.
"""
import json
import subprocess
import sys

import cv2
import numpy as np

W, H = 180, 320


def frames(path):
    cmd = [
        "ffmpeg", "-v", "error", "-i", path,
        "-vf", f"scale={W}:{H}:flags=area,format=yuv444p",
        "-f", "rawvideo", "-pix_fmt", "yuv444p", "-",
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = W * H * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        a = np.frombuffer(buf, np.uint8).reshape(3, H, W)
        yield a
    p.wait()


def analyze(path):
    rows = []
    prev = None
    win = cv2.createHanningWindow((W, H), cv2.CV_32F)
    for i, yuv in enumerate(frames(path)):
        y = yuv[0].astype(np.float32)
        sharp = float(cv2.Laplacian(y, cv2.CV_32F).var())
        dx = dy = 0.0
        resp = 0.0
        if prev is not None:
            (dx, dy), resp = cv2.phaseCorrelate(prev, y, win)
        prev = y
        rows.append(
            {
                "i": i,
                "t": i / 30.0,
                "sharp": round(sharp, 2),
                "dx": round(float(dx), 3),
                "dy": round(float(dy), 3),
                "resp": round(float(resp), 3),
                "y": round(float(yuv[0].mean()), 2),
                "u": round(float(yuv[1].mean()), 2),
                "v": round(float(yuv[2].mean()), 2),
            }
        )
    return rows


def summarize(rows):
    t = np.array([r["t"] for r in rows])
    sharp = np.array([r["sharp"] for r in rows])
    dx = np.array([r["dx"] for r in rows])
    dy = np.array([r["dy"] for r in rows])
    mot = np.hypot(dx, dy)
    # tremblement = composante haute fréquence du mouvement (mouvement - lissage)
    k = 15
    ker = np.ones(k) / k
    sdx = np.convolve(dx, ker, mode="same")
    sdy = np.convolve(dy, ker, mode="same")
    jitter = np.hypot(dx - sdx, dy - sdy)
    per_sec = []
    for s in range(int(np.ceil(t[-1] + 1e-6))):
        m = (t >= s) & (t < s + 1)
        if not m.any():
            continue
        per_sec.append(
            {
                "sec": s,
                "sharp_med": round(float(np.median(sharp[m])), 1),
                "motion_med": round(float(np.median(mot[m])), 2),
                "jitter_mean": round(float(jitter[m].mean()), 2),
                "y_mean": round(float(np.mean([r["y"] for r, mm in zip(rows, m) if mm])), 1),
            }
        )
    return {
        "frames": len(rows),
        "sharp_median": round(float(np.median(sharp)), 1),
        "sharp_p10": round(float(np.percentile(sharp, 10)), 1),
        "motion_median": round(float(np.median(mot)), 2),
        "jitter_mean": round(float(jitter.mean()), 2),
        "y_mean": round(float(np.mean([r["y"] for r in rows])), 1),
        "u_mean": round(float(np.mean([r["u"] for r in rows])), 1),
        "v_mean": round(float(np.mean([r["v"] for r in rows])), 1),
        "per_sec": per_sec,
    }


if __name__ == "__main__":
    out, *vids = sys.argv[1:]
    res = {}
    for v in vids:
        rows = analyze(v)
        summ = summarize(rows)
        res[v] = {"summary": summ, "rows": rows}
        print(
            f"{v}: frames={summ['frames']} sharp_med={summ['sharp_median']} p10={summ['sharp_p10']} "
            f"motion_med={summ['motion_median']} jitter={summ['jitter_mean']} "
            f"YUV=({summ['y_mean']},{summ['u_mean']},{summ['v_mean']})",
            flush=True,
        )
        for ps in summ["per_sec"]:
            print(
                f"   s{ps['sec']:02d} sharp={ps['sharp_med']:7.1f} motion={ps['motion_med']:5.2f} "
                f"jitter={ps['jitter_mean']:5.2f} Y={ps['y_mean']:.0f}"
            )
    json.dump(res, open(out, "w"))
