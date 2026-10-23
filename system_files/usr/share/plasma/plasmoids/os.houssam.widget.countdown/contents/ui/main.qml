import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property date now: new Date()
    readonly property date target: new Date(Plasmoid.configuration.target)
    readonly property real left: Math.max(0, target - now)
    Timer { interval: 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.now = new Date() }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 7
        spacing: 0
        PlasmaComponents.Label { text: Plasmoid.configuration.label; opacity: 0.75 }
        Text {
            text: isNaN(root.target) ? "Set a date" : Math.floor(root.left / 86400000) + " days"
            color: Kirigami.Theme.highlightColor
            font.pixelSize: Kirigami.Units.gridUnit * 3
            font.weight: Font.DemiBold
        }
        PlasmaComponents.Label {
            visible: !isNaN(root.target)
            text: root.left === 0 ? "It's here! 🎉" : Math.floor(root.left / 3600000) % 24 + " h " + Math.floor(root.left / 60000) % 60 + " min " + Math.floor(root.left / 1000) % 60 + " s"
            opacity: 0.7
        }
    }
}
