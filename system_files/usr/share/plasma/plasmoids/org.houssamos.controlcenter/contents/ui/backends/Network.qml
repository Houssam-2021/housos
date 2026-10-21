import QtQuick
import org.kde.plasma.networkmanagement as PlasmaNM

// Wi-Fi and airplane mode, through the same objects as KDE's network widget
Item {
    readonly property bool wifiAvailable: enabledConnections.wirelessHwEnabled
    readonly property bool wifiOn: enabledConnections.wirelessEnabled
    readonly property bool airplaneOn: PlasmaNM.Configuration.airplaneModeEnabled
    // e.g. "Home WiFi: Connected"; the first line when there are several connections
    readonly property string status: (networkStatus.activeConnections || "").split("\n")[0]

    function setWifi(on) {
        handler.enableWireless(on);
    }

    function setAirplane(on) {
        handler.enableAirplaneMode(on);
        PlasmaNM.Configuration.airplaneModeEnabled = on;
    }

    PlasmaNM.EnabledConnections {
        id: enabledConnections
    }

    PlasmaNM.NetworkStatus {
        id: networkStatus
    }

    PlasmaNM.Handler {
        id: handler
    }
}
