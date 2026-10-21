// HoussamOS layout: a thin top bar (app menu, clock, system tray) and a floating glass dock at
// the bottom that holds only apps and grows as apps are pinned or opened.
// Plasma runs each update script once per user, so this also converts existing desktops.

var allPanels = panels();
var dock = null;
var hasTopBar = false;
for (var i = 0; i < allPanels.length; i++) {
    if (allPanels[i].location === "bottom" && dock === null) {
        dock = allPanels[i];
    } else if (allPanels[i].location === "top") {
        hasTopBar = true;
    }
}

if (dock === null) {
    dock = new Panel;
    dock.location = "bottom";
}

// Keep only the app icons in the dock; the menu, clock and tray move to the top bar
var hasTasks = false;
var dockWidgets = dock.widgets();
for (var j = 0; j < dockWidgets.length; j++) {
    var type = dockWidgets[j].type;
    if (type === "org.kde.plasma.icontasks" || type === "org.kde.plasma.taskmanager") {
        hasTasks = true;
    } else {
        dockWidgets[j].remove();
    }
}
if (!hasTasks) {
    dock.addWidget("org.kde.plasma.icontasks");
}

dock.height = 64;              // matches DOCK_HEIGHT in branding/make_theme.py
dock.floating = true;
dock.alignment = "center";
dock.lengthMode = "fit";       // the glass stretches with the number of apps
dock.hiding = "none";

if (!hasTopBar) {
    var bar = new Panel;
    bar.location = "top";
    bar.height = 30;
    bar.floating = false;
    bar.lengthMode = "fill";

    var menu = bar.addWidget("org.kde.plasma.kickoff");
    menu.currentConfigGroup = ["General"];
    menu.writeConfig("icon", "houssamos-logo");

    bar.addWidget("org.kde.plasma.panelspacer");
    bar.addWidget("org.kde.plasma.digitalclock");
    bar.addWidget("org.kde.plasma.panelspacer");
    bar.addWidget("org.kde.plasma.systemtray");
}
