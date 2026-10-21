// HoussamOS layout, sixth version: the Control Center button (org.houssamos.controlcenter) at
// the right end of the top bar, after the system tray, as on macOS.
// Plasma runs each update script once per user, per file name.

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    var panel = allPanels[i];
    if (panel.location !== "top") {
        continue;
    }
    var hasControlCenter = false;
    var widgets = panel.widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type === "org.houssamos.controlcenter") {
            hasControlCenter = true;
        }
    }
    if (!hasControlCenter) {
        panel.addWidget("org.houssamos.controlcenter");
    }
}
