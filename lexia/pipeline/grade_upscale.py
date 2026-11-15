"""Étalonnage + agrandissement 4K (2160x3840, 30 i/s CFR) des 5 sources Lexia.
Réutilise la chaîne et le LUT du film précédent (film/pipeline/grading.py) avec une
balance des blancs mesurée sur le mur du bureau (lumière tungstène, très chaude)."""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, "/home/user/mower/film/pipeline")
import grading as G
G.TARGET_RG, G.TARGET_BG = 1.04, 0.94
G.MEASURED.update({"WA0075": (1.067, 0.912), "WA0076": (1.085, 0.900), "WA0077": (1.078, 0.904),
                   "WA0078": (1.084, 0.901), "WA0079": (1.122, 0.884)})
for n in ["WA0075", "WA0076", "WA0077", "WA0078"]:
    G.TWEAKS[n] = dict(exposure=1.04, sat=0.98, gamma=1.03, target_rg=1.04)
G.TWEAKS["WA0079"] = dict(exposure=1.12, sat=0.97, gamma=1.06, target_rg=1.04)
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "remotion_media"
OUT.mkdir(parents=True, exist_ok=True)
def job(n):
    chain = "fps=30," + G.grade_chain(n, upscale=(2160, 3840), sharpen=0.55, denoise=True)
    out = OUT / f"{n}.mp4"
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / f"sources/{n}.mp4"), "-vf", chain, "-threads", "4",
        "-c:v", "libx264", "-preset", "medium", "-crf", "13", "-g", "30", "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-movflags", "+faststart", "-an", str(out)], capture_output=True, text=True)
    print(n, "OK" if r.returncode == 0 else r.stderr[-500:], flush=True)
with ThreadPoolExecutor(2) as ex:
    list(ex.map(job, sys.argv[2:] or ["WA0077", "WA0079", "WA0078", "WA0076", "WA0075"]))
