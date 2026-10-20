import QtQuick

// HoussamOS login splash: the glass logo on the same white as the boot animation, with a thin
// progress line that fills as the desktop loads. KSplash sets `stage` from 1 to 6.
Rectangle {
    id: root
    color: "#fdfdfd"

    property int stage

    Image {
        id: logo
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -24
        source: "images/houssamos.png"
        width: Math.min(root.width * 0.36, 620)
        fillMode: Image.PreserveAspectFit
        smooth: true
        mipmap: true
        opacity: 0

        NumberAnimation on opacity {
            from: 0
            to: 1
            duration: 700
            easing.type: Easing.OutCubic
        }
    }

    Rectangle {
        id: track
        anchors.top: logo.bottom
        anchors.topMargin: 48
        anchors.horizontalCenter: parent.horizontalCenter
        width: logo.width * 0.45
        height: 4
        radius: 2
        color: "#e4e9f1"

        Rectangle {
            height: parent.height
            radius: parent.radius
            color: "#3482f6"
            width: parent.width * Math.min(Math.max(root.stage, 0), 6) / 6

            Behavior on width {
                NumberAnimation {
                    duration: 600
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
}
