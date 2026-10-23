import QtQuick
import org.kde.plasma.plasma5support as P5Support

P5Support.DataSource {
    id: shell
    engine: "executable"
    property var callbacks: ({})

    function exec(command, callback) {
        callbacks[command] = callback;
        connectSource(command);
    }

    onNewData: (source, data) => {
        const callback = callbacks[source];
        delete callbacks[source];
        disconnectSource(source);
        if (callback) {
            callback(data["stdout"] || "", data["exit code"]);
        }
    }
}
