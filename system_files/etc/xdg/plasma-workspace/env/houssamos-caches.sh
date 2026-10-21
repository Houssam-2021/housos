# HoussamOS: after an update, clear KDE's caches of icons, theme pictures and compiled QML.
# In an image-based system every file carries the same timestamp, so KDE can't tell that they
# changed and would keep showing the old ones. Plasma runs this at login, before it starts.

houssamos_build=/usr/share/houssamos/build-id
houssamos_cache="${XDG_CACHE_HOME:-$HOME/.cache}"
if [ -r "$houssamos_build" ] && ! cmp -s "$houssamos_build" "$houssamos_cache/houssamos-build-id"; then
    rm -f "$houssamos_cache"/icon-cache.kcache "$houssamos_cache"/plasma_theme_*.kcache \
        "$houssamos_cache"/plasma-svgelements* "$houssamos_cache"/ksvg-elements*
    rm -rf "$houssamos_cache"/qmlcache "$houssamos_cache"/*/qmlcache
    mkdir -p "$houssamos_cache"
    cp "$houssamos_build" "$houssamos_cache/houssamos-build-id"
fi
unset houssamos_build houssamos_cache
