import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    id: page
    property alias cfg_label: labelField.text
    property alias cfg_target: targetField.text
    Kirigami.FormLayout {
        PlasmaComponents.TextField { id: labelField; Kirigami.FormData.label: "Name:" }
        PlasmaComponents.TextField { id: targetField; Kirigami.FormData.label: "Date:"; placeholderText: "2027-01-01T00:00:00" }
    }
}
