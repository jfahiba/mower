"""Paramètres d'étalonnage par source et construction des chaînes de filtres FFmpeg.

Mesures (analysis/wb) sur surfaces neutres (sol, murs) :
  WA0042 sol  R/G 1.050 B/G 0.920     WA0049 murs R/G 1.045 B/G 0.939
  WA0044 sol  R/G 1.053 B/G 0.968     WA0048 mur  R/G 1.112 B/G 0.935
  WA0045 sol  R/G 1.049 B/G 0.944
  WA0047 sol  R/G 1.042 B/G 0.913
Cible commune « blanc chaud » R/G 1.05, B/G 0.935 ; WA0048 est aligné sur le mur
du même bureau vu dans WA0049 (R/G 1.07) pour un raccord invisible.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LUT = ROOT / "grade" / "film_look.cube"

TARGET_RG = 1.05
TARGET_BG = 0.935

MEASURED = {
    "WA0042": (1.050, 0.920),
    "WA0044": (1.053, 0.968),
    "WA0045": (1.049, 0.944),
    "WA0047": (1.042, 0.913),
    "WA0049": (1.045, 0.939),
    "WA0048": (1.112, 0.935),
}

# réglages fins par source : exposition (gain linéaire approx.), saturation, gamma
TWEAKS = {
    "WA0042": dict(exposure=1.00, sat=0.97, gamma=1.00, target_rg=TARGET_RG),
    "WA0044": dict(exposure=1.03, sat=0.97, gamma=1.00, target_rg=TARGET_RG),
    "WA0045": dict(exposure=1.02, sat=0.97, gamma=1.00, target_rg=TARGET_RG),
    "WA0047": dict(exposure=0.99, sat=0.97, gamma=1.00, target_rg=TARGET_RG),
    "WA0049": dict(exposure=1.02, sat=1.00, gamma=1.00, target_rg=TARGET_RG),
    # message : peau foncée — on ouvre légèrement les médiums (gamma) sans écraser
    "WA0048": dict(exposure=1.00, sat=1.00, gamma=1.04, target_rg=1.07),
}


def wb_gains(src):
    rg, bg = MEASURED[src]
    t = TWEAKS[src]
    gr = t["target_rg"] / rg
    gb = TARGET_BG / bg
    # normalise pour conserver la luminance (Rec.709)
    lum = 0.2126 * gr + 0.7152 * 1.0 + 0.0722 * gb
    e = t["exposure"] / lum
    return gr * e, 1.0 * e, gb * e


def grade_chain(src, upscale=None, sharpen=0.0, denoise=True):
    """Chaîne de filtres : YUV709 -> RGB float -> balance -> LUT -> (upscale) -> YUV709."""
    gr, gg, gb = wb_gains(src)
    t = TWEAKS[src]
    f = []
    if denoise:
        # débruitage léger spatial+temporel (artefacts de compression WhatsApp)
        f.append("hqdn3d=luma_spatial=1.2:chroma_spatial=1.6:luma_tmp=2.5:chroma_tmp=3.0")
    if abs(t["gamma"] - 1.0) > 1e-3 or abs(t["sat"] - 1.0) > 1e-3:
        # gamma/saturation appliqués dans le domaine YUV (filtre eq)
        f.append(f"eq=gamma={t['gamma']:.3f}:saturation={t['sat']:.3f}:eval=init")
    f.append("zscale=rangein=tv:matrixin=709:transferin=709:primariesin=709:range=full:matrix=709")
    f.append("format=gbrpf32le")
    f.append(f"colorchannelmixer=rr={gr:.4f}:gg={gg:.4f}:bb={gb:.4f}")
    f.append(f"lut3d=file='{LUT}':interp=tetrahedral")
    if upscale:
        w, h = upscale
        f.append(f"zscale=w={w}:h={h}:filter=spline36")
    f.append("format=gbrp16le")
    if sharpen > 0:
        f.append(f"cas=strength={sharpen:.2f}")
    f.append("zscale=rangein=full:range=tv:matrixin=709:matrix=709:transfer=709:primaries=709")
    f.append("format=yuv420p")
    return ",".join(f)


if __name__ == "__main__":
    for s in MEASURED:
        print(s, [round(x, 4) for x in wb_gains(s)])
        print("   ", grade_chain(s, upscale=(2160, 3840), sharpen=0.5))
