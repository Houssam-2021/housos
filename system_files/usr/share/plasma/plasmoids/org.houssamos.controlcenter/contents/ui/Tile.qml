import QtQuick

// A rounded glass tile of the control center, brighter while `active`. With `clickable` it
// reacts to the pointer and emits clicked().
Rectangle {
    id: tile

    property bool active: false
    property bool clickable: false
    signal clicked()

    radius: 14
    color: active ? Qt.rgba(1, 1, 1, 0.20) : (area.containsMouse ? Qt.rgba(1, 1, 1, 0.12) : Qt.rgba(1, 1, 1, 0.08))
    border.width: 1
    border.color: Qt.rgba(1, 1, 1, 0.10)
    scale: area.pressed ? 0.97 : 1

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }

    MouseArea {
        id: area
        anchors.fill: parent
        enabled: tile.clickable
        hoverEnabled: tile.clickable
        cursorShape: tile.clickable ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: tile.clicked()
    }
}
