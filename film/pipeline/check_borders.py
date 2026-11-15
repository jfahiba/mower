"""Détecte les vrais bords noirs de stabilisation : un côté dont la bande de 2 px
est quasi noire pure (Y<8) sur plus de 25 % de sa longueur."""
import subprocess, sys
import numpy as np
W, H = 180, 320
for path in sys.argv[1:]:
    p = subprocess.Popen(["ffmpeg","-v","error","-i",path,"-vf",f"scale={W}:{H}:flags=area","-f","rawvideo","-pix_fmt","gray","-"], stdout=subprocess.PIPE)
    bad = n = 0; worst = 0.0; bad_t = []
    while True:
        b = p.stdout.read(W*H)
        if len(b) < W*H: break
        y = np.frombuffer(b, np.uint8).reshape(H, W)
        sides = [y[:2].min(0), y[-2:].min(0), y[:, :2].min(1), y[:, -2:].min(1)]
        frac = max(float((s < 8).mean()) for s in sides)
        worst = max(worst, frac)
        if frac > 0.25:
            bad += 1; bad_t.append(round(n/30, 2))
        n += 1
    print(f"{path}: {bad}/{n} images avec bord noir, pire côté={worst:.0%}; ex: {bad_t[:8]}{'...' if len(bad_t)>8 else ''}")
