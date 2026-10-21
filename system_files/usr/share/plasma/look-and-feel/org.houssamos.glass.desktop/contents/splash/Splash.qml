import QtQuick

// HoussamOS login splash: the glass logo on deep navy, with a thin blue-to-violet progress line
// that fills as the desktop loads. KSplash sets `stage` from 1 to 6.
Rectangle {
    id: root

    property int stage

    gradient: Gradient {
        GradientStop { position: 0.0; color: "#070a16" }
        GradientStop { position: 1.0; color: "#0d1226" }
    }

    // Soft glow behind the logo
    Rectangle {
        anchors.centerIn: logo
        width: logo.width * 1.6
        height: width * 0.5
        radius: height / 2
        opacity: logo.opacity * 0.35
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: "transparent" }
            GradientStop { position: 0.5; color: "#2a3f8f" }
            GradientStop { position: 1.0; color: "transparent" }
        }
    }

    Image {
        id: logo
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -24
        source: "images/houssamos.png"
        width: Math.min(root.width * 0.32, 560)
        fillMode: Image.PreserveAspectFit
        smooth: true
        mipmap: true
        opacity: 0

        NumberAnimation on opacity {
            from: 0
            to: 1
            duration: 800
            easing.type: Easing.OutCubic
        }
    }

    Rectangle {
        id: track
        anchors.top: logo.bottom
        anchors.topMargin: 48
        anchors.horizontalCenter: parent.horizontalCenter
        width: logo.width * 0.4
        height: 3
        radius: 1.5
        color: "#1c2236"

        Rectangle {
            height: parent.height
            radius: parent.radius
            width: parent.width * Math.min(Math.max(root.stage, 0), 6) / 6
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "#4c8dff" }
                GradientStop { position: 1.0; color: "#8b6cff" }
            }

            Behavior on width {
                NumberAnimation {
                    duration: 600
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
}
