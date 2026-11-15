"""Étalonnage + agrandissement 4K (2160x3840) des médias utilisés par Remotion.

  - plans du timelapse : work/remap/<ID>.mkv -> remotion/public/media/<ID>.mp4
  - message            : sources/WA0048.mp4 -> remotion/public/media/message.mp4
Chaîne (pipeline/grading.py) : débruitage léger -> balance des blancs par source
-> LUT film_look.cube -> zscale spline36 -> CAS (netteté adaptative) -> Rec.709.

NB : la source fait 720x1280 ; l'agrandissement x3 est de haute qualité mais ne
crée pas de vrais détails 4K.

Encodage intermédiaire : H.264 High 4:2:0 8 bits CRF 12, GOP 1 s (accès rapide
aux images par Remotion), balises Rec.709.
Usage : python grade_upscale.py [ID|message ...]
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import edl  # noqa: E402
import grading  # noqa: E402

OUT = ROOT / "remotion/public/media"
OUT.mkdir(parents=True, exist_ok=True)
ENC = [
    "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-profile:v", "high", "-level", "5.2",
    "-g", "30", "-keyint_min", "30", "-sc_threshold", "0", "-pix_fmt", "yuv420p",
    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
    "-movflags", "+faststart", "-an",
]


def job(name, src_path, src_id, sharpen, pre=""):
    chain = grading.grade_chain(src_id, upscale=(edl.WIDTH, edl.HEIGHT), sharpen=sharpen, denoise=True)
    if pre:
        chain = pre + "," + chain
    out = OUT / f"{name}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src_path), "-vf", chain, "-threads", "4", *ENC, str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ÉCHEC {name}: {r.stderr[-800:]}", flush=True)
        return
    n = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
         "stream=nb_read_packets,width,height", "-of", "csv=p=0", str(out)],
        capture_output=True, text=True).stdout.strip()
    print(f"{name}: {n} ({out.stat().st_size / 1e6:.1f} Mo)", flush=True)


def main():
    want = set(sys.argv[1:])
    jobs = []
    for s in edl.TIMELAPSE:
        if not want or s["id"] in want:
            jobs.append((s["id"], ROOT / "work/remap" / f"{s['id']}.mkv", s["src"], 0.50, ""))
    if not want or "message" in want:
        # fps=30 : CFR exact (la source WhatsApp est légèrement VFR) => image n = n/30 s
        jobs.append(("message", ROOT / "sources" / f"{edl.MESSAGE_SRC}.mp4", edl.MESSAGE_SRC, 0.55, "fps=30"))
    # le message (le plus long) en premier
    jobs.sort(key=lambda j: j[0] != "message")
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(lambda j: job(*j), jobs))


if __name__ == "__main__":
    main()
