import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

import org.kde.ksysguard.sensors as Sensors

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Sensors.Sensor { id: used; sensorId: "disk/all/usedPercent"; updateRateLimit: 5000 }
    Sensors.Sensor { id: free; sensorId: "disk/all/free"; updateRateLimit: 5000 }
    Sensors.Sensor { id: readRate; sensorId: "disk/all/read"; updateRateLimit: 1500 }
    Sensors.Sensor { id: writeRate; sensorId: "disk/all/write"; updateRateLimit: 1500 }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 6
        spacing: Kirigami.Units.largeSpacing
        Meter { Layout.fillWidth: true; label: "Disk"; valueText: (free.formattedValue || "--") + " free"; fraction: (used.value || 0) / 100 }
        RowLayout {
            Layout.fillWidth: true
            PlasmaComponents.Label { text: "Read " + (readRate.formattedValue || "--"); opacity: 0.75 }
            Item { Layout.fillWidth: true }
            PlasmaComponents.Label { text: "Write " + (writeRate.formattedValue || "--"); opacity: 0.75 }
        }
    }
}
