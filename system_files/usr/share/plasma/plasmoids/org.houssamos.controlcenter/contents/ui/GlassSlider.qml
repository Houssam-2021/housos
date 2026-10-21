import QtQuick
import org.kde.kirigami as Kirigami

// The control center's slider: a frosted pill that fills with white up to a round knob, with
// an icon at its start. `value` (0 to 1) comes from outside; dragging, clicking or scrolling
// emits moved() with the new value, and the slider follows the pointer while dragging.
Item {
    id: slider

    property real value: 0
    property string icon
    signal moved(real value)

    readonly property real shown: area.pressed ? area.dragValue : Math.max(0, Math.min(1, value))

    implicitWidth: 200
    implicitHeight: 24

    Rectangle {
        anchors.fill: parent
        radius: height / 2
        color: Qt.rgba(1, 1, 1, 0.16)
    }

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: slider.height + (slider.width - slider.height) * slider.shown
        radius: height / 2
        color: Qt.rgba(1, 1, 1, 0.92)
    }

    Kirigami.Icon {
        x: 5
        anchors.verticalCenter: parent.verticalCenter
        width: 14
        height: 14
        source: slider.icon
        isMask: true
        color: "#3a3f55"
    }

    Rectangle {
        width: slider.height
        height: slider.height
        radius: height / 2
        x: (slider.width - width) * slider.shown
        color: "white"
        border.width: 1
        border.color: Qt.rgba(0, 0, 0, 0.12)
        visible: slider.shown > 0.06
    }

    MouseArea {
        id: area

        property real dragValue: 0

        function valueAt(x) {
            return Math.max(0, Math.min(1, (x - slider.height / 2) / (slider.width - slider.height)));
        }

        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onPressed: mouse => {
            dragValue = valueAt(mouse.x);
            slider.moved(dragValue);
        }
        onPositionChanged: mouse => {
            if (pressed) {
                dragValue = valueAt(mouse.x);
                slider.moved(dragValue);
            }
        }
        onWheel: wheel => slider.moved(Math.max(0, Math.min(1, slider.value + wheel.angleDelta.y / 120 * 0.05)))
    }
}
