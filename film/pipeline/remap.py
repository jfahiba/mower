"""Time-remapping à vitesse variable + frame-blending (obturateur virtuel 180°).

Pour chaque plan du timelapse (pipeline/edl.py) :
  - courbe t_sortie -> t_source interpolée en PCHIP (monotone, C1) => speed ramps
  - chaque image de sortie intègre, en lumière linéaire (gamma 2.2), toutes les
    images source couvertes par sa fenêtre d'exposition (1/60 s de sortie) :
    filtre « boîte » exact avec poids fractionnaires => flou de bouger
    proportionnel à la vitesse, sans scintillement quand la vitesse varie ;
  - sous ~1,25 image source par fenêtre (≈ vitesse < 2,5x), image la plus proche
    (pas de fantômes au ralenti / à 1x).
Entrée : work/stab/<SRC>.mp4 (720x1280, 30 i/s CFR) ; sortie : work/remap/<ID>.mkv
(x264 4:4:4 quasi sans perte, Rec.709 tv).

Usage : python remap.py [ID ...]   (sans argument : tous les plans)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import edl  # noqa: E402

W, H = 720, 1280
FPS = edl.FPS
SHUTTER = 0.5  # 180°
GAMMA = 2.2
NEAREST_BELOW = 1.25  # en images source par fenêtre


def decoder(path, start_frame):
    cmd = [
        "ffmpeg", "-v", "error",
        "-ss", f"{max(0, start_frame - 2) / FPS:.4f}", "-i", str(path),
        "-vf", "scale=in_color_matrix=bt709:in_range=tv:out_range=pc:flags=accurate_rnd+full_chroma_int,format=rgb24",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE), max(0, start_frame - 2)


def encoder(path):
    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv444p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "4",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        str(path),
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def remap_shot(shot):
    keys = shot["remap"]
    tout = np.array([k[0] for k in keys])
    tsrc = np.array([k[1] for k in keys])
    curve = PchipInterpolator(tout, tsrc)
    n = shot["frames"]
    src_path = ROOT / "work/stab" / f"{shot['src']}.mp4"
    nsrc = int(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(src_path)],
        capture_output=True, text=True).stdout.strip())

    # fenêtres d'exposition en temps source
    half = SHUTTER / FPS / 2
    t = np.arange(n) / FPS
    lo = curve(np.clip(t - half, tout[0], tout[-1]))
    hi = curve(np.clip(t + half, tout[0], tout[-1]))
    center = curve(t)
    first_needed = int(np.floor(min(lo.min(), center.min()) * FPS)) - 1
    dec, dec_first = decoder(src_path, max(0, first_needed))
    out_path = ROOT / "work/remap" / f"{shot['id']}.mkv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    enc = encoder(out_path)

    buf = {}  # index source -> image linéaire float32
    next_idx = dec_first
    frame_bytes = W * H * 3

    def get(j):
        nonlocal next_idx
        j = int(min(max(j, 0), nsrc - 1))
        while next_idx <= j:
            b = dec.stdout.read(frame_bytes)
            if len(b) < frame_bytes:
                # fin de flux : on duplique la dernière image disponible
                last = max(buf) if buf else None
                if last is None:
                    raise RuntimeError("flux source vide")
                buf[next_idx] = buf[last]
            else:
                img = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
                buf[next_idx] = img ** GAMMA
            next_idx += 1
        return buf[j]

    speeds = []
    for k in range(n):
        a, b = lo[k] * FPS, hi[k] * FPS  # fenêtre en unités « image source »
        width = b - a
        speeds.append(width / (SHUTTER))
        if width < NEAREST_BELOW:
            acc = get(int(round(center[k] * FPS)))
        else:
            j0 = int(np.floor(a + 0.5))
            j1 = int(np.floor(b + 0.5))
            acc = None
            wsum = 0.0
            for j in range(j0, j1 + 1):
                # image j couvre [j-0.5, j+0.5)
                w = min(b, j + 0.5) - max(a, j - 0.5)
                if w <= 0:
                    continue
                img = get(j)
                acc = img * w if acc is None else acc + img * w
                wsum += w
            acc = acc / wsum
        out = (np.clip(acc, 0, 1) ** (1 / GAMMA) * 255.0 + 0.5).astype(np.uint8)
        enc.stdin.write(out.tobytes())
        # libère les images devenues inutiles
        keep_from = int(np.floor(lo[min(k + 1, n - 1)] * FPS)) - 2
        for idx in [i for i in buf if i < keep_from]:
            del buf[idx]
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.kill()
    sp = np.array(speeds)
    print(f"{shot['id']}: {n} images, vitesse {sp.min():.1f}x → {sp.max():.1f}x (moy. {sp.mean():.1f}x) -> {out_path.name}", flush=True)


def main():
    ids = set(sys.argv[1:])
    for shot in edl.TIMELAPSE:
        if ids and shot["id"] not in ids:
            continue
        remap_shot(shot)


if __name__ == "__main__":
    main()
