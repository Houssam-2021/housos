import QtQuick
import org.kde.plasma.private.mpris as Mpris

// The music or video that is playing, from KDE's media controller
Item {
    readonly property var player: mpris.currentPlayer
    readonly property int status: player ? player.playbackStatus : 0
    readonly property bool active: status > Mpris.PlaybackStatus.Stopped
    readonly property bool playing: status === Mpris.PlaybackStatus.Playing
    readonly property string title: player ? player.track : ""
    readonly property string artist: player ? player.artist : ""
    readonly property string artUrl: player ? player.artUrl : ""
    readonly property bool canNext: player ? player.canGoNext : false

    function togglePlaying() {
        if (!player) {
            return;
        }
        if (playing) {
            player.Pause();
        } else {
            player.Play();
        }
    }

    function next() {
        if (player) {
            player.Next();
        }
    }

    Mpris.Mpris2Model {
        id: mpris
    }
}
