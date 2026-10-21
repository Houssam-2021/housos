#!/usr/bin/env python3
"""Generate the HoussamOS Liquid Glass v2 3D icon theme into system_files/.

Every app icon uses a 4-anchor cubic Bezier superellipse (squircle) and a real SVG
<feSpecularLighting> 3D bevel filter on its multi-layered glyph. Folders use 3D
layered sky-blue glass plates. Any icon not in this pack falls back via index.theme:
    Inherits=Tela-dark,breeze-dark,breeze,hicolor
so un-themed apps and symbolic system tray icons use Tela-dark / breeze-dark.

Usage: python branding/make_icons.py
"""
import math
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = "HoussamOS-LiquidGlass"
OUT = ROOT / "system_files" / "usr/share/icons" / THEME

SQUIRCLE_PATH = (
    "M 74,22 "
    "L 182,22 "
    "C 215,22 234,41 234,74 "
    "L 234,182 "
    "C 234,215 215,234 182,234 "
    "L 74,234 "
    "C 41,234 22,215 22,182 "
    "L 22,74 "
    "C 22,41 41,22 74,22 Z"
)

SQUIRCLE_INNER = (
    "M 75,25 "
    "L 181,25 "
    "C 212,25 231,44 231,75 "
    "L 231,181 "
    "C 231,212 212,231 181,231 "
    "L 75,231 "
    "C 44,231 25,212 25,181 "
    "L 25,75 "
    "C 25,44 44,25 75,25 Z"
)

SQUIRCLE_SHADOW = (
    "M 74,29 "
    "L 182,29 "
    "C 215,29 234,48 234,81 "
    "L 234,189 "
    "C 234,222 215,241 182,241 "
    "L 74,241 "
    "C 41,241 22,222 22,189 "
    "L 22,81 "
    "C 22,48 41,29 74,29 Z"
)


def make_gear_path(cx=128.0, cy=128.0, teeth=10, r_outer=72.0, r_root=57.0) -> str:
    pts = []
    step = 2.0 * math.pi / teeth
    for i in range(teeth):
        a0 = i * step - math.pi / 2.0
        angles = [
            (a0 - 0.30 * step, r_root),
            (a0 - 0.17 * step, r_outer),
            (a0 + 0.17 * step, r_outer),
            (a0 + 0.30 * step, r_root),
        ]
        for ang, r in angles:
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d = f"M {pts[0][0]:.2f},{pts[0][1]:.2f} "
    d += " ".join(f"L {x:.2f},{y:.2f}" for x, y in pts[1:])
    return d + " Z"


GEAR_OUTLINE_PATH = make_gear_path()


def make_liquid_glass_squircle(
    uid: str,
    c_top: str,
    c_mid: str,
    c_bot: str,
    c_glow: str,
    glyph_svg: str,
) -> str:
    hydrated_glyph = glyph_svg.replace("__UID__", uid)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <defs>
    <clipPath id="clip_{uid}">
      <path d="{SQUIRCLE_PATH}"/>
    </clipPath>

    <linearGradient id="bg_{uid}" x1="16%" y1="6%" x2="84%" y2="94%">
      <stop offset="0%" stop-color="{c_top}" stop-opacity="0.98"/>
      <stop offset="48%" stop-color="{c_mid}" stop-opacity="0.96"/>
      <stop offset="100%" stop-color="{c_bot}" stop-opacity="0.99"/>
    </linearGradient>

    <radialGradient id="top_light_{uid}" cx="26%" cy="14%" r="68%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.50"/>
      <stop offset="45%" stop-color="#FFFFFF" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>

    <radialGradient id="caustic_{uid}" cx="68%" cy="92%" r="60%">
      <stop offset="0%" stop-color="{c_glow}" stop-opacity="0.72"/>
      <stop offset="55%" stop-color="{c_glow}" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="{c_glow}" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="rim_outer_{uid}" x1="12%" y1="4%" x2="88%" y2="96%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="28%" stop-color="#E0F2FE" stop-opacity="0.58"/>
      <stop offset="62%" stop-color="#FFFFFF" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{c_glow}" stop-opacity="0.80"/>
    </linearGradient>

    <linearGradient id="rim_inner_{uid}" x1="85%" y1="92%" x2="15%" y2="8%">
      <stop offset="0%" stop-color="{c_glow}" stop-opacity="0.55"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.50"/>
    </linearGradient>

    <linearGradient id="glass_white_{uid}" x1="22%" y1="10%" x2="78%" y2="90%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="1"/>
      <stop offset="58%" stop-color="#F1F5F9" stop-opacity="0.96"/>
      <stop offset="100%" stop-color="#CBD5E1" stop-opacity="0.90"/>
    </linearGradient>

    <linearGradient id="glass_sub_{uid}" x1="20%" y1="10%" x2="80%" y2="92%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.84"/>
      <stop offset="100%" stop-color="#CBD5E1" stop-opacity="0.52"/>
    </linearGradient>

    <filter id="bevel3d_{uid}" x="-22%" y="-22%" width="144%" height="144%" color-interpolation-filters="sRGB">
      <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#020617" flood-opacity="0.40" result="drop1"/>
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#020617" flood-opacity="0.26" in="SourceGraphic" result="drop2"/>
      <feMerge result="shadows">
        <feMergeNode in="drop1"/>
        <feMergeNode in="drop2"/>
      </feMerge>
      <feGaussianBlur in="SourceAlpha" stdDeviation="2.4" result="blur_alpha"/>
      <feSpecularLighting in="blur_alpha" surfaceScale="5" specularConstant="0.95" specularExponent="28" lighting-color="#FFFFFF" result="spec_raw">
        <fePointLight x="68" y="42" z="165"/>
      </feSpecularLighting>
      <feComposite in="spec_raw" in2="SourceAlpha" operator="in" result="spec_masked"/>
      <feMerge>
        <feMergeNode in="shadows"/>
        <feMergeNode in="SourceGraphic"/>
        <feMergeNode in="spec_masked"/>
      </feMerge>
    </filter>
  </defs>

  <path d="{SQUIRCLE_SHADOW}" fill="#020617" fill-opacity="0.28"/>
  <path d="{SQUIRCLE_PATH}" fill="url(#bg_{uid})"/>

  <g clip-path="url(#clip_{uid})">
    <circle cx="158" cy="222" r="128" fill="url(#caustic_{uid})"/>
    <circle cx="76" cy="48" r="142" fill="url(#top_light_{uid})"/>
    <path d="M 16,20 L 240,20 L 240,96 C 186,70 86,86 16,120 Z" fill="#FFFFFF" fill-opacity="0.10"/>
    <g filter="url(#bevel3d_{uid})">
      {hydrated_glyph}
    </g>
  </g>

  <path d="{SQUIRCLE_INNER}" fill="none" stroke="url(#rim_inner_{uid})" stroke-width="1.5"/>
  <path d="{SQUIRCLE_PATH}" fill="none" stroke="url(#rim_outer_{uid})" stroke-width="2.2"/>
</svg>
"""


APP_ICONS = [
    {
        "id": "firefox",
        "colors": ("#2E1760", "#180B38", "#0A041C", "#FF6B2B"),
        "aliases": [
            "firefox",
            "org.mozilla.firefox",
            "firefox-esr",
            "web-browser",
            "internet-web-browser",
            "applications-internet",
        ],
        "glyph": """
  <defs>
    <radialGradient id="ff_globe___UID__" cx="38%" cy="32%" r="68%">
      <stop offset="0%" stop-color="#5CE1E6"/>
      <stop offset="45%" stop-color="#3B5BDB"/>
      <stop offset="100%" stop-color="#240046"/>
    </radialGradient>
    <linearGradient id="ff_tail___UID__" x1="15%" y1="90%" x2="88%" y2="12%">
      <stop offset="0%" stop-color="#FF2A6D"/>
      <stop offset="42%" stop-color="#FF6B1A"/>
      <stop offset="80%" stop-color="#FFB800"/>
      <stop offset="100%" stop-color="#FFF3B0"/>
    </linearGradient>
    <linearGradient id="ff_crest___UID__" x1="20%" y1="80%" x2="85%" y2="20%">
      <stop offset="0%" stop-color="#FF5400"/>
      <stop offset="55%" stop-color="#FF9E00"/>
      <stop offset="100%" stop-color="#FFEE99"/>
    </linearGradient>
  </defs>
  <circle cx="128" cy="132" r="56" fill="url(#ff_globe___UID__)"/>
  <circle cx="128" cy="132" r="55" fill="none" stroke="#A5F3FC" stroke-width="1.5" stroke-opacity="0.45"/>
  <path d="M 176,66 C 164,54 146,52 134,58 C 142,64 146,72 146,82 C 135,74 118,74 106,84 C 95,94 94,112 104,124 C 90,118 82,102 86,84 C 66,98 56,124 62,150 C 70,182 102,202 136,198 C 174,194 200,160 196,120 C 194,98 186,78 176,66 Z"
        fill="url(#ff_tail___UID__)"/>
  <path d="M 60,126 C 56,162 84,196 126,198 C 168,200 198,166 196,122 C 194,94 178,72 160,64 C 172,82 174,108 162,126 C 148,146 120,152 100,138 C 86,128 82,110 88,94 C 72,102 62,112 60,126 Z"
        fill="url(#ff_crest___UID__)"/>
  <path d="M 160,64 C 180,84 186,118 170,146 C 154,174 118,184 90,168 C 118,176 148,162 158,136 C 166,114 162,86 146,72 C 152,68 156,66 160,64 Z"
        fill="#FFF8D6" fill-opacity="0.65"/>
""",
    },
    {
        "id": "steam",
        "colors": ("#1E56B8", "#102E6B", "#071433", "#4CC9F0"),
        "aliases": [
            "steam",
            "com.valvesoftware.Steam",
            "steam-icon",
            "steam_icon_default",
            "lutris_steam",
        ],
        "glyph": """
  <path d="M 134,84 L 172,116 L 114,172 L 82,144 Z" fill="url(#glass_sub___UID__)"/>
  <path d="M 30,118 L 104,144 L 92,172 L 24,146 Z" fill="url(#glass_white___UID__)"/>
  <circle cx="154" cy="100" r="35" fill="url(#glass_white___UID__)"/>
  <circle cx="154" cy="100" r="21" fill="#0D2559"/>
  <circle cx="154" cy="100" r="13" fill="url(#glass_white___UID__)"/>
  <circle cx="98" cy="158" r="25" fill="url(#glass_white___UID__)"/>
  <circle cx="98" cy="158" r="15" fill="#0D2559"/>
  <circle cx="98" cy="158" r="9.5" fill="url(#glass_white___UID__)"/>
""",
    },
    {
        "id": "dolphin",
        "colors": ("#48CAE4", "#0096C7", "#023E8A", "#90E0EF"),
        "aliases": [
            "org.kde.dolphin",
            "system-file-manager",
            "dolphin",
            "folder-manager",
            "org.gnome.Nautilus",
            "thunar",
        ],
        "glyph": """
  <defs>
    <linearGradient id="dlp_front___UID__" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.96"/>
      <stop offset="100%" stop-color="#CAF0F8" stop-opacity="0.88"/>
    </linearGradient>
  </defs>
  <path d="M 52,82 C 52,71 61,62 72,62 L 108,62 C 115,62 121,65 126,71 L 133,79 L 184,79 C 195,79 204,88 204,99 L 204,172 C 204,183 195,192 184,192 L 72,192 C 61,192 52,183 52,172 Z"
        fill="url(#glass_sub___UID__)"/>
  <rect x="64" y="82" width="128" height="44" rx="10" fill="#FFFFFF" fill-opacity="0.88"/>
  <rect x="52" y="96" width="152" height="96" rx="22" fill="url(#dlp_front___UID__)"/>
  <path d="M 88,144 C 104,126 126,126 142,140 C 154,150 164,148 172,140"
        fill="none" stroke="#0077B6" stroke-width="8" stroke-linecap="round" stroke-opacity="0.55"/>
""",
    },
    {
        "id": "terminal",
        "colors": ("#33394B", "#1A1E29", "#0B0D13", "#38BDF8"),
        "aliases": [
            "org.kde.konsole",
            "utilities-terminal",
            "terminal",
            "konsole",
            "kde-ptyxis",
            "org.gnome.Ptyxis",
            "org.gnome.Terminal",
            "alacritty",
            "kitty",
        ],
        "glyph": """
  <rect x="46" y="52" width="164" height="152" rx="28" fill="#07090E" fill-opacity="0.72"
        stroke="#FFFFFF" stroke-width="1.5" stroke-opacity="0.22"/>
  <circle cx="70" cy="74" r="5.5" fill="#FF5F56"/>
  <circle cx="88" cy="74" r="5.5" fill="#FFBD2E"/>
  <circle cx="106" cy="74" r="5.5" fill="#27C93F"/>
  <path d="M 74,108 L 112,136 L 74,164" fill="none" stroke="url(#glass_white___UID__)"
        stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="124" y="154" width="48" height="14" rx="7" fill="#38BDF8"/>
""",
    },
    {
        "id": "settings",
        "colors": ("#64748B", "#334155", "#1E293B", "#94A3B8"),
        "aliases": [
            "systemsettings",
            "org.kde.systemsettings",
            "preferences-system",
            "gnome-control-center",
            "configuration_section",
            "gearlever",
            "it.mijorus.gearlever",
        ],
        "glyph": f"""
  <path d="{GEAR_OUTLINE_PATH}" fill="url(#glass_white___UID__)"/>
  <circle cx="128" cy="128" r="40" fill="#1E293B" stroke="#FFFFFF" stroke-width="2" stroke-opacity="0.45"/>
  <line x1="128" y1="88" x2="128" y2="128" stroke="url(#glass_sub___UID__)" stroke-width="9" stroke-linecap="round"/>
  <line x1="128" y1="128" x2="162.6" y2="148" stroke="url(#glass_sub___UID__)" stroke-width="9" stroke-linecap="round"/>
  <line x1="128" y1="128" x2="93.4" y2="148" stroke="url(#glass_sub___UID__)" stroke-width="9" stroke-linecap="round"/>
  <circle cx="128" cy="128" r="16" fill="url(#glass_white___UID__)"/>
  <circle cx="128" cy="128" r="7" fill="#334155"/>
""",
    },
    {
        "id": "discover",
        "colors": ("#00C6FF", "#0072FF", "#0039A6", "#72EFDD"),
        "aliases": [
            "org.kde.discover",
            "plasmadiscover",
            "system-software-install",
            "applications-other",
            "io.github.kolunmi.Bazaar",
            "bazaar",
            "org.gnome.Software",
        ],
        "glyph": """
  <path d="M 98,94 C 98,70 158,70 158,94" fill="none" stroke="url(#glass_sub___UID__)"
        stroke-width="11" stroke-linecap="round"/>
  <rect x="64" y="88" width="128" height="108" rx="26" fill="url(#glass_white___UID__)"/>
  <path d="M 128,110 L 137,133 L 160,142 L 137,151 L 128,174 L 119,151 L 96,142 L 119,133 Z"
        fill="#0066FF"/>
""",
    },
    {
        "id": "lutris",
        "colors": ("#FFB703", "#FB8500", "#B53800", "#FFE169"),
        "aliases": [
            "lutris",
            "net.lutris.Lutris",
            "applications-games",
            "input-gaming",
        ],
        "glyph": """
  <path d="M 84,84 L 172,84 C 194,84 206,104 202,134 L 194,168 C 190,186 172,192 158,178 L 142,160 L 114,160 L 98,178 C 84,192 66,186 62,168 L 54,134 C 50,104 62,84 84,84 Z"
        fill="url(#glass_white___UID__)"/>
  <rect x="82" y="104" width="11" height="31" rx="4" fill="#D9530F"/>
  <rect x="72" y="114" width="31" height="11" rx="4" fill="#D9530F"/>
  <circle cx="168" cy="106" r="6" fill="#F59E0B"/>
  <circle cx="180" cy="118" r="6" fill="#EF4444"/>
  <circle cx="168" cy="130" r="6" fill="#10B981"/>
  <circle cx="156" cy="118" r="6" fill="#3B82F6"/>
  <circle cx="110" cy="142" r="10" fill="#B53800" fill-opacity="0.75"/>
  <circle cx="146" cy="142" r="10" fill="#B53800" fill-opacity="0.75"/>
""",
    },
    {
        "id": "music",
        "colors": ("#FF5D8F", "#F72585", "#9B0650", "#FFACC5"),
        "aliases": [
            "org.kde.elisa",
            "elisa",
            "multimedia-audio-player",
            "spotify",
            "com.spotify.Client",
            "rhythmbox",
            "amberol",
        ],
        "glyph": """
  <path d="M 102,78 L 178,64 L 178,92 L 102,106 Z" fill="url(#glass_white___UID__)"/>
  <rect x="102" y="82" width="13" height="82" rx="6" fill="url(#glass_white___UID__)"/>
  <rect x="165" y="68" width="13" height="82" rx="6" fill="url(#glass_white___UID__)"/>
  <ellipse cx="89" cy="166" rx="22" ry="16" transform="rotate(-16 89 166)" fill="url(#glass_white___UID__)"/>
  <ellipse cx="152" cy="152" rx="22" ry="16" transform="rotate(-16 152 152)" fill="url(#glass_white___UID__)"/>
""",
    },
    {
        "id": "heroic",
        "colors": ("#06D6A0", "#098171", "#053B44", "#80FFDB"),
        "aliases": [
            "heroic",
            "com.heroicgameslauncher.hgl",
        ],
        "glyph": """
  <path d="M 128,52 L 188,74 L 188,128 C 188,166 158,192 128,204 C 98,192 68,166 68,128 L 68,74 Z"
        fill="url(#glass_sub___UID__)"/>
  <path d="M 128,64 L 176,82 L 176,126 C 176,158 152,180 128,190 C 104,180 80,158 80,126 L 80,82 Z"
        fill="#064E52" fill-opacity="0.65"/>
  <path d="M 128,70 L 138,88 L 135,146 L 121,146 L 118,88 Z" fill="url(#glass_white___UID__)"/>
  <path d="M 100,142 L 156,142 L 150,154 L 106,154 Z" fill="url(#glass_white___UID__)"/>
  <rect x="122" y="152" width="12" height="22" rx="5" fill="url(#glass_white___UID__)"/>
  <circle cx="128" cy="178" r="8" fill="url(#glass_white___UID__)"/>
""",
    },
    {
        "id": "protonup",
        "colors": ("#9D4EDD", "#5A189A", "#240046", "#E0AAFF"),
        "aliases": [
            "net.davidotek.pupgui2",
            "protonup-qt",
            "pupgui2",
        ],
        "glyph": """
  <g fill="none" stroke="url(#glass_sub___UID__)" stroke-width="6.5">
    <ellipse cx="128" cy="128" rx="72" ry="26" transform="rotate(30 128 128)"/>
    <ellipse cx="128" cy="128" rx="72" ry="26" transform="rotate(90 128 128)"/>
    <ellipse cx="128" cy="128" rx="72" ry="26" transform="rotate(150 128 128)"/>
  </g>
  <circle cx="128" cy="128" r="26" fill="url(#glass_white___UID__)"/>
  <path d="M 114,134 L 128,118 L 142,134" fill="none" stroke="#5A189A"
        stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    {
        "id": "gamemode",
        "colors": ("#6366F1", "#3730A3", "#1E1B4B", "#818CF8"),
        "aliases": [
            "steamos-gamemode",
            "Return-to-Gaming-Mode",
            "bazzite-steam-bpm",
            "ublue-update",
        ],
        "glyph": """
  <rect x="44" y="84" width="168" height="88" rx="42" fill="url(#glass_white___UID__)"/>
  <rect x="86" y="96" width="84" height="64" rx="10" fill="#1E1B4B"/>
  <circle cx="128" cy="128" r="16" fill="none" stroke="#38BDF8" stroke-width="5"/>
  <circle cx="128" cy="128" r="6" fill="#A855F7"/>
  <circle cx="65" cy="122" r="10" fill="#312E81"/>
  <circle cx="191" cy="122" r="10" fill="#312E81"/>
""",
    },
    {
        "id": "discord",
        "colors": ("#7289DA", "#5865F2", "#313B9E", "#A5B4FC"),
        "aliases": [
            "discord",
            "com.discordapp.Discord",
            "dev.vencord.Vesktop",
            "vesktop",
        ],
        "glyph": """
  <path d="M 174,78 C 162,72 150,69 138,68 L 134,77 C 122,75 110,75 98,77 L 94,68 C 82,69 70,72 58,78 C 44,104 40,132 46,160 C 60,172 76,178 92,180 L 100,166 C 92,163 85,159 79,154 C 96,164 136,164 153,154 C 147,159 140,163 132,166 L 140,180 C 156,178 172,172 186,160 C 192,132 188,104 174,78 Z"
        transform="translate(12, 4)" fill="url(#glass_white___UID__)"/>
  <ellipse cx="104" cy="130" rx="12" ry="14" fill="#4752C4"/>
  <ellipse cx="152" cy="130" rx="12" ry="14" fill="#4752C4"/>
""",
    },
    {
        "id": "code",
        "colors": ("#00B4D8", "#0077B6", "#03045E", "#90E0EF"),
        "aliases": [
            "code",
            "com.visualstudio.code",
            "org.kde.kate",
            "kate",
            "accessories-text-editor",
            "utilities-text-editor",
        ],
        "glyph": """
  <path d="M 70,96 L 156,182 L 184,168 L 184,88 L 156,74 L 70,160 L 56,146 L 56,110 Z"
        fill="url(#glass_sub___UID__)"/>
  <path d="M 156,74 L 184,88 L 184,168 L 156,182 L 156,74 Z" fill="url(#glass_white___UID__)"/>
  <path d="M 70,160 L 156,74 L 184,88 L 86,174 Z" fill="url(#glass_white___UID__)"/>
""",
    },
    {
        "id": "photos",
        "colors": ("#F8FAFC", "#E2E8F0", "#CBD5E1", "#FFFFFF"),
        "aliases": [
            "org.kde.gwenview",
            "gwenview",
            "multimedia-photo-viewer",
            "org.gnome.Loupe",
        ],
        "glyph": """
  <g transform="translate(128,128)">
    <rect x="-17" y="-72" width="34" height="60" rx="17" fill="#FF3B30" fill-opacity="0.86"/>
    <rect x="-17" y="-72" width="34" height="60" rx="17" transform="rotate(45)" fill="#FF9500" fill-opacity="0.86"/>
    <rect x="-17" y="-72" width="34" height="60" rx="17" transform="rotate(90)" fill="#FFCC00" fill-opacity="0.86"/>
    <rect x="-17" y="-72" width="34" height="60" rx="17" transform="rotate(135)" fill="#34C759" fill-opacity="0.86"/>
    <rect x="-17" y="-72" width="34" height="60" rx="17" transform="rotate(180)" fill="#00C7BE" fill-opacity="0.86"/>
    <rect x="-17" y="-72" width="34" height="60" rx="17" transform="rotate(225)" fill="#007AFF" fill-opacity="0.86"/>
    <rect x="-17" y="-72" width="34" height="60" rx="17" transform="rotate(270)" fill="#5856D6" fill-opacity="0.86"/>
    <rect x="-17" y="-72" width="34" height="60" rx="17" transform="rotate(315)" fill="#AF52DE" fill-opacity="0.86"/>
    <circle cx="0" cy="0" r="18" fill="#FFFFFF"/>
  </g>
""",
    },
    {
        "id": "videos",
        "colors": ("#FF7B00", "#E83800", "#7A0C00", "#FFAA00"),
        "aliases": [
            "org.videolan.VLC",
            "vlc",
            "io.mpv.Mpv",
            "mpv",
            "org.kde.haruna",
            "dragonplayer",
            "multimedia-video-player",
        ],
        "glyph": """
  <circle cx="128" cy="128" r="64" fill="url(#glass_sub___UID__)"/>
  <circle cx="128" cy="128" r="52" fill="#431407" fill-opacity="0.65"/>
  <path d="M 108,94 L 166,128 L 108,162 Z" fill="url(#glass_white___UID__)"/>
""",
    },
    {
        "id": "obs",
        "colors": ("#2B303C", "#161920", "#090B0E", "#94A3B8"),
        "aliases": [
            "com.obsproject.Studio",
            "obs",
            "obs-studio",
        ],
        "glyph": """
  <circle cx="128" cy="128" r="68" fill="#0B0D12" fill-opacity="0.68" stroke="#FFFFFF" stroke-width="2" stroke-opacity="0.30"/>
  <g transform="translate(128,128)">
    <path d="M 0,-8 C 18,-44 58,-36 52,6 C 34,-12 12,-12 0,-8 Z" fill="url(#glass_white___UID__)"/>
    <path d="M 0,-8 C 18,-44 58,-36 52,6 C 34,-12 12,-12 0,-8 Z" transform="rotate(120)" fill="url(#glass_white___UID__)"/>
    <path d="M 0,-8 C 18,-44 58,-36 52,6 C 34,-12 12,-12 0,-8 Z" transform="rotate(240)" fill="url(#glass_white___UID__)"/>
    <circle cx="0" cy="0" r="10" fill="url(#glass_white___UID__)"/>
  </g>
""",
    },
    {
        "id": "sysmonitor",
        "colors": ("#10B981", "#059669", "#064E3B", "#6EE7B7"),
        "aliases": [
            "org.kde.plasma-systemmonitor",
            "utilities-system-monitor",
            "ksysguard",
            "htop",
            "btop",
        ],
        "glyph": """
  <rect x="46" y="54" width="164" height="148" rx="28" fill="#03261B" fill-opacity="0.68"
        stroke="#6EE7B7" stroke-width="1.5" stroke-opacity="0.30"/>
  <line x1="64" y1="102" x2="192" y2="102" stroke="#6EE7B7" stroke-width="1" stroke-opacity="0.22"/>
  <line x1="64" y1="128" x2="192" y2="128" stroke="#6EE7B7" stroke-width="1" stroke-opacity="0.22"/>
  <line x1="64" y1="154" x2="192" y2="154" stroke="#6EE7B7" stroke-width="1" stroke-opacity="0.22"/>
  <path d="M 58,136 L 90,136 L 106,92 L 126,166 L 146,112 L 162,136 L 198,136"
        fill="none" stroke="url(#glass_white___UID__)" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
]


FOLDER_BADGES = {
    "folder": (
        "Default Folder",
        ["folder", "inode-directory", "folder-blue"],
        "",
    ),
    "user-home": (
        "Home",
        ["user-home", "folder-home"],
        """<path d="M 96,154 L 128,126 L 160,154 M 106,148 L 106,178 L 150,178 L 150,148"
                 fill="none" stroke="url(#folder_badge)" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/>""",
    ),
    "folder-download": (
        "Downloads",
        ["folder-download", "folder-downloads"],
        """<path d="M 128,122 L 128,166 M 108,148 L 128,168 L 148,148 M 102,180 L 154,180"
                 fill="none" stroke="url(#folder_badge)" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/>""",
    ),
    "user-desktop": (
        "Desktop",
        ["user-desktop", "folder-desktop"],
        """<rect x="98" y="126" width="60" height="42" rx="7" fill="none" stroke="url(#folder_badge)" stroke-width="7"/>
           <line x1="114" y1="180" x2="142" y2="180" stroke="url(#folder_badge)" stroke-width="7" stroke-linecap="round"/>""",
    ),
    "folder-documents": (
        "Documents",
        ["folder-documents", "folder-text"],
        """<rect x="106" y="122" width="44" height="58" rx="6" fill="none" stroke="url(#folder_badge)" stroke-width="7"/>
           <line x1="116" y1="140" x2="140" y2="140" stroke="url(#folder_badge)" stroke-width="6" stroke-linecap="round"/>
           <line x1="116" y1="156" x2="134" y2="156" stroke="url(#folder_badge)" stroke-width="6" stroke-linecap="round"/>""",
    ),
    "folder-pictures": (
        "Pictures",
        ["folder-pictures", "folder-images"],
        """<rect x="98" y="124" width="60" height="52" rx="8" fill="none" stroke="url(#folder_badge)" stroke-width="7"/>
           <circle cx="114" cy="140" r="5" fill="url(#folder_badge)"/>
           <path d="M 102,170 L 122,150 L 136,162 L 146,152 L 154,170" fill="none" stroke="url(#folder_badge)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>""",
    ),
    "folder-music": (
        "Music",
        ["folder-music", "folder-sound"],
        """<path d="M 118,166 L 118,130 L 148,124 L 148,160" fill="none" stroke="url(#folder_badge)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
           <circle cx="112" cy="166" r="8" fill="url(#folder_badge)"/>
           <circle cx="142" cy="160" r="8" fill="url(#folder_badge)"/>""",
    ),
    "folder-videos": (
        "Videos",
        ["folder-videos", "folder-video"],
        """<polygon points="114,126 150,150 114,174" fill="url(#folder_badge)"/>""",
    ),
    "folder-publicshare": (
        "Shared",
        ["folder-publicshare", "folder-remote", "folder-cloud"],
        """<path d="M 106,166 C 96,166 92,154 100,146 C 102,130 124,126 132,138 C 144,134 158,144 154,158 C 152,164 146,166 140,166 Z"
                 fill="none" stroke="url(#folder_badge)" stroke-width="7" stroke-linejoin="round"/>""",
    ),
    "folder-games": (
        "Games",
        ["folder-games"],
        """<rect x="98" y="134" width="60" height="36" rx="16" fill="none" stroke="url(#folder_badge)" stroke-width="7"/>
           <line x1="114" y1="146" x2="114" y2="158" stroke="url(#folder_badge)" stroke-width="5.5" stroke-linecap="round"/>
           <line x1="108" y1="152" x2="120" y2="152" stroke="url(#folder_badge)" stroke-width="5.5" stroke-linecap="round"/>
           <circle cx="142" cy="148" r="4" fill="url(#folder_badge)"/>
           <circle cx="148" cy="156" r="4" fill="url(#folder_badge)"/>""",
    ),
}


def make_macos_sky_folder_svg(folder_id: str, badge_svg: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <defs>
    <linearGradient id="tab_{folder_id}" x1="50%" y1="10%" x2="50%" y2="85%">
      <stop offset="0%" stop-color="#38A1FF"/>
      <stop offset="100%" stop-color="#1463D6"/>
    </linearGradient>
    <linearGradient id="front_{folder_id}" x1="50%" y1="25%" x2="50%" y2="98%">
      <stop offset="0%" stop-color="#8CE0FF"/>
      <stop offset="35%" stop-color="#58BFFF"/>
      <stop offset="82%" stop-color="#2693F8"/>
      <stop offset="100%" stop-color="#1577E6"/>
    </linearGradient>
    <radialGradient id="glow_{folder_id}" cx="50%" cy="95%" r="58%">
      <stop offset="0%" stop-color="#B8F2FF" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="#58BFFF" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="rim_{folder_id}" x1="15%" y1="25%" x2="85%" y2="95%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="35%" stop-color="#FFFFFF" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#BAE6FD" stop-opacity="0.75"/>
    </linearGradient>
    <linearGradient id="folder_badge" x1="50%" y1="20%" x2="50%" y2="90%">
      <stop offset="0%" stop-color="#09479E" stop-opacity="0.78"/>
      <stop offset="100%" stop-color="#063275" stop-opacity="0.92"/>
    </linearGradient>
  </defs>

  <rect x="20" y="64" width="216" height="156" rx="28" fill="#061A38" fill-opacity="0.22"/>
  <rect x="24" y="60" width="208" height="156" rx="26" fill="#061A38" fill-opacity="0.16"/>

  <path d="M 24,68 C 24,52 36,40 52,40 L 94,40 C 106,40 113,45 120,54 L 128,64 L 204,64 C 220,64 232,76 232,92 L 232,186 C 232,202 220,214 204,214 L 52,214 C 36,214 24,202 24,186 Z"
        fill="url(#tab_{folder_id})" stroke="#7DD3FC" stroke-width="1.5"/>

  <rect x="38" y="70" width="180" height="44" rx="12" fill="#FFFFFF" fill-opacity="0.90"/>

  <rect x="22" y="82" width="212" height="132" rx="26" fill="url(#front_{folder_id})"/>
  <rect x="22" y="82" width="212" height="132" rx="26" fill="url(#glow_{folder_id})"/>

  <line x1="42" y1="92" x2="214" y2="92" stroke="#FFFFFF" stroke-width="2.5" stroke-opacity="0.72" stroke-linecap="round"/>
  <rect x="22" y="82" width="212" height="132" rx="26" fill="none" stroke="url(#rim_{folder_id})" stroke-width="2.4"/>

  <g transform="translate(0, 2)" opacity="0.50">
    {badge_svg.replace('url(#folder_badge)', '#FFFFFF')}
  </g>
  {badge_svg}
</svg>
"""


INDEX_THEME = """[Icon Theme]
Name=HoussamOS Liquid Glass
Comment=Studio 3D Liquid Glass icons for HoussamOS. Smooth Bezier squircles, 3D specular bevels, and sky-blue glass folders.
Inherits=Tela-dark,breeze-dark,breeze,hicolor
Example=folder
Directories=scalable/apps,scalable/places

[scalable/apps]
Size=128
MinSize=16
MaxSize=512
Scale=1
Context=Applications
Type=Scalable

[scalable/places]
Size=128
MinSize=16
MaxSize=512
Scale=1
Context=Places
Type=Scalable
"""


def write_svg_with_aliases(target_dir: Path, primary: str, aliases: list[str], svg_text: str) -> int:
    ET.fromstring(svg_text)
    target_dir.mkdir(parents=True, exist_ok=True)
    names = {primary, *aliases}
    for name in sorted(names):
        (target_dir / f"{name}.svg").write_text(svg_text.strip() + "\n", encoding="utf-8", newline="\n")
    return len(names)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.theme").write_text(INDEX_THEME, encoding="utf-8", newline="\n")

    apps_dir = OUT / "scalable" / "apps"
    places_dir = OUT / "scalable" / "places"

    total = 0
    for app in APP_ICONS:
        c_top, c_mid, c_bot, c_glow = app["colors"]
        svg = make_liquid_glass_squircle(app["id"], c_top, c_mid, c_bot, c_glow, app["glyph"])
        total += write_svg_with_aliases(apps_dir, app["id"], app["aliases"], svg)

    for folder_id, (_, aliases, badge_svg) in FOLDER_BADGES.items():
        svg = make_macos_sky_folder_svg(folder_id, badge_svg)
        total += write_svg_with_aliases(places_dir, folder_id, aliases, svg)

    print(f"generated {total} icons into {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
