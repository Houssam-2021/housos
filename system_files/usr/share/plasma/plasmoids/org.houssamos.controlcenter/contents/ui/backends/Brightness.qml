import QtQuick
import org.kde.plasma.private.brightnesscontrolplugin

// Screen brightness, from KDE's power management (not available in most virtual machines).
// `displays` is a model with the roles displayName, label, brightness and maxBrightness.
Item {
    readonly property bool available: control.isBrightnessAvailable
    readonly property var displays: control.displays

    function setBrightness(displayName, value) {
        control.setBrightness(displayName, value);
    }

    ScreenBrightnessControl {
        id: control
    }
}
