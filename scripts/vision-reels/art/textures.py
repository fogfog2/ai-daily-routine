"""Generate original synthetic education textures. No patient or benchmark imagery."""

from pathlib import Path
from PIL import Image
import numpy as np

out = Path(__file__).resolve().parent
rng = np.random.default_rng(31)
y, x = np.mgrid[-1:1:500j, -1.45:1.45:740j]
theta = np.arctan2(y + 0.07, x - 0.12)
r = np.sqrt(((x - 0.12) * 0.92) ** 2 + ((y + 0.07) * 1.06) ** 2)
z = r + 0.09 * np.sin(3 * theta + 0.7) + 0.035 * np.sin(5 * theta + r * 4)
rim = np.exp(-(((z - 0.70) / 0.13) ** 2)) + 0.62 * np.exp(-(((z - 1.08) / 0.095) ** 2))
base = (1 - np.exp(-2.8 * r * r)) + 0.33 * rim
grain = rng.normal(0, 0.012, x.shape) + 0.035 * np.sin(36 * r + 5 * np.sin(theta * 2))
veins = np.exp(-18 * np.abs(np.sin(9 * theta + 2 * np.sin(r * 3) + r * 4)))
light = np.clip(0.8 + 0.22 * x - 0.17 * y, 0, 1.3)
channels = [
    (22 + 146 * base + 25 * grain - 17 * veins) * light,
    (14 + 70 * base + 24 * grain - 15 * veins) * light,
    (21 + 64 * base + 28 * grain - 11 * veins) * light,
]
img = Image.fromarray(np.clip(np.stack(channels, axis=-1), 0, 255).astype("uint8"))
img.save(out / "lumen.jpg", quality=92)
