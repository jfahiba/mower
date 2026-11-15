"""Planche de contact des séquences retenues, extraite du rendu final.

Usage : python contact_sheet.py <video> <sortie.jpg>
Rangées : plans du timelapse (source, vitesse, timecode) ; transition signature
(image par image) ; cadrages du message ; moments typographiques ; carton final.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TL = json.loads((ROOT / "remotion/src/data/timeline.json").read_text())
FPS = TL["fps"]
CW, CH = 360, 640  # vignette
LAB = 92  # bandeau de légende
COLS = 6
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_R = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"


def tc(f):
    s = f / FPS
    return f"{int(s // 60)}:{s % 60:04.1f}"


def grab(video, frame):
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{frame / FPS + 0.001:.4f}", "-i", str(video), "-vf",
         f"scale={CW}:{CH}:flags=lanczos", "-frames:v", "1",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    return Image.frombytes("RGB", (CW, CH), r.stdout)


def main():
    video, out = sys.argv[1], sys.argv[2]
    cells = []  # (rangée, frame, titre, sous-titre)
    for s in TL["timelapse"]:
        mid = s["from_"] + s["durationInFrames"] // 2
        if s["id"] == "A1":
            cells.append(("Timelapse", s["from_"] + 14, "A1 · WA0049 · impact", f"ralenti 10x→1x · {tc(s['from_'] + 14)}"))
            cells.append(("Timelapse", s["from_"] + 70, "A1 · WA0049 · 1x", f"ambiance réelle + J-cut voix · {tc(s['from_'] + 70)}"))
        else:
            cells.append(("Timelapse", mid, f"{s['id']} · {s['src']} · ×{s['avgSpeed']:g}", f"{s['transIn']} · {tc(s['from_'])}–{tc(s['from_'] + s['durationInFrames'])}"))
    vi = TL["message"]["videoIn"]
    for k, f in enumerate([vi - 8, vi - 4, vi - 1, vi, vi + 3, vi + 10]):
        cells.append(("Transition signature", f, f"Raccord · image {f}", ["zoom vers le tableau", "zoom vers le tableau", "flou radial max", "coupe (WA0048)", "flou radial décroissant", "message, cadrage posé"][k]))
    for fr in TL["framing"][1:]:
        f = fr["tlFrom"] + 10
        note = fr["note"] if len(fr["note"]) <= 34 else fr["note"][:33].rstrip() + "…"
        cells.append(("Message (1x)", f, f"Message · {tc(f)} · ×{fr['scale']:.2f}", note))
    for m in TL["moments"]:
        f = {"triad": m["tlTo"] - 10, "event": m["tlFrom"] + 40, "signoff": m["tlFrom"] + 20}[m["kind"]]
        cells.append(("Typographie", f, {"triad": "Triptyque", "event": "Révélation", "signoff": "Signature"}[m["kind"]] + f" · {tc(f)}", ""))
    cells.append(("Typographie", TL["durationInFrames"] - 30, f"Carton final · {tc(TL['durationInFrames'] - 30)}", "modifiable (props Remotion)"))

    rows = []
    cur = None
    for c in cells:
        if c[0] != cur or len(rows[-1][1]) == COLS:
            rows.append((c[0], []))
            cur = c[0]
        rows[-1][1].append(c)

    head = 210
    rowtitle = 60
    Wd = COLS * CW + (COLS + 1) * 16
    Ht = head + sum(rowtitle + CH + LAB + 16 for _ in rows) + 30
    sheet = Image.new("RGB", (Wd, Ht), (16, 9, 11))
    d = ImageDraw.Draw(sheet)
    fb = lambda s: ImageFont.truetype(FONT_B, s)
    fr_ = lambda s: ImageFont.truetype(FONT_R, s)
    d.text((24, 28), "Souper de Noël 2026 — planche de contact des séquences retenues", fill=(235, 201, 143), font=fb(44))
    d.text((24, 96), f"Vertical 9:16 · 2160×3840 · {FPS} i/s · {TL['durationInFrames']} images ({TL['durationInFrames'] / FPS:.1f} s) · "
           f"timelapse {TL['impactFrame'] / FPS:.1f} s + transition {(vi - TL['impactFrame']) / FPS:.1f} s + message 1x + carton", fill=(230, 220, 210), font=fr_(28))
    d.text((24, 140), "Sources : WA0042, WA0044, WA0045, WA0047 (courses) · WA0049 (bureau) · WA0048 (message)", fill=(180, 170, 165), font=fr_(26))
    y = head
    for title, rc in rows:
        d.text((16, y + 14), title.upper(), fill=(235, 201, 143), font=fb(28))
        y += rowtitle
        for k, (_, f, t1, t2) in enumerate(rc):
            x = 16 + k * (CW + 16)
            sheet.paste(grab(video, f), (x, y))
            d.text((x + 4, y + CH + 10), t1, fill=(255, 255, 255), font=fb(23))
            d.text((x + 4, y + CH + 46), t2, fill=(200, 190, 185), font=fr_(20))
        y += CH + LAB + 16
    sheet.save(out, quality=88)
    print(f"{out} : {len(cells)} vignettes, {Wd}x{Ht}")


if __name__ == "__main__":
    main()
