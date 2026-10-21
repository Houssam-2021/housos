import QtQuick
import org.kde.kirigami as Kirigami

// A round icon button: HoussamOS blue when on, frosted when off
Rectangle {
    id: toggle

    property string icon
    property bool checked: false
    signal clicked()

    implicitWidth: 30
    implicitHeight: 30
    radius: width / 2
    color: checked ? "#4c8dff" : Qt.rgba(1, 1, 1, 0.16)
    opacity: enabled ? 1 : 0.4
    scale: area.pressed ? 0.9 : 1

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }

    Kirigami.Icon {
        anchors.centerIn: parent
        width: 16
        height: 16
        source: toggle.icon
        isMask: true
        color: "white"
    }

    MouseArea {
        id: area
        anchors.fill: parent
        enabled: toggle.enabled
        cursorShape: Qt.PointingHandCursor
        onClicked: toggle.clicked()
    }
}
