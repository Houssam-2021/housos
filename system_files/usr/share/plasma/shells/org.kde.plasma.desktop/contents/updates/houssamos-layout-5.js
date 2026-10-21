// HoussamOS layout, fifth version: the dock always floats and holds HoussamOS's own apps.
//
// Plasma stops a floating panel from floating whenever a window touches it, unless the panel
// hides; so the dock dodges windows: it stays a floating pane of blur, slides away when a window
// covers it, and comes back at the bottom edge of the screen.
// Bazzite pins its own picks (Lutris, its Bazaar store, its Portal); HoussamOS pins files, the
// browser, Steam, the terminal and settings, and those apps stay in the app menu.
// Plasma runs each update script once per user, per file name.

var pins = [
    "preferred://filemanager",
    "preferred://browser",
    "applications:steam.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:systemsettings.desktop"
];

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    var panel = allPanels[i];
    if (panel.location !== "bottom") {
        continue;
    }
    panel.floating = true;
    panel.hiding = "dodgewindows";

    var widgets = panel.widgets();
    for (var j = 0; j < widgets.length; j++) {
        var w = widgets[j];
        if (w.type === "org.kde.plasma.icontasks" || w.type === "org.kde.plasma.taskmanager") {
            w.currentConfigGroup = ["General"];
            w.writeConfig("launchers", pins);
            w.reloadConfig();
        }
    }
}
