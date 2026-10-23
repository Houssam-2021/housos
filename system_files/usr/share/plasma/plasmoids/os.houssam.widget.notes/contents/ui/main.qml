import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Timer { id: save; interval: 800; onTriggered: Plasmoid.configuration.text = area.text }

    fullRepresentation: PlasmaComponents.ScrollView {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 12
        PlasmaComponents.TextArea {
            id: area
            text: Plasmoid.configuration.text
            placeholderText: "Write a note..."
            wrapMode: TextEdit.Wrap
            background: null
            onTextChanged: save.restart()
        }
    }
}
