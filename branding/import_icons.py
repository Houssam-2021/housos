#!/usr/bin/env python3
"""Import the HoussamOS Liquid Glass icon theme from its zip into system_files/.

The zip is untrusted input (AI generated), so it is never extracted as-is: only SVG icons,
index.theme and README.txt are taken, each SVG must parse and must not contain scripts,
event handlers, entities or links to outside files, and paths must stay inside the theme.

Then a few mistakes in the generated pack are fixed by pointing icons at better drawings
from the same pack (see FIXES).

Usage: python branding/import_icons.py path/to/HoussamOS-LiquidGlass.zip
"""
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
THEME = "HoussamOS-LiquidGlass"
OUT = ROOT / "system_files" / "usr/share/icons" / THEME

RISKY = re.compile(r"<script|<!ENTITY|<!DOCTYPE|javascript:|\son[a-z]+\s*=|<foreignObject"
                   r"|href\s*=\s*[\"'](?!#|data:image/)", re.I)

# (drawing to use, icons that should show it). "=name" means every icon drawn the same as name.
FIXES = [
    ("gearlever", ["=gnome-control-center"]),                  # the settings drawing is a blank tile
    ("file-manager", ["org.kde.dolphin", "dolphin"]),          # KDE's file manager, not the Dolphin emulator
    ("folder-games", ["net.lutris.Lutris", "lutris"]),         # tell Lutris apart from Steam in the dock
    ("audio-headset", ["audio-headphones", "multimedia-headphones"]),   # was a phone
]


def read_pack(zip_path):
    """Return {relative path: bytes} for the files we accept from the zip."""
    files = {}
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            if info.is_dir() or (info.external_attr >> 16) & 0o170000 == 0o120000:   # skip dirs, symlinks
                continue
            parts = PurePosixPath(info.filename.replace(chr(92), "/")).parts
            if parts and parts[0] == THEME:
                parts = parts[1:]
            if not parts or ".." in parts or parts[0].startswith("/") or ":" in parts[0]:
                raise SystemExit(f"unsafe path in zip: {info.filename}")
            rel = "/".join(parts)
            if rel in ("index.theme", "README.txt") or (rel.startswith("scalable/") and rel.endswith(".svg")):
                files[rel] = z.read(info)
    for rel, data in files.items():
        if rel.endswith(".svg"):
            text = data.decode("utf-8")
            if RISKY.search(text):
                raise SystemExit(f"unsafe content in {rel}")
            ET.fromstring(text)   # must be well-formed XML
    return files


def apply_fixes(files):
    by_name = {}
    for rel in files:
        if rel.endswith(".svg"):
            by_name.setdefault(PurePosixPath(rel).stem, []).append(rel)
    for source, targets in FIXES:
        drawing = files[by_name[source][0]]
        for target in targets:
            if target.startswith("="):
                same = files[by_name[target[1:]][0]]
                paths = [rel for rel, data in files.items() if data == same]
            else:
                paths = by_name.get(target, [])
            for rel in paths:
                files[rel] = drawing
            print(f"fix: {target} -> {source} ({len(paths)} icons)")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    files = read_pack(sys.argv[1])
    if "index.theme" not in files:
        raise SystemExit("index.theme missing from the pack")
    apply_fixes(files)
    if OUT.exists():
        shutil.rmtree(OUT)
    for rel, data in files.items():
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    count = sum(rel.endswith(".svg") for rel in files)
    print(f"imported {count} icons into {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
