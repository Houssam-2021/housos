#!/usr/bin/env python3
"""Generate the HoussamOS "Aurora" wallpapers (dark and light) procedurally.

Layered waves like folded silk or glass: each layer is the area under a flowing curve, with a
soft edge, a thin rim of light along its top and gentle shading below, so it has depth. Back
layers glow, front layers are deep, which keeps the bottom of the screen calm behind the dock.
Fine grain hides banding. Everything is seeded, so every run gives the same images.

Usage: python branding/make_wallpapers.py [width height] [out_dir]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# Each layer: (height of its edge 0..1, wave amplitude, waves across, phase,
#              colour on the left, colour on the right, rim light strength)
PALETTES = {
    "dark": {
        "sky_top": (6, 8, 20), "sky_glow": (52, 46, 140), "glow_at": 0.42,
        "layers": [
            (0.36, 0.060, 0.80, 0.4, (70, 90, 230), (150, 95, 255), 0.55),
            (0.47, 0.075, 0.65, 2.1, (40, 70, 200), (110, 70, 235), 0.60),
            (0.58, 0.060, 1.05, 3.6, (24, 48, 150), (70, 50, 180), 0.55),
            (0.69, 0.055, 0.75, 1.2, (14, 28, 92), (40, 30, 120), 0.30),
            (0.81, 0.040, 1.30, 4.4, (8, 14, 46), (20, 16, 64), 0.20),
        ],
        "rim": (190, 215, 255), "shade": 0.45, "grain": 1.3,
    },
    "light": {
        "sky_top": (232, 238, 252), "sky_glow": (250, 244, 255), "glow_at": 0.42,
        "layers": [
            (0.36, 0.060, 0.80, 0.4, (196, 208, 255), (222, 204, 255), 0.70),
            (0.47, 0.075, 0.65, 2.1, (176, 196, 255), (206, 186, 255), 0.75),
            (0.58, 0.060, 1.05, 3.6, (198, 214, 255), (220, 206, 255), 0.70),
            (0.69, 0.055, 0.75, 1.2, (222, 230, 255), (234, 226, 255), 0.65),
            (0.81, 0.040, 1.30, 4.4, (240, 244, 255), (246, 242, 255), 0.55),
        ],
        "rim": (255, 255, 255), "shade": 0.10, "grain": 0.9,
    },
}


def render(name, width, height, seed=7):
    p = PALETTES[name]
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:height, 0:width].astype(np.float64)
    u, v = x / width, y / height
    px = 1.0 / height                                   # one pixel, in v units

    # Sky: dark at the top, glowing towards the horizon behind the waves
    glow = np.exp(-((v - p["glow_at"]) / 0.32) ** 2) * (0.6 + 0.4 * np.exp(-((u - 0.62) / 0.45) ** 2))
    img = np.array(p["sky_top"]) * (1 - glow[..., None]) + np.array(p["sky_glow"]) * glow[..., None]

    for i, (edge, amp, waves, phase, left, right, rim_strength) in enumerate(p["layers"]):
        curve = (edge + amp * np.sin(2 * np.pi * waves * u + phase)
                 + amp * 0.35 * np.sin(2 * np.pi * waves * 2.3 * u + phase * 1.7 + i))
        depth = v - curve                                # > 0 inside the layer
        inside = 1 / (1 + np.exp(np.clip(-depth / (1.2 * px), -60, 60)))   # soft, anti-aliased edge
        colour = np.array(left) * (1 - u[..., None]) + np.array(right) * u[..., None]
        shade = 1 - p["shade"] * (1 - np.exp(-np.clip(depth, 0, None) / 0.16))
        layer = colour * shade[..., None]
        rim = np.exp(-(np.clip(depth, 0, None) / (2.5 * px)) ** 2) * inside
        sheen = np.exp(-(np.clip(depth, 0, None) / 0.035) ** 2) * inside * 0.6 * rim_strength
        rim_colour = np.array(p["rim"]) * 0.65 + colour * 0.35        # rim light tinted by the layer
        layer = layer + (rim_colour - layer) * (rim * rim_strength + sheen)[..., None]
        img = img * (1 - inside[..., None]) + layer * inside[..., None]

    img += rng.normal(0, p["grain"], img.shape)          # grain hides banding in the gradients
    return Image.fromarray(np.clip(img, 0, 255).round().astype(np.uint8), "RGB")


def main():
    width, height = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) >= 3 else (3840, 2160)
    out = Path(sys.argv[3]) if len(sys.argv) >= 4 else ROOT / "branding" / "src"
    out.mkdir(parents=True, exist_ok=True)
    for name in PALETTES:
        path = out / f"wallpaper-{name}.jpg"
        render(name, width, height).save(path, quality=94, subsampling=0)
        print(f"{path.name}: {width}x{height}")


if __name__ == "__main__":
    main()
