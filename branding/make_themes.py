#!/usr/bin/env python3
"""Generate the themes `hosctl theme set` ships with: system_files/usr/share/houssamos/themes/<slug>/.

Each gets theme.json (palette, accent, fonts, icons, cursor, radius) and, except the two
HoussamOS ones (which use the system's own Aurora wallpaper and colour schemes), a layered-wave
wallpaper in its colours drawn with make_wallpapers.py's renderer. hosctl turns the palette into the
KDE colour scheme and Konsole colours when the theme is applied, so they aren't stored here.

Palettes are the projects' published ones. Usage: python branding/make_themes.py
"""
import json
from pathlib import Path

import make_wallpapers

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "system_files/usr/share/houssamos/themes"
SIZE = (3840, 2160)

# c0..c7 terminal colours (black red green yellow blue magenta cyan white), c8..c15 bright ones
THEMES = {
    "houssamos": {
        "name": "HoussamOS", "mode": "dark", "accent": "#4c8dff", "pair": "houssamos-light",
        "colors": {"bg": "#14182a", "fg": "#e8ecf4", "c0": "#0e1220", "c1": "#ff5c7a", "c2": "#3ddc97",
                   "c3": "#ffb547", "c4": "#4c8dff", "c5": "#8b6cff", "c6": "#5ad1ff", "c7": "#b6bed0"},
        "color_scheme": "HoussamOSDark", "konsole_scheme": "HoussamOS", "plasma_theme": "houssamos-glass",
        "icons": "HoussamOS-LiquidGlass", "cursor": "HoussamOS-Cursor",
        "wallpaper": "/usr/share/wallpapers/HoussamOS",
    },
    "houssamos-light": {
        "name": "HoussamOS Light", "mode": "light", "accent": "#2f6fe8", "pair": "houssamos",
        "colors": {"bg": "#f0f2f7", "fg": "#1c202c", "c0": "#c9cfdc", "c1": "#d6365a", "c2": "#1f9d68",
                   "c3": "#c27c0e", "c4": "#2f6fe8", "c5": "#6c4fe0", "c6": "#1288b8", "c7": "#4a5266"},
        "color_scheme": "HoussamOS", "plasma_theme": "houssamos-glass-light",
        "icons": "HoussamOS-LiquidGlass-Light", "cursor": "HoussamOS-Cursor",
        "wallpaper": "/usr/share/wallpapers/HoussamOS",
    },
    "tokyo-night": {
        "name": "Tokyo Night", "mode": "dark", "accent": "#7aa2f7",
        "colors": {"bg": "#1a1b26", "fg": "#c0caf5", "c0": "#15161e", "c1": "#f7768e", "c2": "#9ece6a",
                   "c3": "#e0af68", "c4": "#7aa2f7", "c5": "#bb9af7", "c6": "#7dcfff", "c7": "#a9b1d6",
                   "c8": "#414868", "c9": "#f7768e", "c10": "#9ece6a", "c11": "#e0af68", "c12": "#7aa2f7",
                   "c13": "#bb9af7", "c14": "#7dcfff", "c15": "#c0caf5"},
        "icons": "Papirus-Dark", "cursor": "Bibata-Modern-Ice",
    },
    "catppuccin-mocha": {
        "name": "Catppuccin Mocha", "mode": "dark", "accent": "#cba6f7", "pair": "catppuccin-latte",
        "colors": {"bg": "#1e1e2e", "fg": "#cdd6f4", "c0": "#45475a", "c1": "#f38ba8", "c2": "#a6e3a1",
                   "c3": "#f9e2af", "c4": "#89b4fa", "c5": "#f5c2e7", "c6": "#94e2d5", "c7": "#bac2de",
                   "c8": "#585b70", "c9": "#f38ba8", "c10": "#a6e3a1", "c11": "#f9e2af", "c12": "#89b4fa",
                   "c13": "#f5c2e7", "c14": "#94e2d5", "c15": "#a6adc8"},
        "icons": "Papirus-Dark", "cursor": "Bibata-Modern-Ice",
    },
    "catppuccin-latte": {
        "name": "Catppuccin Latte", "mode": "light", "accent": "#8839ef", "pair": "catppuccin-mocha",
        "colors": {"bg": "#eff1f5", "fg": "#4c4f69", "c0": "#5c5f77", "c1": "#d20f39", "c2": "#40a02b",
                   "c3": "#df8e1d", "c4": "#1e66f5", "c5": "#ea76cb", "c6": "#179299", "c7": "#acb0be",
                   "c8": "#6c6f85", "c9": "#d20f39", "c10": "#40a02b", "c11": "#df8e1d", "c12": "#1e66f5",
                   "c13": "#ea76cb", "c14": "#179299", "c15": "#bcc0cc"},
        "icons": "Papirus-Light", "cursor": "Bibata-Modern-Classic",
    },
    "nord": {
        "name": "Nord", "mode": "dark", "accent": "#88c0d0",
        "colors": {"bg": "#2e3440", "fg": "#d8dee9", "c0": "#3b4252", "c1": "#bf616a", "c2": "#a3be8c",
                   "c3": "#ebcb8b", "c4": "#81a1c1", "c5": "#b48ead", "c6": "#88c0d0", "c7": "#e5e9f0",
                   "c8": "#4c566a", "c9": "#bf616a", "c10": "#a3be8c", "c11": "#ebcb8b", "c12": "#81a1c1",
                   "c13": "#b48ead", "c14": "#8fbcbb", "c15": "#eceff4"},
        "icons": "Papirus-Dark", "cursor": "Bibata-Modern-Ice",
    },
    "gruvbox": {
        "name": "Gruvbox", "mode": "dark", "accent": "#d79921",
        "colors": {"bg": "#282828", "fg": "#ebdbb2", "c0": "#3c3836", "c1": "#cc241d", "c2": "#98971a",
                   "c3": "#d79921", "c4": "#458588", "c5": "#b16286", "c6": "#689d6a", "c7": "#a89984",
                   "c8": "#928374", "c9": "#fb4934", "c10": "#b8bb26", "c11": "#fabd2f", "c12": "#83a598",
                   "c13": "#d3869b", "c14": "#8ec07c", "c15": "#ebdbb2"},
        "icons": "Papirus-Dark", "cursor": "Bibata-Modern-Amber",
    },
    "rose-pine": {
        "name": "Rosé Pine", "mode": "dark", "accent": "#c4a7e7",
        "colors": {"bg": "#191724", "fg": "#e0def4", "c0": "#26233a", "c1": "#eb6f92", "c2": "#31748f",
                   "c3": "#f6c177", "c4": "#9ccfd8", "c5": "#c4a7e7", "c6": "#ebbcba", "c7": "#e0def4",
                   "c8": "#6e6a86", "c9": "#eb6f92", "c10": "#31748f", "c11": "#f6c177", "c12": "#9ccfd8",
                   "c13": "#c4a7e7", "c14": "#ebbcba", "c15": "#e0def4"},
        "icons": "Papirus-Dark", "cursor": "Bibata-Modern-Ice",
    },
    "everforest": {
        "name": "Everforest", "mode": "dark", "accent": "#a7c080",
        "colors": {"bg": "#2d353b", "fg": "#d3c6aa", "c0": "#343f44", "c1": "#e67e80", "c2": "#a7c080",
                   "c3": "#dbbc7f", "c4": "#7fbbb3", "c5": "#d699b6", "c6": "#83c092", "c7": "#d3c6aa",
                   "c8": "#859289", "c9": "#e67e80", "c10": "#a7c080", "c11": "#dbbc7f", "c12": "#7fbbb3",
                   "c13": "#d699b6", "c14": "#83c092", "c15": "#d3c6aa"},
        "icons": "Papirus-Dark", "cursor": "Bibata-Modern-Ice",
    },
}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def wallpaper_palette(t):
    """make_wallpapers.py's layered waves, coloured from the theme."""
    c = {k: rgb(v) for k, v in t["colors"].items()}
    bg, accent = c["bg"], rgb(t["accent"])
    dark = t["mode"] == "dark"
    white, black = (255, 255, 255), (0, 0, 0)
    if dark:
        layers = [
            (0.36, 0.060, 0.80, 0.4, mix(bg, accent, 0.80), mix(bg, c["c5"], 0.85), 0.55),
            (0.47, 0.075, 0.65, 2.1, mix(bg, c["c4"], 0.62), mix(bg, accent, 0.70), 0.60),
            (0.58, 0.060, 1.05, 3.6, mix(bg, c["c4"], 0.38), mix(bg, c["c5"], 0.45), 0.55),
            (0.69, 0.055, 0.75, 1.2, mix(bg, accent, 0.18), mix(bg, c["c5"], 0.22), 0.30),
            (0.81, 0.040, 1.30, 4.4, mix(bg, black, 0.25), mix(bg, black, 0.15), 0.20),
        ]
        return {"sky_top": mix(bg, black, 0.55), "sky_glow": mix(bg, accent, 0.35), "glow_at": 0.42,
                "layers": layers, "rim": mix(white, accent, 0.25), "shade": 0.45, "grain": 1.3}
    layers = [
        (0.36, 0.060, 0.80, 0.4, mix(bg, accent, 0.30), mix(bg, c["c5"], 0.30), 0.70),
        (0.47, 0.075, 0.65, 2.1, mix(bg, c["c4"], 0.38), mix(bg, accent, 0.40), 0.75),
        (0.58, 0.060, 1.05, 3.6, mix(bg, c["c4"], 0.22), mix(bg, c["c5"], 0.25), 0.70),
        (0.69, 0.055, 0.75, 1.2, mix(bg, white, 0.3), mix(bg, accent, 0.10), 0.65),
        (0.81, 0.040, 1.30, 4.4, mix(bg, white, 0.6), mix(bg, white, 0.5), 0.55),
    ]
    return {"sky_top": mix(bg, accent, 0.10), "sky_glow": mix(bg, white, 0.7), "glow_at": 0.42,
            "layers": layers, "rim": white, "shade": 0.10, "grain": 0.9}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, t in THEMES.items():
        d = OUT / slug
        d.mkdir(exist_ok=True)
        theme = {"name": t["name"], "author": "HoussamOS", **{k: v for k, v in t.items() if k != "name"}}
        theme.setdefault("font", "Inter")
        theme.setdefault("mono_font", "JetBrains Mono")
        theme.setdefault("radius", 12)
        if "wallpaper" not in theme:
            make_wallpapers.PALETTES[slug] = wallpaper_palette(t)
            make_wallpapers.render(slug, *SIZE).save(d / "wallpaper.jpg", quality=88, subsampling=0)
            theme["wallpaper"] = "wallpaper.jpg"
        (d / "theme.json").write_text(json.dumps(theme, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"{slug}: {theme['name']} ({theme['mode']})")


if __name__ == "__main__":
    main()
