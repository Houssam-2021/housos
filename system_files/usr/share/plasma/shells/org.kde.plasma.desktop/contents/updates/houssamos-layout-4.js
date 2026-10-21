// HoussamOS layout, fourth version: take Bazzite's own tools out of the dock on existing
// desktops. Bazzite pins its welcome app, Bazzite Portal, as io.github.ublue_os.yafti_gtk.desktop
// (houssamos-layout-3.js looked for a name it doesn't have). Plasma runs each update script once
// per user, per file name.

var unwanted = /yafti|bazzite|ublue/i;

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    var widgets = allPanels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        var w = widgets[j];
        if (w.type !== "org.kde.plasma.icontasks" && w.type !== "org.kde.plasma.taskmanager") {
            continue;
        }
        w.currentConfigGroup = ["General"];
        var launchers = w.readConfig("launchers", "");
        var items = Array.isArray(launchers) ? launchers : String(launchers).split(",");
        var kept = [];
        var removed = false;
        for (var k = 0; k < items.length; k++) {
            var item = String(items[k]).trim();
            if (unwanted.test(item)) {
                removed = true;
            } else if (item) {
                kept.push(item);
            }
        }
        if (removed) {
            w.writeConfig("launchers", kept);
            w.reloadConfig();
        }
    }
}
