import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

import org.kde.ksysguard.sensors as Sensors

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Sensors.Sensor { id: down; sensorId: "network/all/download"; updateRateLimit: 1000 }
    Sensors.Sensor { id: up; sensorId: "network/all/upload"; updateRateLimit: 1000 }

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 5
        spacing: Kirigami.Units.largeSpacing * 3
        Repeater {
            model: [["↓", "Download", down], ["↑", "Upload", up]]
            delegate: ColumnLayout {
                id: rate
                required property var modelData
                required property int index
                spacing: 0
                Text {
                    text: rate.modelData[0] + " " + (rate.modelData[2].formattedValue || "--")
                    color: rate.index === 0 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    font.pixelSize: Kirigami.Units.gridUnit * 1.5
                    font.weight: Font.DemiBold
                }
                PlasmaComponents.Label { text: rate.modelData[1]; opacity: 0.7 }
            }
        }
    }
}
