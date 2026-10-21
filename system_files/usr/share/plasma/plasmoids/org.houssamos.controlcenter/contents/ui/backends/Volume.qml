import QtQuick
import org.kde.plasma.private.volume

// The volume of the default output, as KDE's volume widget sees it (0 to 1 is 0 to 100 %)
Item {
    readonly property var sink: PreferredDevice.sink
    readonly property bool available: !!sink
    readonly property bool muted: available && sink.muted
    readonly property real level: available && !sink.muted ? sink.volume / PulseAudio.NormalVolume : 0

    function setLevel(value) {
        if (!available) {
            return;
        }
        sink.volume = Math.round(value * PulseAudio.NormalVolume);
        sink.muted = value === 0;
    }

    function toggleMute() {
        if (available) {
            sink.muted = !sink.muted;
        }
    }
}
