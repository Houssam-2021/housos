# HoussamOS

A gaming-ready Linux desktop for everyday users, built on [Bazzite](https://bazzite.gg)
(Fedora Atomic + KDE Plasma) using the Universal Blue image template.

## How it is built

- `Containerfile` + `build_files/build.sh` define the OS image.
- GitHub Actions (`build.yml`) builds it every day and on every push, and publishes it to
  `ghcr.io/houssam-2021/houssamos`.
- `build-disk.yml` (run manually from the Actions tab) turns the image into an installable ISO.
- Installed systems update themselves from that image and can roll back to the previous version.

## Roadmap

1. Base image with HoussamOS branding
2. Visual identity: logo, boot animation, login screen, theme
3. Undo timeline (snapshots before every change)
4. Gaming extras: "Will my games work?" checker, automatic game mode
5. Privacy report
6. Offline AI assistant
7. Guest mode

## Image signing

Signing is skipped until a `SIGNING_SECRET` repository secret exists. See the
[Universal Blue template docs](https://github.com/ublue-os/image-template#container-signing).
