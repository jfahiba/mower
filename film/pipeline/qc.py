"""Contrôle qualité des livrables (Phase F). Écrit deliverables/qc_report.json et
affiche un résumé. Vérifie : flux/codecs/profils/couleurs, résolution, cadence,
nombre d'images, durées A/V, loudness et true-peak, images noires, gels,
décalage audio (intercorrélation avec le mix de référence), validité du SRT.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "deliverables"
TL = json.loads((ROOT / "remotion/src/data/timeline.json").read_text())
EXPECTED_FRAMES = TL["durationInFrames"]
FPS = TL["fps"]


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def count_frames(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                        "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return int(r.stdout.strip())


def loudness(path):
    r = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(path), "-map", "0:a:0",
                        "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    get = lambda k: float(re.search(rf"{k}:\s+(-?[\d.]+)", txt).group(1))
    return {"integrated_lufs": get("I"), "lra_lu": get("LRA"), "true_peak_dbtp": get("Peak")}


def detect(path, scale="540:960"):
    r = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(path), "-map", "0:v:0",
                        "-vf", f"scale={scale},blackdetect=d=0.04:pix_th=0.05,freezedetect=n=0.001:d=0.5",
                        "-f", "null", "-"], capture_output=True, text=True)
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)
    freezes = re.findall(r"freeze_start: ([\d.]+)", r.stderr)
    fends = re.findall(r"freeze_end: ([\d.]+)", r.stderr)
    return {"black": [(float(a), float(b)) for a, b in blacks],
            "freeze": [(float(a), float(b)) for a, b in zip(freezes, fends)]}


def audio_offset_ms(path, ref_wav):
    """Décalage (ms) entre l'audio du livrable et le mix de référence (0 = synchrone)."""
    ref, sr = sf.read(ref_wav, dtype="float32", always_2d=True)
    tmp = D / "_qc_audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-map", "0:a:0", "-ac", "2", "-ar", str(sr),
                    "-c:a", "pcm_f32le", str(tmp)], check=True)
    out, _ = sf.read(tmp, dtype="float32", always_2d=True)
    tmp.unlink()
    a = ref[: sr * 20].mean(axis=1)
    b = out[: sr * 20].mean(axis=1)
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    lag = int(np.argmax(np.abs(np.concatenate([c[-sr:], c[: sr]])))) - sr
    corr = float(np.max(np.abs(c)) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    return lag / sr * 1000.0, corr


def voice_sync():
    """Décalage (ms) de la voix montée par rapport à la source WA0048, segment par segment."""
    sr = 48000
    src, _ = sf.read(ROOT / "analysis/audio/WA0048_48k.wav", dtype="float32", always_2d=True)
    src = src.mean(axis=1)
    v, _ = sf.read(ROOT / "remotion/public/audio/stems/voice.wav", dtype="float32", always_2d=True)
    v = v.mean(axis=1)
    res = []
    for sg in TL["message"]["segments"]:
        s0 = sg["srcFrom"] / FPS + 0.5
        s1 = min(sg["srcTo"] / FPS - 0.2, s0 + 8)
        if s1 - s0 < 1:
            continue
        off = (sg["tlFrom"] - sg["srcFrom"]) / FPS
        a = src[int(s0 * sr):int(s1 * sr)]
        b = v[int((s0 + off) * sr):int((s1 + off) * sr)]
        n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
        c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
        m = int(0.2 * sr)
        cc = np.concatenate([c[-m:], c[: m + 1]])
        res.append(round((int(np.argmax(np.abs(cc))) - m) / sr * 1000, 2))
    return res


def check_srt(path, duration):
    txt = path.read_text(encoding="utf-8")
    blocks = [b for b in txt.strip().split("\n\n") if b.strip()]
    def t(s):
        h, m, r = s.split(":"); sec, ms = r.split(",")
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    issues = []
    prev_end = -1
    for b in blocks:
        lines = b.split("\n")
        a, z = lines[1].split(" --> ")
        s, e = t(a), t(z)
        if e <= s:
            issues.append(f"durée nulle/négative bloc {lines[0]}")
        if s < prev_end - 1e-6:
            issues.append(f"chevauchement bloc {lines[0]}")
        if e > duration + 0.05:
            issues.append(f"au-delà de la fin bloc {lines[0]}")
        if any(len(l) > 42 for l in lines[2:]):
            issues.append(f"ligne > 42 caractères bloc {lines[0]}")
        prev_end = e
    return {"cues": len(blocks), "issues": issues, "first": blocks[0].split("\n")[1], "last": blocks[-1].split("\n")[1]}


def main():
    files = sys.argv[1:] or ["FINAL_MASTER_4K.mp4", "FINAL_WEB.mp4"]
    report = {"expected_frames": EXPECTED_FRAMES, "expected_duration_s": EXPECTED_FRAMES / FPS, "files": {}}
    ref = ROOT / "remotion/public/audio/mix.wav"
    for name in files:
        p = D / name
        info = probe(p)
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        a = next(s for s in info["streams"] if s["codec_type"] == "audio")
        frames = count_frames(p)
        loud = loudness(p)
        det = detect(p)
        off, corr = audio_offset_ms(p, ref)
        rec = {
            "size_mb": round(int(info["format"]["size"]) / 1e6, 1),
            "duration_s": round(float(info["format"]["duration"]), 3),
            "bitrate_mbps": round(int(info["format"]["bit_rate"]) / 1e6, 2),
            "video": {
                "codec": v["codec_name"], "profile": v.get("profile"), "tag": v.get("codec_tag_string"),
                "width": v["width"], "height": v["height"], "pix_fmt": v["pix_fmt"],
                "fps": v["r_frame_rate"], "frames": frames,
                "color": [v.get("color_primaries"), v.get("color_transfer"), v.get("color_space"), v.get("color_range")],
                "start": float(v.get("start_time", 0)), "duration": float(v.get("duration", 0)),
            },
            "audio": {
                "codec": a["codec_name"], "profile": a.get("profile"), "sample_rate": int(a["sample_rate"]),
                "channels": a["channels"], "bitrate_kbps": round(int(a.get("bit_rate", 0)) / 1000),
                "start": float(a.get("start_time", 0)), "duration": float(a.get("duration", 0)),
            },
            "loudness": loud,
            "black_segments": det["black"],
            "freeze_segments": det["freeze"],
            "audio_offset_ms": round(off, 2),
            "audio_ref_correlation": round(corr, 3),
        }
        checks = {
            "frames_ok": frames == EXPECTED_FRAMES,
            "fps_ok": v["r_frame_rate"] == f"{FPS}/1",
            "aspect_9_16": v["width"] * 16 == v["height"] * 9,
            "rec709_tags": rec["video"]["color"][:3] == ["bt709", "bt709", "bt709"],
            "audio_48k_stereo": rec["audio"]["sample_rate"] == 48000 and rec["audio"]["channels"] == 2,
            "loudness_ok": abs(loud["integrated_lufs"] + 14) <= 0.6 and loud["true_peak_dbtp"] <= -0.8,
            "av_duration_delta_s": round(abs(rec["video"]["duration"] - rec["audio"]["duration"]), 3),
            "no_unexpected_black": all(s < 0.5 or s > EXPECTED_FRAMES / FPS - 1.0 for s, _ in det["black"]),
            "freezes_only_on_end_card": all(s >= TL["endCard"]["tlFrom"] / FPS - 0.5 for s, _ in det["freeze"]),
            "audio_in_sync": abs(off) <= 1.0 * 1000 / FPS,  # < 1 image
        }
        rec["checks"] = checks
        report["files"][name] = rec
    report["srt"] = check_srt(D / "FINAL_SUBTITLES.srt", EXPECTED_FRAMES / FPS)
    report["voice_sync_ms"] = voice_sync()
    (D / "qc_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    for name, rec in report["files"].items():
        v, a, l = rec["video"], rec["audio"], rec["loudness"]
        print(f"\n== {name}  ({rec['size_mb']} Mo, {rec['bitrate_mbps']} Mb/s, {rec['duration_s']} s)")
        print(f"   vidéo : {v['codec']} {v['profile']} [{v['tag']}] {v['width']}x{v['height']} {v['pix_fmt']} {v['fps']} — {v['frames']} images — couleurs {v['color']}")
        print(f"   audio : {a['codec']} {a['profile']} {a['sample_rate']} Hz {a['channels']} canaux {a['bitrate_kbps']} kb/s")
        print(f"   loudness : {l['integrated_lufs']} LUFS, LRA {l['lra_lu']} LU, true-peak {l['true_peak_dbtp']} dBTP")
        print(f"   noir : {rec['black_segments']} | gels : {rec['freeze_segments']}")
        print(f"   décalage audio vs mix de référence : {rec['audio_offset_ms']} ms (corrélation {rec['audio_ref_correlation']})")
        for k, val in rec["checks"].items():
            print(f"   [{'OK' if (val is True or (isinstance(val, float) and val < 0.05)) else '!!'}] {k} = {val}")
    print(f"\n== Synchronisation voix / source WA0048 par segment (ms) : {report['voice_sync_ms']}")
    s = report["srt"]
    print(f"\n== SRT : {s['cues']} sous-titres, {s['first']} … {s['last']}, problèmes : {s['issues'] or 'aucun'}")


if __name__ == "__main__":
    main()
