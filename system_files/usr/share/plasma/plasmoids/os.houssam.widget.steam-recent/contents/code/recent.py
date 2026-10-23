#!/usr/bin/python3
"""Prints the 5 Steam games played most recently as JSON (for the steam-recent widget)."""
import glob, json, os, re
home = os.path.expanduser("~")
roots = [os.path.join(home, ".local/share/Steam"), os.path.join(home, ".steam/steam"),
         os.path.join(home, ".var/app/com.valvesoftware.Steam/.local/share/Steam")]
libraries = set()
for root in roots:
    vdf = os.path.join(root, "steamapps/libraryfolders.vdf")
    if os.path.isfile(vdf):
        libraries.add(os.path.join(root, "steamapps"))
        for path in re.findall(r'"path"\s+"([^"]+)"', open(vdf, encoding="utf-8", errors="replace").read()):
            libraries.add(os.path.join(path.replace("\\\\", "/"), "steamapps"))
games = {}
for lib in libraries:
    for acf in glob.glob(os.path.join(lib, "appmanifest_*.acf")):
        text = open(acf, encoding="utf-8", errors="replace").read()
        get = lambda key: (re.search(r'"%s"\s+"([^"]*)"' % key, text) or [None, ""])[1]
        appid, name = get("appid"), get("name")
        if appid and name and "Proton" not in name and "Steam Linux Runtime" not in name and "Steamworks" not in name:
            games[appid] = {"appid": appid, "name": name, "played": int(get("LastPlayed") or 0)}
print(json.dumps(sorted(games.values(), key=lambda g: -g["played"])[:5]))
