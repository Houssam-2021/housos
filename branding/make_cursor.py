#!/usr/bin/env python3
"""Generate the HoussamOS cursor theme from Houssam's arrow (branding/src/cursor.png).

Only the arrow is drawn here; the other cursors (hand, text, busy, resize) come from
Bibata-Modern-Classic, which the theme inherits. The arrow gets a soft shadow so it stays
visible on light backgrounds. Output is Xcursor files, the format KDE and GTK read, at the
usual sizes; build_files/build.sh links the arrow's other names (left_ptr, arrow) to it.
Usage: python branding/make_cursor.py
"""
import struct
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "branding/src/cursor.png"
OUT = ROOT / "system_files/usr/share/icons/HoussamOS-Cursor"
SIZES = (24, 32, 36, 48, 64, 72, 96)
ARROW_HEIGHT = 0.82       # share of the cursor size the arrow fills
SHADOW = (0.035, 0.05, 0.30)  # blur and drop as shares of the size, and opacity

XCURSOR_IMAGE = 0xFFFD0002


def tip(arrow):
    """The arrow's point: the left end of its first solid row."""
    alpha = arrow.getchannel("A")
    w, h = arrow.size
    for y in range(h):
        for x in range(w):
            if alpha.getpixel((x, y)) > 128:
                return x, y
    raise ValueError("cursor image is empty")


def frame(arrow, size):
    """The arrow drawn on a size x size canvas, with its hotspot."""
    scale = size * ARROW_HEIGHT / arrow.height
    small = arrow.resize((max(1, round(arrow.width * scale)), round(arrow.height * scale)), Image.LANCZOS)
    offset = (max(1, round(size * 0.06)), max(1, round(size * 0.04)))
    blur, drop, opacity = SHADOW
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shade = Image.new("RGBA", small.size, (0, 0, 0, 255))
    shade.putalpha(small.getchannel("A").point(lambda a: int(a * opacity)))
    shadow.paste(shade, (offset[0], offset[1] + round(size * drop)), shade)
    canvas = shadow.filter(ImageFilter.GaussianBlur(size * blur))
    canvas.alpha_composite(small, offset)
    tx, ty = tip(arrow)
    return canvas, (offset[0] + round(tx * scale), offset[1] + round(ty * scale))


def xcursor(frames):
    """Xcursor file bytes: header, table of contents, then one image chunk per size."""
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, len(frames))
    toc, chunks = [], []
    position = 16 + 12 * len(frames)
    for size, (image, (xhot, yhot)) in frames:
        pixels = bytearray()
        raw = image.tobytes()
        for i in range(0, len(raw), 4):
            r, g, b, a = raw[i:i + 4]
            # premultiplied ARGB, little-endian
            pixels += struct.pack("<I", (a << 24) | (r * a // 255) << 16 | (g * a // 255) << 8 | (b * a // 255))
        chunk = struct.pack("<9I", 36, XCURSOR_IMAGE, size, 1, image.width, image.height, xhot, yhot, 0) + pixels
        toc.append(struct.pack("<III", XCURSOR_IMAGE, size, position))
        chunks.append(chunk)
        position += len(chunk)
    return header + b"".join(toc) + b"".join(chunks)


def main():
    arrow = Image.open(SRC).convert("RGBA")
    arrow = arrow.crop(arrow.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox())
    (OUT / "cursors").mkdir(parents=True, exist_ok=True)
    (OUT / "cursors/default").write_bytes(xcursor([(s, frame(arrow, s)) for s in SIZES]))
    (OUT / "index.theme").write_text(
        "[Icon Theme]\nName=HoussamOS\n"
        "Comment=The HoussamOS arrow; other cursors from Bibata Modern Classic\n"
        "Inherits=Bibata-Modern-Classic\n", newline="\n")
    preview = Image.new("RGBA", (sum(SIZES) + 10 * len(SIZES), max(SIZES)), (245, 245, 250, 255))
    x = 0
    for s in SIZES:
        image, _ = frame(arrow, s)
        preview.alpha_composite(image, (x, 0))
        x += s + 10
    preview.save(ROOT / "branding/preview-cursor.png")
    print(f"cursor theme HoussamOS-Cursor: sizes {', '.join(map(str, SIZES))}")


if __name__ == "__main__":
    main()
