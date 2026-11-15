"""Contrôle qualité des 10 capsules + planche de contact.
Vérifie pour chaque fichier : images attendues, 30 i/s, 9:16, Rec.709, AAC 48 kHz
stéréo, loudness -14 LUFS / true-peak <= -0,8 dBTP, absence de noir accidentel,
audio identique au mix de référence (décalage)."""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "deliverables"
DATA = json.loads((ROOT / "remotion/src/data/capsules.json").read_text())


def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(p)], capture_output=True, text=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next(s for s in j["streams"] if s["codec_type"] == "audio")
    n = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)
    return j, v, a, n


def loud(p):
    e = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    e = e[e.rfind("Summary:"):]
    return float(re.search(r"I:\s+(-?[\d.]+)", e).group(1)), float(re.search(r"Peak:\s+(-?[\d.]+)", e).group(1))


def black(p):
    e = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(p), "-vf", "scale=270:480,blackdetect=d=0.1:pix_th=0.05", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", e)]


def offset_ms(p, ref):
    r, sr = sf.read(ref, dtype="float32", always_2d=True)
    o = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32).reshape(-1, 2)
    a, b = r[: sr * 15].mean(1), o[: sr * 15].mean(1)
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    m = sr // 2
    cc = np.concatenate([c[-m:], c[: m + 1]])
    return (int(np.argmax(np.abs(cc))) - m) / sr * 1000


def main():
    rep = {}
    ok_all = True
    for c in DATA["capsules"]:
        for kind in ("4K", "WEB"):
            p = D / f"{c['id']}_{kind}.mp4"
            if not p.exists():
                print("MANQUANT", p.name)
                ok_all = False
                continue
            j, v, a, n = probe(p)
            I, TP = loud(p)
            bl = black(p)
            off = offset_ms(p, ROOT / f"remotion/public/audio/{c['id']}.wav")
            chk = dict(frames=n == c["durationInFrames"], fps=v["r_frame_rate"] == "30/1", ratio=v["width"] * 16 == v["height"] * 9,
                       rec709=v.get("color_primaries") == "bt709" and v.get("color_space") == "bt709",
                       audio=a["sample_rate"] == "48000" and a["channels"] == 2, loudness=abs(I + 14) <= 0.6 and TP <= -0.8,
                       no_black=all(s < 0.4 or s > c["durationInFrames"] / 30 - 1 for s, _ in bl), sync=abs(off) < 34)
            ok_all &= all(chk.values())
            rep[p.name] = dict(size_mb=round(int(j["format"]["size"]) / 1e6, 1), codec=f"{v['codec_name']} {v.get('profile')}", res=f"{v['width']}x{v['height']}",
                               frames=n, duration=round(float(j["format"]["duration"]), 2), lufs=I, true_peak=TP, offset_ms=round(off, 1), black=bl, checks=chk)
            print(f"{p.name:14s} {rep[p.name]['size_mb']:6.1f} Mo {v['codec_name']:5s} {v['width']}x{v['height']} {n} img {I} LUFS TP {TP} décalage {off:.1f} ms  "
                  + ("OK" if all(chk.values()) else f"ÉCART {[k for k, x in chk.items() if not x]}"))
    (D / "qc_report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print("TOUT CONFORME" if ok_all else "ÉCARTS À CORRIGER")
    # planche de contact : une rangée par capsule (titre, parole, photo, parole, carton)
    TW, TH = 216, 384
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 22)
    rows = []
    for c in DATA["capsules"]:
        p = D / f"{c['id']}_WEB.mp4"
        if not p.exists():
            continue
        ph = c["photos"][0]["tlFrom"] + 18 if c["photos"] else c["bodyEnd"] // 2
        fr = [40, c["bodyEnd"] // 3, ph, int(c["bodyEnd"] * 0.8), c["durationInFrames"] - 25]
        ims = []
        for f in fr:
            b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{f / 30:.3f}", "-i", str(p), "-frames:v", "1", "-vf", f"scale={TW}:{TH}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            ims.append(Image.frombytes("RGB", (TW, TH), b))
        rows.append((c, ims))
    sheet = Image.new("RGB", (5 * (TW + 8) + 520, len(rows) * (TH + 12) + 90), (11, 26, 46))
    d = ImageDraw.Draw(sheet)
    d.text((16, 20), "Lexia Notaires — Me Rania Arbi répond à vos questions : 10 capsules 9:16 (4K)", fill=(159, 220, 250), font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 30))
    for k, (c, ims) in enumerate(rows):
        y = 80 + k * (TH + 12)
        d.text((16, y + 10), c["id"], fill=(56, 168, 236), font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 40))
        words, line, yy = c["title"].split(" "), "", y + 70
        for w in words:
            if len(line + " " + w) > 24:
                d.text((16, yy), line.strip(), fill=(255, 255, 255), font=font)
                yy += 32
                line = ""
            line += " " + w
        d.text((16, yy), line.strip(), fill=(255, 255, 255), font=font)
        d.text((16, y + TH - 40), f"{c['durationInFrames'] / 30:.1f} s", fill=(220, 230, 238), font=font)
        for i, im in enumerate(ims):
            sheet.paste(im, (510 + i * (TW + 8), y))
    sheet.save(D / "PLANCHE_CONTACT.jpg", quality=88)


if __name__ == "__main__":
    main()
