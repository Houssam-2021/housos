import QtQuick
import org.kde.bluezqt as BluezQt

// Bluetooth on and off, as KDE's Bluetooth widget does it
Item {
    readonly property bool available: BluezQt.Manager.bluetoothBlocked || BluezQt.Manager.adapters.length > 0
    readonly property bool isOn: BluezQt.Manager.bluetoothOperational
    readonly property int connectedDevices: BluezQt.Manager.connectedDevices.length

    function setOn(enable) {
        BluezQt.Manager.bluetoothBlocked = !enable;
        BluezQt.Manager.adapters.forEach(adapter => {
            adapter.powered = enable;
        });
    }
}
