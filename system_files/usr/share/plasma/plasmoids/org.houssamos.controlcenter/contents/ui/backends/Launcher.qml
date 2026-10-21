import QtQuick
import org.kde.plasma.plasma5support as P5Support

// Starts programs (Spectacle, System Settings)
Item {
    function run(command) {
        runner.connectSource(command);
    }

    P5Support.DataSource {
        id: runner
        engine: "executable"
        onNewData: source => disconnectSource(source)
    }
}
