import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

// The control center panel, laid out like macOS's: connections on the left, Do Not Disturb,
// screenshot and settings on the right, then display and sound sliders and what is playing.
// It sits in Plasma's popup, which already draws the HoussamOS glass with live blur behind it.
//
// Each connection to the system is a separate file in backends/, loaded on its own: if one
// can't load on a machine (no Bluetooth, no brightness control in a virtual machine), only its
// part hides or shows as unavailable.
Item {
    id: cc

    signal closeRequested()

    property string backends: Qt.resolvedUrl("backends/")
    readonly property var network: networkLoader.item
    readonly property var bluetooth: bluetoothLoader.item
    readonly property var notifications: notificationsLoader.item
    readonly property var volume: volumeLoader.item
    readonly property var brightness: brightnessLoader.item
    readonly property var media: mediaLoader.item
    readonly property var launcher: launcherLoader.item

    readonly property color textColor: "#f2f4f8"
    readonly property color dimColor: Qt.rgba(1, 1, 1, 0.6)

    function launch(command) {
        cc.closeRequested();
        pendingCommand.command = command;
        pendingCommand.restart();
    }

    implicitWidth: 372
    implicitHeight: column.implicitHeight + 20

    Loader { id: networkLoader; source: cc.backends + "Network.qml" }
    Loader { id: bluetoothLoader; source: cc.backends + "Bluetooth.qml" }
    Loader { id: notificationsLoader; source: cc.backends + "Notifications.qml" }
    Loader { id: volumeLoader; source: cc.backends + "Volume.qml" }
    Loader { id: brightnessLoader; source: cc.backends + "Brightness.qml" }
    Loader { id: mediaLoader; source: cc.backends + "Media.qml" }
    Loader { id: launcherLoader; source: cc.backends + "Launcher.qml" }

    // Programs start once the panel has closed, so a screenshot doesn't show it
    Timer {
        id: pendingCommand
        property string command
        interval: 300
        onTriggered: if (cc.launcher) cc.launcher.run(command)
    }

    ColumnLayout {
        id: column
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Tile {
                Layout.fillWidth: true
                Layout.preferredWidth: 1
                Layout.fillHeight: true
                implicitHeight: connections.implicitHeight + 24

                ColumnLayout {
                    id: connections
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 10

                    ToggleRow {
                        icon: "network-wireless-symbolic"
                        title: "Wi-Fi"
                        enabled: !!cc.network && cc.network.wifiAvailable && !cc.network.airplaneOn
                        checked: !!cc.network && cc.network.wifiOn && enabled
                        subtitle: !enabled ? "Unavailable" : (checked ? (cc.network.status || "On") : "Off")
                        onToggled: cc.network.setWifi(!cc.network.wifiOn)
                    }
                    ToggleRow {
                        icon: "network-bluetooth-symbolic"
                        title: "Bluetooth"
                        enabled: !!cc.bluetooth && cc.bluetooth.available
                        checked: enabled && cc.bluetooth.isOn
                        subtitle: !enabled ? "Unavailable"
                                 : !checked ? "Off"
                                 : cc.bluetooth.connectedDevices > 0 ? cc.bluetooth.connectedDevices + " connected" : "On"
                        onToggled: cc.bluetooth.setOn(!cc.bluetooth.isOn)
                    }
                    ToggleRow {
                        icon: "network-flightmode-on-symbolic"
                        title: "Airplane Mode"
                        enabled: !!cc.network
                        checked: enabled && cc.network.airplaneOn
                        subtitle: checked ? "On" : "Off"
                        onToggled: cc.network.setAirplane(!cc.network.airplaneOn)
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.preferredWidth: 1
                spacing: 10

                Tile {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    implicitHeight: dnd.implicitHeight + 24
                    active: !!cc.notifications && cc.notifications.doNotDisturb
                    clickable: !!cc.notifications
                    onClicked: cc.notifications.setDoNotDisturb(!cc.notifications.doNotDisturb)

                    ToggleRow {
                        id: dnd
                        anchors.fill: parent
                        anchors.margins: 12
                        icon: "notifications-disabled-symbolic"
                        title: "Do Not Disturb"
                        enabled: !!cc.notifications
                        checked: enabled && cc.notifications.doNotDisturb
                        subtitle: checked ? "On" : "Off"
                        onToggled: cc.notifications.setDoNotDisturb(!cc.notifications.doNotDisturb)
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Repeater {
                        model: [
                            { icon: "camera-photo-symbolic", label: "Screenshot", command: "spectacle --region" },
                            { icon: "configure-symbolic", label: "Settings", command: "systemsettings" },
                        ]

                        Tile {
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            implicitHeight: 72
                            clickable: !!cc.launcher
                            onClicked: cc.launch(modelData.command)

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 6

                                Kirigami.Icon {
                                    Layout.alignment: Qt.AlignHCenter
                                    implicitWidth: 20
                                    implicitHeight: 20
                                    source: modelData.icon
                                    isMask: true
                                    color: cc.textColor
                                }
                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.label
                                    color: cc.textColor
                                    font.pixelSize: 11
                                    font.weight: Font.Medium
                                }
                            }
                        }
                    }
                }
            }
        }

        // One brightness slider per screen that has one
        Repeater {
            model: cc.brightness && cc.brightness.available ? cc.brightness.displays : null

            Tile {
                id: displayTile
                required property string displayName
                required property string label
                required property int brightness
                required property int maxBrightness
                Layout.fillWidth: true
                implicitHeight: displayColumn.implicitHeight + 24

                ColumnLayout {
                    id: displayColumn
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    Text {
                        text: "Display"
                        color: cc.textColor
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                    }
                    GlassSlider {
                        Layout.fillWidth: true
                        icon: "brightness-high-symbolic"
                        value: displayTile.maxBrightness > 0 ? displayTile.brightness / displayTile.maxBrightness : 0
                        onMoved: value => cc.brightness.setBrightness(displayTile.displayName,
                                                                      Math.round(value * displayTile.maxBrightness))
                    }
                }
            }
        }

        Tile {
            Layout.fillWidth: true
            implicitHeight: soundColumn.implicitHeight + 24
            visible: !!cc.volume && cc.volume.available

            ColumnLayout {
                id: soundColumn
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                Text {
                    text: "Sound"
                    color: cc.textColor
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                }
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    GlassSlider {
                        Layout.fillWidth: true
                        icon: cc.volume && cc.volume.muted ? "audio-volume-muted-symbolic" : "audio-volume-high-symbolic"
                        value: cc.volume ? cc.volume.level : 0
                        onMoved: value => cc.volume.setLevel(value)
                    }
                    RoundToggle {
                        implicitWidth: 24
                        implicitHeight: 24
                        icon: "audio-volume-muted-symbolic"
                        checked: !!cc.volume && cc.volume.muted
                        onClicked: cc.volume.toggleMute()
                    }
                }
            }
        }

        Tile {
            Layout.fillWidth: true
            implicitHeight: 64

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Rectangle {
                    Layout.preferredWidth: 44
                    Layout.preferredHeight: 44
                    radius: 8
                    color: Qt.rgba(1, 1, 1, 0.12)

                    Kirigami.ShadowedImage {
                        id: art
                        anchors.fill: parent
                        radius: 8
                        source: cc.media && cc.media.active ? cc.media.artUrl : ""
                        fillMode: Image.PreserveAspectCrop
                        visible: status === Image.Ready
                    }
                    Kirigami.Icon {
                        anchors.centerIn: parent
                        width: 22
                        height: 22
                        source: "media-album-cover-symbolic"
                        isMask: true
                        color: cc.dimColor
                        visible: !art.visible
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    Text {
                        Layout.fillWidth: true
                        text: cc.media && cc.media.active ? (cc.media.title || "Playing") : "Not playing"
                        color: cc.media && cc.media.active ? cc.textColor : cc.dimColor
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        elide: Text.ElideRight
                    }
                    Text {
                        Layout.fillWidth: true
                        text: cc.media && cc.media.active ? cc.media.artist : ""
                        color: cc.dimColor
                        font.pixelSize: 11
                        elide: Text.ElideRight
                        visible: text !== ""
                    }
                }

                Repeater {
                    model: cc.media && cc.media.active ? 2 : 0

                    Kirigami.Icon {
                        required property int index
                        implicitWidth: 22
                        implicitHeight: 22
                        source: index === 0
                            ? (cc.media.playing ? "media-playback-pause-symbolic" : "media-playback-start-symbolic")
                            : "media-skip-forward-symbolic"
                        isMask: true
                        color: index === 1 && !cc.media.canNext ? cc.dimColor : cc.textColor

                        MouseArea {
                            anchors.fill: parent
                            anchors.margins: -6
                            cursorShape: Qt.PointingHandCursor
                            onClicked: parent.index === 0 ? cc.media.togglePlaying() : cc.media.next()
                        }
                    }
                }
            }
        }
    }
}
