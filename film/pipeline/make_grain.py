"""Textures de grain argentique (4 images 2304x3968, gaussiennes, légèrement adoucies)
utilisées par la composition Remotion (remotion/public/grain/)."""
from pathlib import Path

import cv2
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "remotion/public/grain"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(11)
for i in range(4):
    n = rng.normal(0, 1, (3968, 2304)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), 0.7)
    n /= n.std()
    img = np.clip(128 + n * 40, 0, 255).astype(np.uint8)
    cv2.imwrite(str(OUT / f"grain_full{i}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
print("grain ok")
