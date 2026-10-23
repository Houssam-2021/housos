import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    id: page
    property alias cfg_city: cityField.text
    property string cfg_unit
    Kirigami.FormLayout {
        PlasmaComponents.TextField { id: cityField; Kirigami.FormData.label: "City:"; placeholderText: "e.g. Oujda" }
        PlasmaComponents.ComboBox {
            Kirigami.FormData.label: "Units:"
            model: ["celsius", "fahrenheit"]
            currentIndex: Math.max(0, model.indexOf(page.cfg_unit))
            onActivated: page.cfg_unit = currentText
        }
    }
}
