import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    id: page
    property alias cfg_showSeconds: seconds.checked
    Kirigami.FormLayout {
        PlasmaComponents.CheckBox { id: seconds; Kirigami.FormData.label: "Seconds:"; text: "Show seconds" }
    }
}
