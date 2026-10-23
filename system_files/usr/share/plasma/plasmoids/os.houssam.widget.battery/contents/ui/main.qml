import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property int percent: -1
    property string status: ""

    Shell { id: shell }
    Timer {
        interval: 30000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: shell.exec("sh -c 'for b in /sys/class/power_supply/BAT*; do [ -e \"$b/capacity\" ] && cat \"$b/capacity\" \"$b/status\" && break; done'", (out, code) => {
            const lines = out.trim().split("\n");
            root.percent = lines.length >= 2 ? parseInt(lines[0]) : -1;
            root.status = lines.length >= 2 ? lines[1] : "";
        })
    }

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 14
        Layout.preferredHeight: Kirigami.Units.gridUnit * 5
        spacing: Kirigami.Units.largeSpacing * 2
        Kirigami.Icon {
            Layout.preferredWidth: Kirigami.Units.iconSizes.large
            Layout.preferredHeight: Kirigami.Units.iconSizes.large
            source: root.percent < 0 ? "battery-missing" : (root.status === "Charging" ? "battery-charging" : (root.percent > 60 ? "battery-good" : (root.percent > 20 ? "battery-low" : "battery-caution")))
        }
        ColumnLayout {
            spacing: 0
            Text {
                text: root.percent < 0 ? "No battery" : root.percent + " %"
                color: root.percent >= 0 && root.percent <= 15 ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.textColor
                font.pixelSize: Kirigami.Units.gridUnit * 2
                font.weight: Font.DemiBold
            }
            PlasmaComponents.Label { text: root.percent < 0 ? "This PC runs on mains power" : root.status; opacity: 0.7 }
        }
    }
}
