// HoussamOS layout, second version: the redesigned glass dock is slimmer (64 px) and the top bar
// 30 px. Plasma runs each update script once per user, so this resizes desktops that already ran
// houssamos-layout.js with the earlier sizes; for new accounts it changes nothing.

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    var panel = allPanels[i];
    if (panel.location === "bottom") {
        panel.height = 64;         // matches DOCK_HEIGHT in branding/make_theme.py
        panel.floating = true;
        panel.alignment = "center";
        panel.lengthMode = "fit";
    } else if (panel.location === "top") {
        panel.height = 30;         // matches TOPBAR_HEIGHT in branding/make_theme.py
    }
}
