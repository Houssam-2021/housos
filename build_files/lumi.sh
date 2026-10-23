#!/bin/bash
# Lumi, the HoussamOS assistant (Houssam's own app, private repo Houssam-2021/Lumi): installed from
# its pinned release into /usr/lib/lumi, started at login, Meta+L brings it up.
# The release is private, so the build gets a read-only token as the build secret "lumi_token"
# (repo secret LUMI_RELEASE_TOKEN). Without it the image is built without Lumi.
set -euo pipefail

LUMI_VERSION=v3.5.0        # bump here to ship a new Lumi release
TARBALL=Lumi-Linux-x86_64.tar.gz
SUMS=SHA256SUMS-linux.txt
API=https://api.github.com/repos/Houssam-2021/Lumi

token=""
if [ -s /run/secrets/lumi_token ]; then
    token=$(cat /run/secrets/lumi_token)
fi
if [ -z "$token" ]; then
    echo "::warning title=Lumi not installed::No LUMI_RELEASE_TOKEN secret; the image is built without Lumi"
    exit 0
fi

work=$(mktemp -d)
gh() { curl -fsSL --retry 3 -H "Authorization: Bearer $token" "$@"; }
gh -H "Accept: application/vnd.github+json" "$API/releases/tags/$LUMI_VERSION" > "$work/release.json"
asset_url() {
    python3 -c 'import json, sys
for a in json.load(open(sys.argv[1]))["assets"]:
    if a["name"] == sys.argv[2]:
        print(a["url"])' "$work/release.json" "$1"
}
for name in "$TARBALL" "$SUMS"; do
    url=$(asset_url "$name")
    if [ -z "$url" ]; then
        echo "::error title=Lumi release incomplete::$name is missing from Lumi $LUMI_VERSION"
        exit 1
    fi
    gh -H "Accept: application/octet-stream" -o "$work/$name" "$url"
done
(cd "$work" && grep -E "[[:space:]]\*?$TARBALL\$" "$SUMS" | sha256sum -c -)

tar -xzf "$work/$TARBALL" -C "$work"
src="$work/Lumi-Linux"
if [ ! -x "$src/lumi/lumi" ]; then
    echo "::error title=Lumi tarball layout changed::Lumi-Linux/lumi/lumi not found in $TARBALL"
    exit 1
fi
rm -rf /usr/lib/lumi
mkdir -p /usr/lib/lumi
cp -a "$src/lumi/." /usr/lib/lumi/
ln -sf /usr/lib/lumi/lumi /usr/bin/lumi
install -Dm644 "$src/lumi.png" /usr/share/icons/hicolor/256x256/apps/lumi.png

# App menu entry, autostart (its first launch is the HoussamOS welcome), and Meta+L
desktop=/usr/share/houssamos/lumi/lumi.desktop
install -Dm644 "$desktop" /usr/share/applications/lumi.desktop
install -Dm644 "$desktop" /usr/share/kglobalaccel/lumi.desktop
install -Dm644 /usr/share/houssamos/lumi/lumi-autostart.desktop /etc/xdg/autostart/lumi.desktop
# Meta+L locks the screen in KDE; it goes to Lumi, and locking moves to Ctrl+Alt+L
tab=$'\t'
mkdir -p /etc/xdg
cat >> /etc/xdg/kglobalshortcutsrc <<EOF

[ksmserver]
Lock Session=Ctrl+Alt+L${tab}Screensaver,Ctrl+Alt+L${tab}Screensaver,Lock Session
EOF
rm -rf "$work"
echo "Lumi $LUMI_VERSION installed"
