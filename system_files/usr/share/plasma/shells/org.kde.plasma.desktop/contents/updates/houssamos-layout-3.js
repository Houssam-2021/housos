// HoussamOS layout, third version: remove Bazzite Portal (pinned by Bazzite's bazzite-pins.js)
// from the dock and application launcher on existing desktops. Plasma runs each update script
// once per user, per file name.

function withoutPortal(value) {
    var items = Array.isArray(value) ? value : String(value).split(",");
    var kept = [];
    for (var i = 0; i < items.length; i++) {
        var item = String(items[i]).trim();
        if (item && item.indexOf("bazzite-portal") === -1) {
            kept.push(item);
        }
    }
    return Array.isArray(value) ? kept : kept.join(",");
}

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    var widgets = allPanels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        var w = widgets[j];
        if (w.type === "org.kde.plasma.icontasks" || w.type === "org.kde.plasma.taskmanager") {
            w.currentConfigGroup = ["General"];
            var launchers = w.readConfig("launchers", "");
            if (launchers && String(launchers).indexOf("bazzite-portal") !== -1) {
                w.writeConfig("launchers", withoutPortal(launchers));
            }
        } else if (w.type === "org.kde.plasma.kickoff") {
            w.currentConfigGroup = ["General"];
            var favs = w.readConfig("favorites", "");
            if (favs && String(favs).indexOf("bazzite-portal") !== -1) {
                w.writeConfig("favorites", withoutPortal(favs));
            }
        }
    }
}
