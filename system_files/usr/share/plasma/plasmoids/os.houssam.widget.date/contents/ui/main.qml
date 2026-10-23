import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property date now: new Date()
    Timer { interval: 60000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.now = new Date() }

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 15
        Layout.preferredHeight: Kirigami.Units.gridUnit * 6
        spacing: Kirigami.Units.largeSpacing * 2
        Text {
            text: Qt.formatDate(root.now, "d")
            color: Kirigami.Theme.highlightColor
            font.pixelSize: Kirigami.Units.gridUnit * 4
            font.weight: Font.DemiBold
        }
        ColumnLayout {
            spacing: 0
            Text {
                text: Qt.formatDate(root.now, "dddd")
                color: Kirigami.Theme.textColor
                font.pixelSize: Kirigami.Units.gridUnit * 1.6
                font.weight: Font.DemiBold
            }
            PlasmaComponents.Label { text: Qt.formatDate(root.now, "MMMM yyyy"); opacity: 0.75 }
        }
    }
}
