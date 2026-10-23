import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    readonly property var quotes: [["The best way to predict the future is to create it.", "Peter Drucker"], ["Simplicity is the ultimate sophistication.", "Leonardo da Vinci"], ["Stay hungry, stay foolish.", "Stewart Brand"], ["Well done is better than well said.", "Benjamin Franklin"], ["It always seems impossible until it's done.", "Nelson Mandela"], ["Make it work, make it right, make it fast.", "Kent Beck"], ["Small steps every day.", "Unknown"], ["Done is better than perfect.", "Sheryl Sandberg"], ["Knowledge is power.", "Francis Bacon"], ["What we think, we become.", "Buddha"], ["Patience is bitter, but its fruit is sweet.", "Jean-Jacques Rousseau"], ["The secret of getting ahead is getting started.", "Mark Twain"], ["Quality is not an act, it is a habit.", "Will Durant"], ["Seek knowledge from the cradle to the grave.", "Proverb"]]
    property int pick: Math.floor(Date.now() / 86400000) % quotes.length

    fullRepresentation: MouseArea {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 18
        Layout.preferredHeight: Kirigami.Units.gridUnit * 7
        onClicked: root.pick = (root.pick + 1) % root.quotes.length
        ColumnLayout {
            anchors.fill: parent
            Text {
                Layout.fillWidth: true
                Layout.fillHeight: true
                text: "“" + root.quotes[root.pick][0] + "”"
                color: Kirigami.Theme.textColor
                wrapMode: Text.WordWrap
                font.pixelSize: Kirigami.Units.gridUnit * 1.2
                font.italic: true
                verticalAlignment: Text.AlignVCenter
            }
            PlasmaComponents.Label { Layout.alignment: Qt.AlignRight; text: "— " + root.quotes[root.pick][1]; color: Kirigami.Theme.highlightColor }
        }
    }
}
