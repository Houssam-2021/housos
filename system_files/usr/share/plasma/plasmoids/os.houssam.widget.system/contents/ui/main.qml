import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

import org.kde.ksysguard.sensors as Sensors

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation

    Sensors.Sensor { id: cpu; sensorId: "cpu/all/usage"; updateRateLimit: 1500 }
    Sensors.Sensor { id: ram; sensorId: "memory/physical/usedPercent"; updateRateLimit: 1500 }
    Sensors.Sensor { id: ramUsed; sensorId: "memory/physical/used"; updateRateLimit: 1500 }
    Sensors.Sensor { id: gpu; sensorId: "gpu/gpu1/usage"; updateRateLimit: 1500 }
    Sensors.Sensor { id: cpuTemp; sensorId: "cpu/all/averageTemperature"; updateRateLimit: 3000 }
    Sensors.Sensor { id: gpuTemp; sensorId: "gpu/gpu1/temperature"; updateRateLimit: 3000 }

    function has(s) { return s.value !== undefined && s.value !== null && s.formattedValue !== ""; }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 10
        spacing: Kirigami.Units.largeSpacing
        Meter { Layout.fillWidth: true; label: "CPU"; valueText: Math.round(cpu.value || 0) + " %"; fraction: (cpu.value || 0) / 100 }
        Meter { Layout.fillWidth: true; label: "Memory"; valueText: root.has(ramUsed) ? ramUsed.formattedValue : Math.round(ram.value || 0) + " %"; fraction: (ram.value || 0) / 100 }
        Meter { Layout.fillWidth: true; visible: root.has(gpu); label: "Graphics"; valueText: Math.round(gpu.value || 0) + " %"; fraction: (gpu.value || 0) / 100 }
        RowLayout {
            Layout.fillWidth: true
            visible: root.has(cpuTemp) || root.has(gpuTemp)
            PlasmaComponents.Label { text: "Temperatures"; opacity: 0.75 }
            Item { Layout.fillWidth: true }
            PlasmaComponents.Label {
                text: (root.has(cpuTemp) ? "CPU " + Math.round(cpuTemp.value) + "°" : "")
                    + (root.has(cpuTemp) && root.has(gpuTemp) ? "  ·  " : "")
                    + (root.has(gpuTemp) ? "GPU " + Math.round(gpuTemp.value) + "°" : "")
                font.weight: Font.DemiBold
            }
        }
    }
}
