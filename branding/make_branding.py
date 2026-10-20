#!/usr/bin/env python3
"""Generate the HoussamOS branding files in system_files/ from the source art in branding/src/.

Source files (replace any of them, then run this script again):
  src/boot-animation.mp4  boot animation, logo on a white background, loops seamlessly
  src/logo-wordmark.png   "HoussamOS" logo on a white background
  src/wallpaper.png       desktop, lock screen and login background
  src/dock-glass.jpg      glass tray used as the dock background (TRAY_* below say where it is)

Needs Python 3 with Pillow and numpy, and ffmpeg on PATH.
Usage: python branding/make_branding.py [--preview]
"""
import base64
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "branding" / "src"
OUT = ROOT / "system_files"

THEME_DIR = OUT / "usr/share/plymouth/themes/houssamos"
ASSET_DIR = OUT / "usr/share/houssamos"

BOOT_BG = 253            # background grey level of the boot video (near white)
FRAME_WIDTH = 800        # boot frames are scaled to this width to keep the initramfs small
ICON_SIZES = [16, 22, 24, 32, 36, 48, 64, 96, 128, 256, 512]
ICON_FRAME_TIME = 4.0    # seconds into the boot video where it shows "HOS"
SOUND_START, SOUND_LENGTH, SOUND_FADE = 1.45, 2.4, 0.4   # startup sound cut from the video's audio


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def cut_out(img, low=8, high=20):
    """Cut the glass letters out of the white background as solid shapes.

    The letters differ from the background by 50-200 grey levels, the background by under 8, so
    pixels below `low` become transparent and above `high` fully opaque, with a soft edge between.
    Edge pixels are un-blended from white so they show no light fringe on dark backgrounds.
    (Simply turning white into transparency would make the light glass vanish on dark panels.)
    """
    a = np.asarray(img.convert("RGB")).astype(np.float64)
    dist = (255 - a).max(axis=2)
    alpha = np.clip((dist - low) / (high - low), 0, 1)
    safe = np.where(alpha > 0, alpha, 1)[..., None]
    edge = (alpha < 1)[..., None]
    rgb = np.where(edge, np.clip((a - 255 * (1 - alpha[..., None])) / safe, 0, 255), a)
    return Image.fromarray(np.dstack([rgb, alpha * 255]).round().astype(np.uint8), "RGBA")


def letters(img):
    """Split a cut-out word into its letters, using the empty columns between them."""
    filled, _ = solid(img)
    spans, start = [], None
    for x, f in enumerate(filled):
        if f and start is None:
            start = x
        elif not f and start is not None:
            spans.append((start, x))
            start = None
    if start is not None:
        spans.append((start, len(filled)))
    spans = [(x0, x1) for x0, x1 in spans if x1 - x0 >= img.width * 0.05]   # drop leftover specks
    return [crop_to_content(img.crop((x0, 0, x1, img.height))) for x0, x1 in spans]


def solid(img, min_pixels=4):
    """Per column and per row: does it hold real content? Rows/columns with only a few stray
    pixels (video noise near the frame edges) do not count."""
    mask = np.asarray(img.getchannel("A")) > 12
    return mask.sum(axis=0) >= min_pixels, mask.sum(axis=1) >= min_pixels


def crop_to_content(img, pad=0):
    cols, rows = solid(img)
    xs, ys = np.flatnonzero(cols), np.flatnonzero(rows)
    x0, x1, y0, y1 = xs[0], xs[-1] + 1, ys[0], ys[-1] + 1
    return img.crop((max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, img.width), min(y1 + pad, img.height)))


def square(img, margin=0.06):
    side = round(max(img.size) * (1 + 2 * margin))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
    return canvas


def video_frames(video, tmp):
    run("ffmpeg", "-v", "error", "-i", str(video), str(tmp / "f%04d.png"))
    rate = run("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
               "-of", "default=nw=1:nk=1", str(video)).strip()
    num, den = rate.split("/")
    return sorted(tmp.glob("f*.png")), round(int(num) / int(den))


def boot_animation(video):
    """Plymouth frames: crop to the area the logo moves in, scale, reduce to 256 colours."""
    with tempfile.TemporaryDirectory() as t:
        files, fps = video_frames(video, Path(t))
        lo, hi = [10**9, 10**9], [0, 0]
        for f in files:
            a = np.asarray(Image.open(f).convert("RGB")).astype(int)
            ys, xs = np.where(np.abs(a - BOOT_BG).max(axis=2) > 12)
            if len(xs):
                lo = [min(lo[0], xs.min()), min(lo[1], ys.min())]
                hi = [max(hi[0], xs.max()), max(hi[1], ys.max())]
        w0, h0 = Image.open(files[0]).size
        box = (max(lo[0] - 16, 0), max(lo[1] - 16, 0), min(hi[0] + 16, w0), min(hi[1] + 16, h0))

        for old in THEME_DIR.glob("frame-*.png"):
            old.unlink()
        THEME_DIR.mkdir(parents=True, exist_ok=True)
        for i, f in enumerate(files, 1):
            im = Image.open(f).convert("RGB").crop(box)
            im = im.resize((FRAME_WIDTH, round(im.height * FRAME_WIDTH / im.width)), Image.LANCZOS)
            a = np.asarray(im).astype(int)
            a[np.abs(a - BOOT_BG).max(axis=2) <= 4] = BOOT_BG   # flatten background noise
            Image.fromarray(a.astype(np.uint8)).quantize(colors=256, dither=Image.Dither.FLOYDSTEINBERG) \
                .save(THEME_DIR / f"frame-{i}.png", optimize=True)
        frame_height = round((box[3] - box[1]) * FRAME_WIDTH / (box[2] - box[0]))

    script = (ROOT / "branding" / "houssamos.script.in").read_text()
    script = script.replace("@FRAME_COUNT@", str(len(files))).replace("@FPS@", str(fps)) \
                   .replace("@BG@", f"{BOOT_BG / 255:.3f}")
    (THEME_DIR / "houssamos.script").write_text(script, newline="\n")
    (THEME_DIR / "houssamos.plymouth").write_text(
        "[Plymouth Theme]\n"
        "Name=HoussamOS\n"
        "Description=HoussamOS boot animation\n"
        "ModuleName=script\n\n"
        "[script]\n"
        "ImageDir=/usr/share/plymouth/themes/houssamos\n"
        "ScriptFile=/usr/share/plymouth/themes/houssamos/houssamos.script\n", newline="\n")
    size = sum(p.stat().st_size for p in THEME_DIR.glob("frame-*.png"))
    print(f"boot animation: {len(files)} frames, {fps} fps, {FRAME_WIDTH}x{frame_height}, {size / 1e6:.1f} MB")


def icons(video):
    """Icons taken from the "HOS" moment of the boot animation, in every size icon themes use.

    "HOS" is too wide to read below 64 px, so small sizes (and the scalable icon used for the
    app menu button) show just the "H".
    """
    with tempfile.TemporaryDirectory() as t:
        frame = Path(t) / "hos.png"
        run("ffmpeg", "-v", "error", "-ss", str(ICON_FRAME_TIME), "-i", str(video), "-frames:v", "1", str(frame))
        word = crop_to_content(cut_out(Image.open(frame)))
    hos, h = square(word), square(letters(word)[0], margin=0.1)
    out = ASSET_DIR / "icons"
    out.mkdir(parents=True, exist_ok=True)
    for s in ICON_SIZES:
        (h if s <= 48 else hos).resize((s, s), Image.LANCZOS).save(out / f"{s}.png", optimize=True)
    buf = io.BytesIO()
    h.resize((256, 256), Image.LANCZOS).save(buf, "PNG", optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    (out / "houssamos-logo.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="256" height="256" viewBox="0 0 256 256">'
        f'<image width="256" height="256" xlink:href="data:image/png;base64,{data}"/></svg>\n', newline="\n")
    pix = OUT / "usr/share/pixmaps"
    pix.mkdir(parents=True, exist_ok=True)
    hos.resize((256, 256), Image.LANCZOS).save(pix / "houssamos-logo.png", optimize=True)
    print(f"icons: {len(ICON_SIZES)} sizes + svg")
    return h, hos


def wordmark(path):
    logo = crop_to_content(cut_out(Image.open(path)), pad=8)
    if logo.width > 1200:
        logo = logo.resize((1200, round(logo.height * 1200 / logo.width)), Image.LANCZOS)
    logo.save(OUT / "usr/share/pixmaps/houssamos-wordmark.png", optimize=True)
    print(f"wordmark: {logo.width}x{logo.height}")
    return logo


def wallpaper(path):
    img = Image.open(path)
    pkg = OUT / "usr/share/wallpapers/HoussamOS"
    if pkg.exists():
        shutil.rmtree(pkg)
    (pkg / "contents/images").mkdir(parents=True)
    shutil.copy(path, pkg / f"contents/images/{img.width}x{img.height}{path.suffix}")
    (pkg / "metadata.json").write_text(json.dumps({
        "KPlugin": {"Authors": [{"Name": "Houssam"}], "Id": "HoussamOS", "Name": "HoussamOS", "License": "CC-BY-SA-4.0"}
    }, indent=4) + "\n", newline="\n")
    print(f"wallpaper: {img.width}x{img.height}")


THEME_ID = "houssamos-glass"
DOCK_HEIGHT = 84                       # logical px; must match the layout script
# Where things are in src/dock-glass.jpg (source pixels)
TRAY_CROP = (213, 270, 1188, 580)      # tray plus its shadow
TRAY_BODY = (233, 282, 1168, 530)      # the glass itself (blur goes behind this)
TRAY_ROWS = (340, 455)                 # top rim ends / front wall starts: the floor between stretches
TRAY_CAP = 120                         # width of each rounded end, kept unstretched


def glass_layer(path):
    """Turn a photo of glass on a light background into a layer that works on any wallpaper.

    Each pixel is compared with the background around it: darker means glass shading (kept as
    black with alpha), lighter means a highlight (white with alpha). The background is estimated
    per row from the photo's left and right edges, since it is a soft gradient, not pure white.
    """
    a = np.asarray(Image.open(path).convert("L")).astype(np.float64)
    h, w = a.shape
    left, right = np.median(a[:, :120], axis=1), np.median(a[:, -120:], axis=1)
    bg = left[:, None] + (right - left)[:, None] * np.arange(w)[None, :] / (w - 1)
    d = a - bg
    d[np.abs(d) < 3] = 0
    dark = np.clip(-d / np.maximum(bg, 1) * 1.8, 0, 1)
    light = np.clip(d / np.maximum(255 - bg, 12), 0, 1)
    alpha = np.maximum(dark, light)
    rgb = np.where((light > dark)[..., None], 255.0, 0.0) * np.ones(3)

    # Fade out everything away from the tray so background-estimate errors leave no box
    keep = Image.new("L", (w, h), 0)
    x0, y0, x1, y1 = TRAY_BODY
    ImageDraw.Draw(keep).rounded_rectangle((x0 - 6, y0 - 6, x1 + 6, TRAY_CROP[3] - 4), radius=56, fill=255)
    keep = np.asarray(keep.filter(ImageFilter.GaussianBlur(6))) / 255.0
    layer = Image.fromarray(np.dstack([rgb, alpha * keep * 255]).round().astype(np.uint8), "RGBA")

    body = Image.new("L", (w, h), 0)
    ImageDraw.Draw(body).rounded_rectangle(TRAY_BODY, radius=50, fill=255)
    return layer.crop(TRAY_CROP), Image.merge("RGBA", [body] * 4).crop(TRAY_CROP)


def nine_slice(img, scale):
    """Cut into the 9 frame pieces Plasma stretches. Returns {name: (image, logical w, logical h)}."""
    cw, ch = img.size
    cap, top, bottom = TRAY_CAP, TRAY_ROWS[0] - TRAY_CROP[1], TRAY_ROWS[1] - TRAY_CROP[1]
    xs = [0, cap, cw - cap, cw]
    ys = [0, top, bottom, ch]
    logical_w = [round(cap * scale), 100, round(cap * scale)]
    rows = [round(top * scale), 0, round((ch - bottom) * scale)]
    rows[1] = DOCK_HEIGHT - rows[0] - rows[2]
    names = [["topleft", "top", "topright"], ["left", "center", "right"], ["bottomleft", "bottom", "bottomright"]]
    pieces = {}
    for r in range(3):
        for c in range(3):
            piece = img.crop((xs[c], ys[r], xs[c + 1], ys[r + 1]))
            lw, lh = logical_w[c], rows[r]
            pieces[names[r][c]] = (piece.resize((lw * 2, lh * 2), Image.LANCZOS), lw, lh)   # 2x for HiDPI
    return pieces


def glass_theme(path):
    """Plasma desktop theme: glass tray dock (bottom panel) and a frosted top bar.

    Only the panel background is ours; every other element falls back to Breeze.
    """
    tray, body = glass_layer(path)
    scale = DOCK_HEIGHT / tray.height
    parts = []

    def image(name, img, x, y, w, h):
        buf = io.BytesIO()
        img.save(buf, "PNG", optimize=True)
        data = base64.b64encode(buf.getvalue()).decode()
        parts.append(f'<image id="{name}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none" '
                     f'xlink:href="data:image/png;base64,{data}"/>')

    def rect(name, x, y, w, h, fill="#000000", opacity=0.0):
        parts.append(f'<rect id="{name}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
                     f'fill-opacity="{opacity}"/>')

    # Elements sit on a grid of 150x120 cells; only their own sizes matter to Plasma.
    def cell(col, row):
        return col * 150, row * 120

    # Dock: unprefixed elements, so any panel without its own prefix (the bottom one) uses them.
    # mask-* is the area KWin blurs behind the panel: the glass body only.
    for prefix, src, first_row in (("", tray, 0), ("mask-", body, 3)):
        for i, (name, (img, w, h)) in enumerate(nine_slice(src, scale).items()):
            image(prefix + name, img, *cell(i % 3, first_row + i // 3), w, h)
    # Content margins (icon area inside the glass) and stretching instead of tiling
    hints = [("hint-stretch-borders", 1, 1), ("hint-top-margin", 1, 14), ("hint-bottom-margin", 1, 22),
             ("hint-left-margin", 24, 1), ("hint-right-margin", 24, 1)]
    for i, (name, w, h) in enumerate(hints):
        rect(name, *cell(i, 6), w, h)

    # Top bar: "north-" elements, a white frosted strip with a faint line underneath
    strip = [("topleft", 1, 1, 0), ("top", 10, 1, 0), ("topright", 1, 1, 0),
             ("left", 1, 10, 0.55), ("center", 10, 10, 0.55), ("right", 1, 10, 0.55),
             ("bottomleft", 1, 1, 0.08), ("bottom", 10, 1, 0.08), ("bottomright", 1, 1, 0.08)]
    for i, (name, w, h, opacity) in enumerate(strip):
        fill = "#ffffff" if 3 <= i < 6 else "#000000"
        rect(f"north-{name}", *cell(i % 3, 7 + i // 3), w, h, fill, opacity)
    hints = [("north-hint-stretch-borders", 1, 1), ("north-hint-top-margin", 1, 2),
             ("north-hint-bottom-margin", 1, 2), ("north-hint-left-margin", 6, 1), ("north-hint-right-margin", 6, 1)]
    for i, (name, w, h) in enumerate(hints):
        rect(name, *cell(i, 10), w, h)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           'width="750" height="1320" viewBox="0 0 750 1320">\n' + "\n".join(parts) + "\n</svg>\n")
    theme = OUT / f"usr/share/plasma/desktoptheme/{THEME_ID}"
    if theme.exists():
        shutil.rmtree(theme)
    for sub in ("widgets", "translucent/widgets"):     # translucent/ is what Plasma uses with compositing
        (theme / sub).mkdir(parents=True)
        (theme / sub / "panel-background.svg").write_text(svg, newline="\n")
    (theme / "metadata.json").write_text(json.dumps({
        "KPlugin": {"Id": THEME_ID, "Name": "HoussamOS Glass", "Description": "Glass dock and frosted top bar",
                    "Authors": [{"Name": "Houssam"}], "License": "CC-BY-SA-4.0", "Version": "1.0",
                    "Website": "https://github.com/Houssam-2021/housos"},
        "X-Plasma-API-Minimum-Version": "6.0"
    }, indent=4) + "\n", newline="\n")
    (theme / "plasmarc").write_text(
        "[BlurBehindEffect]\nenabled=true\n\n"
        "[ContrastEffect]\nenabled=false\n\n"
        "[AdaptiveTransparency]\nenabled=false\n", newline="\n")
    shutil.copy(ROOT / "branding" / "colors", theme / "colors")
    print(f"glass theme: dock {DOCK_HEIGHT}px tall, {sum(len(p) for p in parts) / 1e3:.0f} KB svg")
    return tray, scale


def dock_preview(tray, scale):
    """The dock stretched for 5 and 9 apps over the wallpaper (placeholder squares for icons)."""
    wp = Image.open(SRC / "wallpaper.png").convert("RGBA").resize((1920, 1080), Image.LANCZOS)
    pieces = nine_slice(tray, scale)
    rows = []
    for n in (5, 9):
        width = n * 52 + (n - 1) * 8 + 2 * 24
        dock = Image.new("RGBA", (width, DOCK_HEIGHT), (0, 0, 0, 0))
        y = 0
        for row in (("topleft", "top", "topright"), ("left", "center", "right"),
                    ("bottomleft", "bottom", "bottomright")):
            lw = pieces[row[0]][1]
            h = pieces[row[0]][2]
            dock.alpha_composite(pieces[row[0]][0].resize((lw, h), Image.LANCZOS), (0, y))
            dock.alpha_composite(pieces[row[1]][0].resize((width - 2 * lw, h), Image.LANCZOS), (lw, y))
            dock.alpha_composite(pieces[row[2]][0].resize((lw, h), Image.LANCZOS), (width - lw, y))
            y += h
        scene = wp.copy()
        dx, dy = (1920 - width) // 2, 1080 - DOCK_HEIGHT - 8
        scene.alpha_composite(dock, (dx, dy))
        draw = ImageDraw.Draw(scene)
        for i in range(n):
            x = dx + 24 + i * 60
            draw.rounded_rectangle((x, dy + 14, x + 52, dy + 66), radius=12, fill=(60 + 20 * i, 140, 230 - 15 * i))
        rows.append(scene.crop((0, 1080 - 200, 1920, 1080)))
    sheet = Image.new("RGBA", (1920, 400))
    sheet.paste(rows[0], (0, 0))
    sheet.paste(rows[1], (0, 200))
    sheet.convert("RGB").save(ROOT / "branding" / "preview-dock.jpg", quality=90)
    print("preview: branding/preview-dock.jpg")


def installer_art(wallpaper_path, logo):
    """Pictures for the installer (Anaconda), swapped into the ISO by build-disk.yml.

    sidebar-bg: tall strip of the wallpaper's glass wave behind the left sidebar
    sidebar-logo: the HoussamOS logo at the top of the sidebar
    topbar-bg: wide strip used instead of the sidebar on small screens
    """
    out = ROOT / "disk_config" / "installer"
    out.mkdir(parents=True, exist_ok=True)
    wp = Image.open(wallpaper_path).convert("RGB")
    tall = wp.resize((round(wp.width * 2160 / wp.height), 2160), Image.LANCZOS)
    center = round(tall.width * 0.82)          # the glass wave sits on the right of the wallpaper
    tall.crop((center - 200, 0, center + 200, 2160)).save(out / "sidebar-bg.png", optimize=True)
    wide = wp.resize((1920, round(wp.height * 1920 / wp.width)), Image.LANCZOS)
    wide.crop((0, 0, 1920, 64)).save(out / "topbar-bg.png", optimize=True)
    logo.resize((170, round(logo.height * 170 / logo.width)), Image.LANCZOS).save(out / "sidebar-logo.png", optimize=True)
    print("installer art: sidebar-bg, sidebar-logo, topbar-bg")


def startup_sound(video):
    out = OUT / "usr/share/sounds/houssamos"
    out.mkdir(parents=True, exist_ok=True)
    fade_at = SOUND_LENGTH - SOUND_FADE
    run("ffmpeg", "-v", "error", "-y", "-ss", str(SOUND_START), "-t", str(SOUND_LENGTH), "-i", str(video), "-vn",
        "-af", f"afade=t=in:d=0.05,afade=t=out:st={fade_at}:d={SOUND_FADE}", "-c:a", "libvorbis", "-q:a", "5",
        str(out / "startup.oga"))
    print("startup sound: startup.oga")


def preview(icons, logo):
    """Icons and logo on light and dark backgrounds, to check they stay readable."""
    h, hos = icons
    sheet = Image.new("RGBA", (1100, 520), (0, 0, 0, 0))
    for col, bg in enumerate([(240, 240, 240, 255), (30, 30, 34, 255)]):
        panel = Image.new("RGBA", (550, 520), bg)
        x = 20
        for s in (16, 24, 32, 48, 96, 128):
            i = (h if s <= 48 else hos).resize((s, s), Image.LANCZOS)
            panel.alpha_composite(i, (x, 20 + (128 - s) // 2))
            x += s + 20
        lw = logo.resize((510, round(logo.height * 510 / logo.width)), Image.LANCZOS)
        panel.alpha_composite(lw, (20, 200))
        sheet.paste(panel, (col * 550, 0))
    path = ROOT / "branding" / "preview.png"
    sheet.save(path)
    print(f"preview: {path}")


if __name__ == "__main__":
    boot_animation(SRC / "boot-animation.mp4")
    icon_set = icons(SRC / "boot-animation.mp4")
    logo = wordmark(SRC / "logo-wordmark.png")
    wallpaper(SRC / "wallpaper.png")
    installer_art(SRC / "wallpaper.png", logo)
    startup_sound(SRC / "boot-animation.mp4")
    tray, tray_scale = glass_theme(SRC / "dock-glass.jpg")
    if "--preview" in sys.argv:
        preview(icon_set, logo)
        dock_preview(tray, tray_scale)
