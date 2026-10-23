import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property var games: []
    readonly property string script: Qt.resolvedUrl("../code/recent.py").toString().replace("file://", "")

    Shell { id: shell }
    Timer {
        interval: 5 * 60 * 1000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: shell.exec("python3 '" + root.script + "'", (out, code) => {
            try { root.games = JSON.parse(out); } catch (e) { root.games = []; }
        })
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 13
        PlasmaComponents.Label { text: "Recently played"; font.weight: Font.DemiBold; font.pixelSize: Kirigami.Units.gridUnit * 1.2 }
        PlasmaComponents.Label { visible: root.games.length === 0; text: "No Steam games yet"; opacity: 0.7 }
        Repeater {
            model: root.games
            PlasmaComponents.ItemDelegate {
                required property var modelData
                Layout.fillWidth: true
                icon.name: "steam_icon_" + modelData.appid
                text: modelData.name
                onClicked: shell.exec("steam steam://rungameid/" + modelData.appid, () => {})
            }
        }
        Item { Layout.fillHeight: true }
    }
}
