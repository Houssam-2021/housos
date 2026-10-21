import QtQuick

// HoussamOS login splash: it continues the boot animation. Same purple as the boot video
// (branding/make_branding.py prints it), the logo as the video's last frame at the size the boot
// screen draws it, and a thin light line underneath that fills as the desktop loads.
// KSplash sets `stage` from 1 to 6.
Rectangle {
    id: root

    property int stage
    // The boot screen draws its 800 px frames at whole multiples on large screens
    readonly property int bootScale: Math.max(1, Math.floor((width + 400) / 1920))

    color: "#22163f"

    Image {
        id: logo
        anchors.centerIn: parent
        source: "images/boot-logo.png"
        width: implicitWidth * root.bootScale
        height: implicitHeight * root.bootScale
        smooth: true
    }

    Rectangle {
        id: track
        anchors.top: logo.bottom
        anchors.topMargin: 12 * root.bootScale
        anchors.horizontalCenter: parent.horizontalCenter
        width: 180 * root.bootScale
        height: 3 * root.bootScale
        radius: height / 2
        color: Qt.rgba(1, 1, 1, 0.14)

        Rectangle {
            height: parent.height
            radius: parent.radius
            width: parent.width * Math.min(Math.max(root.stage, 0), 6) / 6
            color: Qt.rgba(0.92, 0.94, 1, 0.85)

            Behavior on width {
                NumberAnimation {
                    duration: 600
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
}
