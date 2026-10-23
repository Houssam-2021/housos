import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    ListModel { id: tasks }

    function load() {
        tasks.clear();
        try {
            JSON.parse(Plasmoid.configuration.items || "[]").forEach(t => tasks.append({ text: String(t.text), done: !!t.done }));
        } catch (e) {}
    }
    function store() {
        const out = [];
        for (let i = 0; i < tasks.count; i++) out.push({ text: tasks.get(i).text, done: tasks.get(i).done });
        Plasmoid.configuration.items = JSON.stringify(out);
    }
    Component.onCompleted: load()

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 14
        PlasmaComponents.Label { text: "To do"; font.weight: Font.DemiBold; font.pixelSize: Kirigami.Units.gridUnit * 1.2 }
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: tasks
            delegate: RowLayout {
                required property int index
                required property string text
                required property bool done
                width: ListView.view.width
                PlasmaComponents.CheckBox {
                    checked: done
                    onToggled: { tasks.setProperty(index, "done", checked); root.store(); }
                }
                PlasmaComponents.Label { Layout.fillWidth: true; text: parent.text; opacity: done ? 0.5 : 1; font.strikeout: done; elide: Text.ElideRight }
                PlasmaComponents.ToolButton { icon.name: "edit-delete-remove"; onClicked: { tasks.remove(index); root.store(); } }
            }
        }
        PlasmaComponents.TextField {
            Layout.fillWidth: true
            placeholderText: "Add a task and press Enter"
            onAccepted: {
                if (text.trim()) { tasks.append({ text: text.trim(), done: false }); root.store(); text = ""; }
            }
        }
    }
}
