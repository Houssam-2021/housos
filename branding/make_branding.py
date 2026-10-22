#!/usr/bin/env python3
"""Generate the HoussamOS branding files in system_files/ from the source art in branding/src/.

Source files (replace any of them, then run this script again):
  src/boot-animation.mp4  logo animation on a white background: icons and startup sound
  src/boot-animation-purple.mp4  the same animation on dark purple: the boot screen, whose
                          background colour the login splash (Splash.qml) also uses
  src/logo-wordmark.png   "HoussamOS" logo on a white background
  src/wallpaper-*.jpg     desktop, lock and login backgrounds, made by make_wallpapers.py

The Plasma theme and colour schemes are made by make_theme.py.

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
    """Plymouth frames: crop to the area the logo moves in, scale, reduce to 256 colours.

    The background colour comes from the video's top and bottom edges. The last frame is also
    saved for the login splash, so the logo looks the same there as at the end of the boot."""
    with tempfile.TemporaryDirectory() as t:
        files, fps = video_frames(video, Path(t))
        first = np.asarray(Image.open(files[0]).convert("RGB")).astype(int)
        edges = np.concatenate([first[:8].reshape(-1, 3), first[-8:].reshape(-1, 3)])
        bg = np.median(edges, axis=0).round().astype(int)
        lo, hi = [10**9, 10**9], [0, 0]
        for f in files:
            a = np.asarray(Image.open(f).convert("RGB")).astype(int)
            ys, xs = np.where(np.abs(a - bg).max(axis=2) > 12)
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
            a[np.abs(a - bg).max(axis=2) <= 4] = bg   # flatten background noise
            Image.fromarray(a.astype(np.uint8)).quantize(colors=256, dither=Image.Dither.FLOYDSTEINBERG) \
                .save(THEME_DIR / f"frame-{i}.png", optimize=True)
        frame_height = round((box[3] - box[1]) * FRAME_WIDTH / (box[2] - box[0]))
        splash = OUT / "usr/share/plasma/look-and-feel/org.houssamos.glass.desktop/contents/splash/images"
        splash.mkdir(parents=True, exist_ok=True)
        last = Image.open(files[-1]).convert("RGB").crop(box)
        last = np.asarray(last.resize((FRAME_WIDTH, frame_height), Image.LANCZOS)).astype(int)
        last[np.abs(last - bg).max(axis=2) <= 4] = bg
        Image.fromarray(last.astype(np.uint8)).save(splash / "boot-logo.png", optimize=True)

    script = (ROOT / "branding" / "houssamos.script.in").read_text()
    script = script.replace("@FRAME_COUNT@", str(len(files))).replace("@FPS@", str(fps)) \
                   .replace("@BG@", ", ".join(f"{c / 255:.3f}" for c in bg))
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
    print(f"boot animation: {len(files)} frames, {fps} fps, {FRAME_WIDTH}x{frame_height}, {size / 1e6:.1f} MB, "
          f"background #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x} (Splash.qml uses the same colour)")


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


def wallpaper(light_path, dark_path):
    """KDE wallpaper package with a light and a dark image; Plasma picks the one matching the
    colour scheme. The images come from branding/make_wallpapers.py."""
    pkg = OUT / "usr/share/wallpapers/HoussamOS"
    if pkg.exists():
        shutil.rmtree(pkg)
    for folder, path in (("images", light_path), ("images_dark", dark_path)):
        img = Image.open(path)
        (pkg / "contents" / folder).mkdir(parents=True)
        shutil.copy(path, pkg / "contents" / folder / f"{img.width}x{img.height}{path.suffix}")
    (pkg / "metadata.json").write_text(json.dumps({
        "KPlugin": {"Authors": [{"Name": "Houssam"}], "Id": "HoussamOS", "Name": "HoussamOS Aurora", "License": "CC-BY-SA-4.0"}
    }, indent=4) + "\n", newline="\n")
    print(f"wallpaper: light + dark, {img.width}x{img.height}")


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
    installer_background(out / "houssamos-bg.jpg")
    print("installer art: sidebar-bg, sidebar-logo, topbar-bg, houssamos-bg")


def installer_background(path, size=(1920, 1080), seed=7):
    """The installer's backdrop (houssamos.css draws the glass panel over it): the boot purple
    lit up in violet, a soft streak of light, and out-of-focus circles of light (bokeh) in three
    depths. Seeded, so it comes out the same every run."""
    w, h = size
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    deep, purple, glow = np.array([22, 13, 48]), np.array([62, 36, 112]), np.array([150, 105, 230])
    t = np.clip(0.55 * x + 0.45 * y, 0, 1)[..., None]
    base = deep + (purple - deep) * t
    light = np.exp(-(((x - 0.62) / 0.42) ** 2 + ((y - 0.38) / 0.36) ** 2))[..., None]
    base = base + (glow - base) * 0.55 * light
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    streak = Image.new("L", size, 0)
    draw = ImageDraw.Draw(streak)
    for offset, width, strength in ((0, 90, 70), (170, 40, 45)):
        draw.line([(-200, h * 0.95 + offset), (w + 200, h * 0.05 + offset)], fill=strength, width=width)
    streak = streak.filter(ImageFilter.GaussianBlur(70))
    img.alpha_composite(Image.merge("RGBA", (*[Image.new("L", size, c) for c in (235, 220, 255)], streak)))

    tints = [(196, 160, 255), (255, 176, 230), (150, 125, 255), (232, 214, 255)]
    for count, radii, alphas, blur in ((14, (90, 170), (25, 55), 18), (30, (35, 85), (35, 90), 6),
                                       (34, (10, 30), (60, 150), 1.5)):
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for _ in range(count):
            r = rng.uniform(*radii)
            cx, cy = rng.uniform(-0.05, 1.05) * w, rng.uniform(-0.05, 1.05) * h
            colour = tints[rng.integers(len(tints))]
            a = int(rng.uniform(*alphas))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*colour, a),
                         outline=(*colour, min(255, int(a * 1.6))), width=max(1, int(r / 14)))
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    img.convert("RGB").filter(ImageFilter.GaussianBlur(0.8)).save(path, quality=90)


def look_and_feel(wallpaper_path, logo, package="org.houssamos.glass.desktop"):
    """Pictures for a HoussamOS Global Theme (system_files/.../look-and-feel/<package>). The light
    theme gets only previews; build.sh copies the splash into it from the dark one."""
    lnf = OUT / f"usr/share/plasma/look-and-feel/{package}/contents"
    (lnf / "previews").mkdir(parents=True, exist_ok=True)
    if package == "org.houssamos.glass.desktop":
        (lnf / "splash/images").mkdir(parents=True, exist_ok=True)
        logo.save(lnf / "splash/images/houssamos.png", optimize=True)

    wp = Image.open(wallpaper_path).convert("RGBA")
    full = wp.resize((1920, round(wp.height * 1920 / wp.width)), Image.LANCZOS)
    mark = logo.resize((560, round(logo.height * 560 / logo.width)), Image.LANCZOS)
    full.alpha_composite(mark, ((full.width - mark.width) // 2, (full.height - mark.height) // 2))
    full.convert("RGB").save(lnf / "previews/fullscreenpreview.jpg", quality=88)
    full.resize((400, round(full.height * 400 / full.width)), Image.LANCZOS).save(lnf / "previews/preview.png", optimize=True)

    print(f"global theme {package}: previews")


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
    boot_animation(SRC / "boot-animation-purple.mp4")
    icon_set = icons(SRC / "boot-animation.mp4")
    logo = wordmark(SRC / "logo-wordmark.png")
    wallpaper(SRC / "wallpaper-light.jpg", SRC / "wallpaper-dark.jpg")
    installer_art(SRC / "wallpaper-dark.jpg", logo)
    look_and_feel(SRC / "wallpaper-dark.jpg", logo)
    look_and_feel(SRC / "wallpaper-light.jpg", logo, "org.houssamos.glasslight.desktop")
    startup_sound(SRC / "boot-animation.mp4")
    if "--preview" in sys.argv:
        preview(icon_set, logo)
