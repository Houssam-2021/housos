/*
    HoussamOS Control Center: a button in the top bar that opens a glass panel with Wi-Fi,
    Bluetooth, airplane mode, Do Not Disturb, screenshot, settings, display and sound sliders and
    the music that is playing, in the style of macOS's Control Center.
    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    preferredRepresentation: compactRepresentation
    toolTipMainText: "Control Center"
    toolTipSubText: "Wi-Fi, Bluetooth, sound, display and music"

    compactRepresentation: MouseArea {
        property bool wasExpanded: false

        hoverEnabled: true
        onPressed: wasExpanded = root.expanded
        onClicked: root.expanded = !wasExpanded

        Kirigami.Icon {
            anchors.fill: parent
            source: Qt.resolvedUrl("../images/control-center.svg")
            isMask: true
            color: Kirigami.Theme.textColor
            active: parent.containsMouse
        }
    }

    fullRepresentation: ControlCenter {
        Layout.minimumWidth: implicitWidth
        Layout.preferredWidth: implicitWidth
        Layout.maximumWidth: implicitWidth
        Layout.minimumHeight: implicitHeight
        Layout.preferredHeight: implicitHeight
        Layout.maximumHeight: implicitHeight
        onCloseRequested: root.expanded = false
    }
}
