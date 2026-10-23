import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property date now: new Date()
    readonly property bool twelveHour: Qt.locale().timeFormat(Locale.ShortFormat).toLowerCase().indexOf("a") >= 0

    Timer {
        interval: 1000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: root.now = new Date()
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 8
        spacing: 0
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: Qt.formatTime(root.now, (root.twelveHour ? "h:mm" : "hh:mm") + (Plasmoid.configuration.showSeconds ? ":ss" : ""))
            color: Kirigami.Theme.textColor
            font.pixelSize: Kirigami.Units.gridUnit * 4
            font.weight: Font.Light
            font.features: { "tnum": 1 }
        }
        PlasmaComponents.Label {
            Layout.alignment: Qt.AlignHCenter
            text: Qt.formatDate(root.now, Qt.locale(), Locale.LongFormat)
            opacity: 0.75
        }
    }
}
