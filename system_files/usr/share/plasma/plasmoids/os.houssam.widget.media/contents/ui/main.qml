import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

import org.kde.plasma.private.mpris as Mpris

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Mpris.Mpris2Model { id: mpris }
    readonly property var player: mpris.currentPlayer
    readonly property bool playing: player ? player.playbackStatus === Mpris.PlaybackStatus.Playing : false

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 20
        Layout.preferredHeight: Kirigami.Units.gridUnit * 6
        spacing: Kirigami.Units.largeSpacing
        Rectangle {
            Layout.preferredWidth: Kirigami.Units.gridUnit * 5
            Layout.preferredHeight: Kirigami.Units.gridUnit * 5
            radius: 12
            clip: true
            color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.1)
            Image { anchors.fill: parent; source: root.player ? root.player.artUrl : ""; fillMode: Image.PreserveAspectCrop; visible: status === Image.Ready }
            Kirigami.Icon { anchors.centerIn: parent; width: parent.width / 2; height: width; source: "media-optical-audio"; visible: !root.player || !root.player.artUrl }
        }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            PlasmaComponents.Label { Layout.fillWidth: true; text: root.player && root.player.track ? root.player.track : "Nothing playing"; font.weight: Font.DemiBold; elide: Text.ElideRight }
            PlasmaComponents.Label { Layout.fillWidth: true; text: root.player ? root.player.artist : ""; opacity: 0.7; elide: Text.ElideRight }
            RowLayout {
                enabled: !!root.player
                PlasmaComponents.ToolButton { icon.name: "media-skip-backward"; onClicked: root.player.Previous() }
                PlasmaComponents.ToolButton { icon.name: root.playing ? "media-playback-pause" : "media-playback-start"; onClicked: root.playing ? root.player.Pause() : root.player.Play() }
                PlasmaComponents.ToolButton { icon.name: "media-skip-forward"; onClicked: root.player.Next() }
            }
        }
    }
}
