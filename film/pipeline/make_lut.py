"""Génère le LUT 3D « look » du film (fichier .cube, 33³), Rec.709 -> Rec.709.

Look : cinématographique naturel, chaud et premium (bordeaux / or / crème),
pensé pour un portrait de peau foncée sous lumière chaude :
  - courbe tonale filmique douce : noirs légèrement relevés (mat), épaule
    progressive dans les hautes lumières (néons, murs blancs), contraste
    médian modéré ;
  - chroma : compression douce des couleurs très saturées (emballages de
    supermarché), légère désaturation cyan/bleu/vert, rouges-orangés-ors
    préservés (peau, robe, foulard) ;
  - split-toning subtil : ombres légèrement froides, hautes lumières dorées.
Travail en Oklab (perceptuel) sur des valeurs linéarisées (gamma 2.4, BT.1886).

Usage: python make_lut.py <out.cube> [size]
"""
import sys

import numpy as np


def srgb_like_to_linear(v):
    return np.clip(v, 0, 1) ** 2.4


def linear_to_srgb_like(v):
    return np.clip(v, 0, 1) ** (1 / 2.4)


# Oklab (Björn Ottosson) — matrices pour primaires sRGB/Rec.709 (identiques)
M1 = np.array(
    [
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005],
    ]
)
M2 = np.array(
    [
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660],
    ]
)
M1i = np.linalg.inv(M1)
M2i = np.linalg.inv(M2)


def lin_to_oklab(rgb):
    lms = rgb @ M1.T
    lms_ = np.cbrt(np.maximum(lms, 0))
    return lms_ @ M2.T


def oklab_to_lin(lab):
    lms_ = lab @ M2i.T
    lms = lms_ ** 3
    return lms @ M1i.T


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def tone_curve(L):
    """Courbe sur L (Oklab, 0..1). Toe relevé, S doux, épaule douce."""
    # contraste en S autour du gris moyen perceptuel (~0.55)
    pivot = 0.56
    k = 1.10
    x = L - pivot
    s = pivot + x * k / (1 + 0.55 * np.abs(x) * (k - 1) * 4)
    # toe : relève légèrement les noirs (mat) sans écraser les ombres
    toe_lift = 0.028
    s = toe_lift + s * (1 - toe_lift)
    # épaule : compresse doucement au-dessus de 0.86
    sh = 0.86
    over = np.maximum(s - sh, 0)
    s = np.where(s > sh, sh + over / (1 + over * 4.0), s)
    return np.clip(s, 0, 1)


def grade(rgb_enc):
    lin = srgb_like_to_linear(rgb_enc)
    lab = lin_to_oklab(lin)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]

    C = np.hypot(a, b)
    h = np.degrees(np.arctan2(b, a)) % 360  # Oklab hue

    # --- chroma par teinte -------------------------------------------------
    # Oklab: rouge ~ 20-30°, orange/peau ~ 45-70°, jaune ~ 100-110°,
    # vert ~ 140°, cyan ~ 195°, bleu ~ 265°, magenta ~ 330°.
    def bump(center, width):
        d = np.abs(((h - center + 180) % 360) - 180)
        return np.clip(1 - d / width, 0, 1) ** 2

    sat = np.ones_like(C)
    sat *= 1 - 0.16 * bump(195, 55)  # cyans (frigos, emballages)
    sat *= 1 - 0.10 * bump(265, 50)  # bleus
    sat *= 1 - 0.14 * bump(145, 45)  # verts
    sat *= 1 + 0.04 * bump(40, 35)  # rouges-orangés (robe bordeaux)
    sat *= 1 + 0.02 * bump(75, 30)  # ors / peau (très léger)

    # compression douce des chromas extrêmes (évite l'aspect « néon »)
    Cn = C * sat
    knee = 0.13
    Cc = np.where(Cn > knee, knee + (Cn - knee) / (1 + (Cn - knee) * 6.0), Cn)

    # légère rotation des magentas/roses vers le rouge chaud (peau plus naturelle)
    rot = 4.0 * bump(350, 30)
    h2 = np.radians(h - rot)

    a2 = Cc * np.cos(h2)
    b2 = Cc * np.sin(h2)

    # --- tonalité -----------------------------------------------------------
    L2 = tone_curve(L)

    # --- split-toning subtil -----------------------------------------------
    shadows = 1 - smoothstep(0.15, 0.50, L2)
    highs = smoothstep(0.60, 0.97, L2)
    # le split-toning ne s'applique qu'aux zones peu saturées (protège la peau)
    neutral = 1 - smoothstep(0.015, 0.06, Cc)
    # ombres : à peine froides ; hautes lumières : légèrement dorées
    a2 = a2 - 0.002 * shadows * neutral + 0.0015 * highs
    b2 = b2 - 0.004 * shadows * neutral + 0.0075 * highs

    out = oklab_to_lin(np.stack([L2, a2, b2], axis=-1))
    return linear_to_srgb_like(out)


def main():
    out = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 33
    g = np.linspace(0, 1, n)
    # ordre .cube : R varie le plus vite
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")
    rgb = np.stack([r, gg, b], axis=-1).reshape(-1, 3)
    res = np.clip(grade(rgb), 0, 1)
    with open(out, "w") as f:
        f.write('TITLE "Film look - premium warm natural (Rec.709)"\n')
        f.write(f"LUT_3D_SIZE {n}\n")
        f.write("DOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n")
        for v in res:
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
    # contrôle : gris neutres
    for v in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
        print(v, np.round(grade(np.array([[v, v, v]]))[0], 4))


if __name__ == "__main__":
    main()
