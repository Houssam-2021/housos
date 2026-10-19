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
