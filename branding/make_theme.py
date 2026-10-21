#!/usr/bin/env python3
"""Generate the HoussamOS Glass Plasma theme and the HoussamOS colour schemes.

Everything is drawn as vector shapes (no pictures), so it stays sharp at any scale:
  - floating dock: rounded frosted glass, lighter at the top, with a bright rim of light
  - top bar: slim frosted strip with a hairline underneath
  - menus, popups, notifications, widgets and tooltips: dark glass, a little more solid
  - dock indicators: a soft glass tile behind the app in use or under the pointer, and a
    small light under every running app
Each shape also gets a mask, which is the exact area KWin blurs behind it (the live blur).
Elements a theme does not draw fall back to Breeze, coloured by the theme's colours.

All colours live in PALETTE, so the whole system can be recoloured in one place.
Usage: python branding/make_theme.py
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "system_files"
THEME_ID = "houssamos-glass"
DOCK_HEIGHT = 64      # logical px; the layout script uses the same value
TOPBAR_HEIGHT = 30

PALETTE = {
    "accent": (76, 141, 255),          # HoussamOS blue
    "accent_soft": (110, 165, 255),
    "violet": (139, 108, 255),
    "glass": (18, 22, 36),             # tint of all glass surfaces
    "edge": (255, 255, 255),           # the fine light edge
    "text": (232, 236, 244),
    "text_dim": (150, 160, 180),
    "positive": (61, 220, 151),
    "neutral": (255, 181, 71),
    "negative": (255, 92, 122),
}

# (radius, glass opacity, edge opacity, content margins top/bottom/left/right)
SHAPES = {
    "dock": (22, 0.14, 0.24, (6, 6, 10, 10)),
    "dialog": (14, 0.72, 0.12, (12, 12, 12, 12)),
    "tooltip": (10, 0.86, 0.12, (8, 8, 10, 10)),
}

# The dock is light frosted glass rather than dark glass, so it stays visible over dark windows:
# a pale tint, extra light at the top (glow) fading out over the top corners, and a brighter
# rim along the top edge where light would catch it.
DOCK_GLASS = {"tint": (236, 242, 255), "glow": 0.12, "rim": 0.55}

# Dock indicators (widgets/tasks.svg): corner size, glass tile radius, and the space around icons
TASK_CORNER = 22
TASK_RADIUS = 12
TASK_MARGINS = (3, 5, 4, 4)


def rgba(colour, alpha):
    return f'fill="rgb({colour[0]},{colour[1]},{colour[2]})" fill-opacity="{alpha:.3f}"'


class Svg:
    """Collects frame elements, each placed in its own cell so their sizes stay exact."""

    def __init__(self):
        self.parts, self.defs, self.row = [], [], 0

    def frame(self, prefix, radius, glass, edge, mask=False, hairline_only_bottom=False,
              tint=None, glow=0.0, rim=None):
        """The nine pieces Plasma stretches into a frame of any size.

        Corners are quarter circles, edges and centre are rectangles. The 1px light edge sits
        just inside the shape; for the top bar only a hairline at the bottom is drawn.
        tint, glow and rim are for the dock: the glass colour, extra opacity at the very top that
        fades out over the top corners, and the opacity of the top edge (the others use edge).
        """
        r, w = max(radius, 1), 10
        g = tint or PALETTE["glass"]
        rim = edge if rim is None else rim
        fill = 'fill="#000000"' if mask else rgba(g, glass)
        top_fill = fill
        if glow and not mask and radius > 1:
            gid = f"glow{self.row}"
            colour = f"rgb({g[0]},{g[1]},{g[2]})"
            self.defs.append(
                f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{r}">'
                f'<stop offset="0" stop-color="{colour}" stop-opacity="{glass + glow:.3f}"/>'
                f'<stop offset="1" stop-color="{colour}" stop-opacity="{glass:.3f}"/></linearGradient>')
            top_fill = f'fill="url(#{gid})"'
        line = 'fill="#000000" fill-opacity="0"' if mask else rgba(PALETTE["edge"], edge)
        top_line = 'fill="#000000" fill-opacity="0"' if mask else rgba(PALETTE["edge"], rim)
        y0 = self.row * 40
        x = 0
        pieces = []

        def corner(name, cx, cy, sweep_path):
            top = name.startswith("top")
            pieces.append((name, r, r, f'<path {top_fill if top else fill} d="{sweep_path}"/>' + (
                "" if mask or hairline_only_bottom or radius <= 1 else
                f'<path fill="none" stroke="rgb(255,255,255)" stroke-opacity="{rim if top else edge:.3f}" '
                f'stroke-width="1" d="{arc_line(name, r)}"/>')))

        if radius > 1:
            corner("topleft", r, r, f"M{r},{r} L0,{r} A{r},{r} 0 0 1 {r},0 Z")
            corner("topright", 0, r, f"M0,{r} L0,0 A{r},{r} 0 0 1 {r},{r} Z")
            corner("bottomleft", r, 0, f"M{r},0 L{r},{r} A{r},{r} 0 0 1 0,0 Z")
            corner("bottomright", 0, 0, f"M0,0 L{r},0 A{r},{r} 0 0 1 0,{r} Z")
        else:
            for name in ("topleft", "topright", "bottomleft", "bottomright"):
                body = f'<rect {fill} width="1" height="1"/>'
                if name.startswith("bottom") and hairline_only_bottom and not mask:
                    body += f'<rect {line} width="1" height="1"/>'
                pieces.append((name, 1, 1, body))

        def edge_piece(name, pw, ph, line_rect, body_fill=fill, line_fill=line):
            body = f'<rect {body_fill} width="{pw}" height="{ph}"/>'
            if line_rect and not mask:
                body += (f'<rect {line_fill} x="{line_rect[0]}" y="{line_rect[1]}" '
                         f'width="{line_rect[2]}" height="{line_rect[3]}"/>')
            pieces.append((name, pw, ph, body))

        if hairline_only_bottom:
            edge_piece("top", w, r, None)
            edge_piece("left", r, w, None)
            edge_piece("right", r, w, None)
            edge_piece("bottom", w, r, (0, r - 1, w, 1))
        else:
            edge_piece("top", w, r, (0, 0, w, 1), top_fill, top_line)
            edge_piece("left", r, w, (0, 0, 1, w))
            edge_piece("right", r, w, (r - 1, 0, 1, w))
            edge_piece("bottom", w, r, (0, r - 1, w, 1))
        pieces.append(("center", w, w, f'<rect {fill} width="{w}" height="{w}"/>'))

        for name, pw, ph, body in pieces:
            self.parts.append(f'<g id="{prefix}{name}" transform="translate({x},{y0})">{body}</g>')
            x += pw + 6
        self.row += 2

    def task_frame(self, prefix, tile=None, light=None):
        """One dock indicator state for widgets/tasks.svg.

        tile is (fill opacity, edge opacity) of the rounded glass tile behind the icon, or None.
        light is (colour, opacity) of the small light under the icon, or None. The light sits in
        the bottom edge piece, which Plasma stretches across the icon minus the two corners, so
        the wide corners keep it short.
        """
        c, r, w = TASK_CORNER, TASK_RADIUS, 10
        white = PALETTE["edge"]
        clear = 'fill="#000000" fill-opacity="0"'
        fill = rgba(white, tile[0]) if tile else clear
        a = r - 0.5
        shape = f"M0,{c} L0,{r} A{r},{r} 0 0 1 {r},0 L{c},0 L{c},{c} Z"
        outline = f"M0.5,{c} L0.5,{r} A{a},{a} 0 0 1 {r},0.5 L{c},0.5"
        pieces = []
        # One corner drawn once, mirrored into the other three
        for name, flip in (("topleft", ""), ("topright", f"translate({c},0) scale(-1,1)"),
                           ("bottomleft", f"translate(0,{c}) scale(1,-1)"),
                           ("bottomright", f"translate({c},{c}) scale(-1,-1)")):
            body = f'<path {fill} d="{shape}"/>'
            if tile:
                body += (f'<path fill="none" stroke="rgb(255,255,255)" stroke-opacity="{tile[1]:.3f}" '
                         f'stroke-width="1" d="{outline}"/>')
            pieces.append((name, c, c, f'<g transform="{flip}">{body}</g>' if flip else body))

        def side(name, pw, ph, line_rect, extra=""):
            body = f'<rect {fill} width="{pw}" height="{ph}"/>'
            if tile:
                body += (f'<rect {rgba(white, tile[1])} x="{line_rect[0]}" y="{line_rect[1]}" '
                         f'width="{line_rect[2]}" height="{line_rect[3]}"/>')
            pieces.append((name, pw, ph, body + extra))

        dot = ""
        if light:
            dot = f'<rect {rgba(light[0], light[1])} x="0" y="{c - 4}" width="{w}" height="2.5" rx="1.25"/>'
        side("top", w, c, (0, 0, w, 1))
        side("bottom", w, c, (0, c - 1, w, 1), dot)
        side("left", c, w, (0, 0, 1, w))
        side("right", c, w, (c - 1, 0, 1, w))
        pieces.append(("center", w, w, f'<rect {fill} width="{w}" height="{w}"/>'))

        y0, x = self.row * 40, 0
        for name, pw, ph, body in pieces:
            self.parts.append(f'<g id="{prefix}{name}" transform="translate({x},{y0})">{body}</g>')
            x += pw + 6
        self.row += 2

    def hints(self, prefix, margins):
        top, bottom, left, right = margins
        y0 = self.row * 40
        items = [("hint-stretch-borders", 1, 1), ("hint-top-margin", 1, top), ("hint-bottom-margin", 1, bottom),
                 ("hint-left-margin", left, 1), ("hint-right-margin", right, 1)]
        for i, (name, w, h) in enumerate(items):
            self.parts.append(f'<rect id="{prefix}{name}" x="{i * 30}" y="{y0}" width="{w}" height="{h}" '
                              f'fill="#000000" fill-opacity="0"/>')
        self.row += 1

    def text(self):
        height = self.row * 40 + 40
        defs = "<defs>" + "".join(self.defs) + "</defs>\n" if self.defs else ""
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="%d" viewBox="0 0 400 %d">\n' % (height, height)
                + defs + "\n".join(self.parts) + "\n</svg>\n")


def arc_line(corner, r):
    """The light edge along a corner: an arc 0.5px inside the shape's outline."""
    a = r - 0.5
    return {
        "topleft": f"M0.5,{r} A{a},{a} 0 0 1 {r},0.5",
        "topright": f"M0,0.5 A{a},{a} 0 0 1 {r - 0.5},{r}",
        "bottomleft": f"M{r},{r - 0.5} A{a},{a} 0 0 1 0.5,0",
        "bottomright": f"M{r - 0.5},0 A{a},{a} 0 0 1 0,{r - 0.5}",
    }[corner]


def frame_svg(shape, with_topbar=False):
    radius, glass, edge, margins = SHAPES[shape]
    look = DOCK_GLASS if shape == "dock" else {}
    svg = Svg()
    svg.frame("", radius, glass, edge, **look)
    svg.frame("mask-", radius, glass, edge, mask=True)
    svg.hints("", margins)
    if with_topbar:
        # Top bar: "north-" elements. The mask naming differs between Plasma versions,
        # so both orders are provided.
        svg.frame("north-", 1, 0.55, 0.08, hairline_only_bottom=True)
        svg.frame("north-mask-", 1, 0.55, 0.08, mask=True, hairline_only_bottom=True)
        svg.frame("mask-north-", 1, 0.55, 0.08, mask=True, hairline_only_bottom=True)
        svg.hints("north-", (2, 2, 6, 6))
    return svg.text()


def tasks_svg():
    """Dock indicators. The task manager asks for a state ("focus" is the app in use, the
    unprefixed frame is a pinned app that isn't running) with "-hover" when the pointer is on it,
    falling back to "hover" and then to the plain state. Every state gets the same margins so
    icons keep their size when an app starts."""
    white, attention = PALETTE["edge"], PALETTE["neutral"]
    states = {
        "": (None, None),
        "normal-": (None, (white, 0.55)),
        "minimized-": (None, (white, 0.30)),
        "attention-": (None, (attention, 0.95)),
        "focus-": ((0.12, 0.20), (white, 0.95)),
        "hover-": ((0.08, 0.14), (white, 0.55)),
        "launcher-hover-": ((0.08, 0.14), None),
        "focus-hover-": ((0.16, 0.24), (white, 0.95)),
        "minimized-hover-": ((0.08, 0.14), (white, 0.30)),
        "attention-hover-": ((0.08, 0.14), (attention, 0.95)),
    }
    svg = Svg()
    for prefix, (tile, light) in states.items():
        svg.task_frame(prefix, tile, light)
        svg.hints(prefix, TASK_MARGINS)
    return svg.text()


def colour_groups(dark):
    a, soft, violet = PALETTE["accent"], PALETTE["accent_soft"], PALETTE["violet"]
    if dark:
        text, dim = PALETTE["text"], PALETTE["text_dim"]
        groups = {
            "Window": ((20, 24, 36), (26, 31, 46)),
            "View": ((14, 17, 27), (20, 24, 36)),
            "Button": ((32, 38, 56), (44, 52, 76)),
            "Header": ((16, 20, 30), (20, 24, 36)),
            "Tooltip": ((20, 24, 36), (26, 31, 46)),
            "Complementary": ((10, 13, 22), (16, 20, 30)),
        }
        link = soft
    else:
        text, dim = (28, 32, 44), (105, 115, 135)
        groups = {
            "Window": ((240, 242, 247), (230, 233, 240)),
            "View": ((252, 252, 254), (244, 246, 250)),
            "Button": ((248, 249, 252), (232, 236, 244)),
            "Header": ((228, 232, 240), (240, 242, 247)),
            "Tooltip": ((250, 250, 252), (240, 242, 247)),
            "Complementary": ((20, 24, 36), (26, 31, 46)),
        }
        a, link = (47, 111, 232), (47, 111, 232)

    def group(bg, alt, fg, fg_dim):
        return {
            "BackgroundNormal": bg, "BackgroundAlternate": alt,
            "ForegroundNormal": fg, "ForegroundInactive": fg_dim, "ForegroundActive": a,
            "ForegroundLink": link, "ForegroundVisited": violet,
            "ForegroundNegative": PALETTE["negative"], "ForegroundNeutral": PALETTE["neutral"],
            "ForegroundPositive": PALETTE["positive"],
            "DecorationFocus": a, "DecorationHover": soft,
        }

    out = {}
    for name, (bg, alt) in groups.items():
        dark_group = dark or name == "Complementary"
        fg = PALETTE["text"] if dark_group else text
        fg_dim = PALETTE["text_dim"] if dark_group else dim
        out[name] = group(bg, alt, fg, fg_dim)
    out["Selection"] = group(a, soft, (255, 255, 255), (230, 238, 255))
    return out


def colours_text(dark, name=None):
    lines = []
    if name:
        lines += ["[General]", f"ColorScheme={name}", f"Name={name.replace('OSDark', 'OS Dark')}", "",
                  "[KDE]", "contrast=4", ""]
        title_bg = (16, 20, 30) if dark else (228, 232, 240)
        title_fg = PALETTE["text"] if dark else (28, 32, 44)
        idle_bg = (20, 24, 36) if dark else (240, 242, 247)
        lines += ["[WM]"] + [f"{k}={','.join(map(str, v))}" for k, v in (
            ("activeBackground", title_bg), ("activeBlend", title_bg), ("activeForeground", title_fg),
            ("inactiveBackground", idle_bg), ("inactiveBlend", idle_bg),
            ("inactiveForeground", PALETTE["text_dim"]))] + [""]
    for group, keys in sorted(colour_groups(dark).items()):
        lines.append(f"[Colors:{group}]")
        lines += [f"{k}={','.join(map(str, v))}" for k, v in sorted(keys.items())]
        lines.append("")
    return "\n".join(lines)


def main():
    theme = OUT / f"usr/share/plasma/desktoptheme/{THEME_ID}"
    if theme.exists():
        shutil.rmtree(theme)
    files = {
        "widgets/panel-background.svg": frame_svg("dock", with_topbar=True),
        "dialogs/background.svg": frame_svg("dialog"),
        "widgets/background.svg": frame_svg("dialog"),
        "widgets/tooltip.svg": frame_svg("tooltip"),
        "widgets/tasks.svg": tasks_svg(),
    }
    for sub in ("", "translucent/"):     # translucent/ is what Plasma uses with compositing
        for rel, text in files.items():
            path = theme / sub / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, newline="\n")
    (theme / "metadata.json").write_text(json.dumps({
        "KPlugin": {"Id": THEME_ID, "Name": "HoussamOS Glass",
                    "Description": "Glass with live blur: floating frosted dock, slim top bar, glass menus",
                    "Authors": [{"Name": "Houssam"}], "License": "CC-BY-SA-4.0", "Version": "2.1",
                    "Website": "https://github.com/Houssam-2021/housos"},
        "X-Plasma-API-Minimum-Version": "6.0"
    }, indent=4) + "\n", newline="\n")
    (theme / "plasmarc").write_text(
        "[BlurBehindEffect]\nenabled=true\n\n"
        "[ContrastEffect]\nenabled=true\ncontrast=0.25\nintensity=0.85\nsaturation=1.6\n\n"
        "[AdaptiveTransparency]\nenabled=false\n", newline="\n")
    (theme / "colors").write_text(colours_text(dark=True), newline="\n")

    schemes = OUT / "usr/share/color-schemes"
    schemes.mkdir(parents=True, exist_ok=True)
    (schemes / "HoussamOSDark.colors").write_text(colours_text(True, "HoussamOSDark"), newline="\n")
    (schemes / "HoussamOS.colors").write_text(colours_text(False, "HoussamOS"), newline="\n")
    print(f"theme {THEME_ID}: {len(files)} frame files (+ translucent copies), colour schemes HoussamOSDark, HoussamOS")


if __name__ == "__main__":
    main()
