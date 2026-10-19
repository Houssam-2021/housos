#!/bin/bash

set -ouex pipefail

# Copy the contents of system_files/ of the git repo to /
cp -avf "/ctx/system_files"/. /

### HoussamOS branding
# Only change what users see. ID/ID_LIKE stay Bazzite's so its update and setup tools keep working.
sed -i \
    -e 's/^NAME=.*/NAME="HoussamOS"/' \
    -e 's/^PRETTY_NAME=.*/PRETTY_NAME="HoussamOS"/' \
    /usr/lib/os-release
if grep -q '^DEFAULT_HOSTNAME=' /usr/lib/os-release; then
    sed -i 's/^DEFAULT_HOSTNAME=.*/DEFAULT_HOSTNAME="houssamos"/' /usr/lib/os-release
else
    echo 'DEFAULT_HOSTNAME="houssamos"' >> /usr/lib/os-release
fi

### Install packages
# Packages can be installed from any enabled repo on the image (Fedora, RPM Fusion).
# dnf5 install -y <package>

### Repository cleanup
# bootc-image-builder reads /etc/yum.repos.d directly when it builds the installer ISO.
# It ignores dnf5's repos.override.d (where Bazzite turns repos off with
# "config-manager setopt") and fails on any enabled repo whose GPG key file is missing.

# Turn off one repo id in whichever .repo file defines it
disable_repo() {
    local id="$1" f
    for f in /etc/yum.repos.d/*.repo; do
        grep -qF "[${id}]" "$f" || continue
        sed -i -e "/^\[${id}\]/,/^\[/{/^enabled[[:space:]]*=/d}" -e "/^\[${id}\]/a enabled=0" "$f"
        echo "Disabled repo ${id} in ${f}"
    done
}

# Copy repos that dnf5 overrides turned off into the .repo files
if compgen -G "/etc/dnf/repos.override.d/*.repo" > /dev/null; then
    awk '/^\[[^]]+\]/ { id = substr($0, 2, index($0, "]") - 2) }
         /^enabled[[:space:]]*=[[:space:]]*(0|false|no)[[:space:]]*$/ { print id }' \
        /etc/dnf/repos.override.d/*.repo | sort -u | while read -r id; do
        [[ "$id" == *[*?]* ]] && continue
        disable_repo "$id"
    done
fi

# Turn off enabled repos whose local GPG key file does not exist (they cannot work anyway)
releasever=$(rpm -E %fedora)
basearch=$(uname -m)
awk -v rv="$releasever" -v ba="$basearch" '
    function keys(   n, i, a, k) {
        n = split($0, a, /[[:space:],]+/)
        for (i = 1; i <= n; i++) if (a[i] ~ /^file:\/\//) {
            k = substr(a[i], 8)
            gsub(/\$\{?releasever\}?/, rv, k)
            gsub(/\$\{?basearch\}?/, ba, k)
            print id, k
        }
    }
    /^\[[^]]+\]/ { id = substr($0, 2, index($0, "]") - 2); inkey = 0; next }
    /^gpgkey[[:space:]]*=/ { inkey = 1; sub(/^gpgkey[[:space:]]*=/, ""); keys(); next }
    inkey && /^[[:space:]]+[^[:space:]]/ { keys(); next }
    { inkey = 0 }
' /etc/yum.repos.d/*.repo | while read -r id key; do
    if [ ! -f "$key" ]; then
        echo "Repo ${id} needs missing key ${key}"
        disable_repo "$id"
    fi
done
