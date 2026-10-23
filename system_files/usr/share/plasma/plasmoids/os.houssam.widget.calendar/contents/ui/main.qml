import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property date today: new Date()
    property int month: today.getMonth()
    property int year: today.getFullYear()
    readonly property int firstDay: Qt.locale().firstDayOfWeek
    Timer { interval: 60000; running: true; repeat: true; onTriggered: root.today = new Date() }

    function cells() {
        const first = new Date(year, month, 1);
        const offset = (first.getDay() - firstDay + 7) % 7;
        const days = new Date(year, month + 1, 0).getDate();
        const out = [];
        for (let i = 0; i < 42; i++) {
            const d = i - offset + 1;
            out.push(d >= 1 && d <= days ? d : 0);
        }
        return out;
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 15
        RowLayout {
            Layout.fillWidth: true
            PlasmaComponents.ToolButton { icon.name: "go-previous"; onClicked: { if (root.month === 0) { root.month = 11; root.year--; } else root.month--; } }
            PlasmaComponents.Label {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: Qt.locale().standaloneMonthName(root.month) + " " + root.year
                font.weight: Font.DemiBold
            }
            PlasmaComponents.ToolButton { icon.name: "go-next"; onClicked: { if (root.month === 11) { root.month = 0; root.year++; } else root.month++; } }
        }
        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: 7
            columnSpacing: 2
            rowSpacing: 2
            Repeater {
                model: 7
                PlasmaComponents.Label {
                    required property int index
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    text: Qt.locale().dayName((index + root.firstDay) % 7, Locale.NarrowFormat)
                    opacity: 0.6
                }
            }
            Repeater {
                model: root.cells()
                Rectangle {
                    required property int modelData
                    readonly property bool isToday: modelData === root.today.getDate() && root.month === root.today.getMonth() && root.year === root.today.getFullYear()
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: height / 2
                    color: isToday ? Kirigami.Theme.highlightColor : "transparent"
                    PlasmaComponents.Label {
                        anchors.centerIn: parent
                        text: modelData > 0 ? modelData : ""
                        color: parent.isToday ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
                    }
                }
            }
        }
    }
}
