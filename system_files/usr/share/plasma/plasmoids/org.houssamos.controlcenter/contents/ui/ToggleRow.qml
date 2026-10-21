import QtQuick
import QtQuick.Layouts

// One line of a control center tile: a round toggle, a name and what state it is in
RowLayout {
    id: row

    property alias icon: toggle.icon
    property alias checked: toggle.checked
    property string title
    property string subtitle
    signal toggled()

    spacing: 10

    RoundToggle {
        id: toggle
        enabled: row.enabled
        onClicked: row.toggled()
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 0

        Text {
            Layout.fillWidth: true
            text: row.title
            color: "#f2f4f8"
            font.pixelSize: 13
            font.weight: Font.DemiBold
            elide: Text.ElideRight
        }
        Text {
            Layout.fillWidth: true
            text: row.subtitle
            color: Qt.rgba(1, 1, 1, 0.6)
            font.pixelSize: 11
            elide: Text.ElideRight
            visible: text !== ""
        }
    }
}
