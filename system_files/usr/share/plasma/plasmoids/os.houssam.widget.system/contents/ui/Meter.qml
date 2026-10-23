import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

ColumnLayout {
    property string label
    property string valueText
    property real fraction: 0
    spacing: 4

    RowLayout {
        Layout.fillWidth: true
        PlasmaComponents.Label { text: label; opacity: 0.75 }
        Item { Layout.fillWidth: true }
        PlasmaComponents.Label { text: valueText; font.weight: Font.DemiBold }
    }
    Rectangle {
        Layout.fillWidth: true
        implicitHeight: 6
        radius: 3
        color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.15)
        Rectangle {
            width: parent.width * Math.max(0, Math.min(1, fraction))
            height: parent.height
            radius: 3
            color: Kirigami.Theme.highlightColor
            Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutQuart } }
        }
    }
}
