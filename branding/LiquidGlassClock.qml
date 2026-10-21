/*
    HoussamOS lock screen clock: the date over large liquid glass digits. The digits are a real
    font (Inter Display, semibold) that act like glass: the wallpaper shows through them blurred,
    slightly magnified like a lens and more vivid, with a gloss at the top, a bright rim of light
    along the top-left edges, a softer one along the bottom-right, and a soft shadow.

    build_files/build.sh installs this file next to KDE's LockScreenUi.qml and makes its Clock use
    it. LockScreenUi also draws a drop-shadowed copy of the clock (clockShadow, given to the clock
    as "shadow"); this clock hides that copy, because a second layer would make the glass solid.
    The wallpaper comes from LockScreenUi's WallpaperFader (a sibling with mainStack and source);
    if it isn't found the digits are frosted white instead. Without a GPU (software rendering) the
    effects can't run, so plain digits are shown.
*/
import QtQuick
import QtQuick.Layouts
import QtQuick.Effects
import QtQuick.Window

ColumnLayout {
    id: root

    readonly property bool softwareRendering: GraphicsInfo.api === GraphicsInfo.Software
    readonly property bool use24Hour: Qt.locale().timeFormat(Locale.ShortFormat).toLowerCase().indexOf("a") === -1
    readonly property int digitSize: Math.round(Math.max(100, Math.min(190, Screen.height * 0.16)))
    property date now: new Date()

    // 12-hour clocks show no AM/PM, as on phones
    readonly property string timeText: use24Hour
        ? Qt.formatTime(now, Qt.locale(), Locale.ShortFormat)
        : ((now.getHours() % 12) || 12) + ":" + String(now.getMinutes()).padStart(2, "0")
    readonly property string dateText: Qt.formatDate(now, Qt.locale(), Locale.LongFormat)

    // The wallpaper item, and where the digits sit over it
    property Item backdrop: null
    property rect behindRect: Qt.rect(0, 0, 1, 1)
    // How much white frost covers the glass: less when the wallpaper shows through
    readonly property real frost: backdrop ? 0.45 : 1.0

    function updateBehind() {
        if (backdrop && digits.width > 0) {
            const at = digits.mapToItem(backdrop, 0, 0);
            behindRect = Qt.rect(at.x, at.y, digits.width, digits.height);
        }
    }

    spacing: 0
    onXChanged: updateBehind()
    onYChanged: updateBehind()

    Component.onCompleted: {
        if (root.shadow) {
            root.shadow.visible = false;
        }
        const siblings = root.parent ? root.parent.children : [];
        for (let i = 0; i < siblings.length; i++) {
            if (siblings[i] !== root && siblings[i].mainStack !== undefined && siblings[i].source) {
                root.backdrop = siblings[i].source;
                break;
            }
        }
        updateBehind();
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            root.now = new Date();
            root.updateBehind();
        }
    }

    component Glyphs: Text {
        text: root.timeText
        font.family: "Inter Display"
        font.pixelSize: root.digitSize
        font.weight: Font.DemiBold
        font.letterSpacing: -root.digitSize * 0.02
        font.features: { "tnum": 1 }
    }

    Text {
        Layout.alignment: Qt.AlignHCenter
        text: root.dateText
        color: "#F2FFFFFF"
        font.family: "Inter"
        font.pixelSize: Math.round(root.digitSize * 0.18)
        font.weight: Font.Medium
        style: Text.Raised
        styleColor: "#59000000"
    }

    Item {
        id: digits

        // Room around the digits for the shadow; the negative layout margins take most of it
        // back, so the clock stays compact
        readonly property int pad: Math.round(root.digitSize * 0.14)
        readonly property real rim: Math.max(1.5, root.digitSize * 0.014)

        Layout.alignment: Qt.AlignHCenter
        Layout.topMargin: -Math.round(root.digitSize * 0.26)
        Layout.bottomMargin: -Math.round(root.digitSize * 0.30)
        implicitWidth: glyphs.implicitWidth + pad * 2
        implicitHeight: glyphs.implicitHeight + pad * 2

        Glyphs {
            visible: root.softwareRendering
            x: digits.pad
            y: digits.pad
            color: "#EBFFFFFF"
            style: Text.Outline
            styleColor: "#4D000000"
        }

        Item {
            anchors.fill: parent
            visible: !root.softwareRendering

            // The digit shapes, used as masks and never shown themselves. The two shifted copies
            // mark the edges: what the down-right copy doesn't cover is the top-left edge.
            Item {
                id: shape
                anchors.fill: parent
                visible: false
                layer.enabled: true
                Glyphs { id: glyphs; x: digits.pad; y: digits.pad; color: "white" }
            }
            Item {
                id: shapeDownRight
                anchors.fill: parent
                visible: false
                layer.enabled: true
                Glyphs { x: digits.pad + digits.rim; y: digits.pad + digits.rim; color: "white" }
            }
            Item {
                id: shapeUpLeft
                anchors.fill: parent
                visible: false
                layer.enabled: true
                Glyphs { x: digits.pad - digits.rim; y: digits.pad - digits.rim; color: "white" }
            }

            // Soft shadow under the glass
            MultiEffect {
                anchors.fill: parent
                transform: Translate { y: Math.round(root.digitSize * 0.02) }
                source: shape
                colorization: 1.0
                colorizationColor: "#000614"
                autoPaddingEnabled: false
                blurEnabled: true
                blurMax: 24
                blur: 0.5
                opacity: 0.22
            }

            // The wallpaper seen through the glass: a slightly smaller area stretched over the
            // digits, so it is magnified like a lens, then blurred and made more vivid
            ShaderEffectSource {
                id: behind
                anchors.fill: parent
                visible: false
                sourceItem: root.backdrop
                sourceRect: Qt.rect(root.behindRect.x + root.behindRect.width * 0.04,
                                    root.behindRect.y + root.behindRect.height * 0.04,
                                    root.behindRect.width * 0.92, root.behindRect.height * 0.92)
            }
            MultiEffect {
                anchors.fill: parent
                visible: root.backdrop !== null
                source: behind
                // Padding would stretch the mask over a bigger area than the digits
                autoPaddingEnabled: false
                blurEnabled: true
                blurMax: 32
                blur: 0.5
                brightness: 0.12
                saturation: 0.45
                maskEnabled: true
                maskSource: shape
                maskThresholdMin: 0.5
                maskSpreadAtMin: 1.0
            }

            // Frost and gloss: brighter at the top of the digits, a faint gloss line across the
            // middle, and a little light caught again at the bottom. The digits fill roughly the
            // middle half of this item (between the cap height and the baseline).
            Rectangle {
                id: frostFill
                anchors.fill: parent
                visible: false
                layer.enabled: true
                gradient: Gradient {
                    GradientStop { position: 0.25; color: Qt.rgba(0.94, 0.96, 1.0, 0.58 * root.frost) }
                    GradientStop { position: 0.42; color: Qt.rgba(0.94, 0.96, 1.0, 0.32 * root.frost) }
                    GradientStop { position: 0.50; color: Qt.rgba(0.94, 0.96, 1.0, 0.18 * root.frost) }
                    GradientStop { position: 0.51; color: Qt.rgba(0.94, 0.96, 1.0, 0.11 * root.frost) }
                    GradientStop { position: 0.75; color: Qt.rgba(0.94, 0.96, 1.0, 0.28 * root.frost) }
                }
            }
            MultiEffect {
                anchors.fill: parent
                source: frostFill
                maskEnabled: true
                maskSource: shape
                maskThresholdMin: 0.5
                maskSpreadAtMin: 1.0
            }

            // Bright rim along the top-left edges
            Rectangle {
                id: lightRim
                anchors.fill: parent
                visible: false
                layer.enabled: true
                color: Qt.rgba(1, 1, 1, 0.95)
            }
            Item {
                id: topLeftEdge
                anchors.fill: parent
                visible: false
                layer.enabled: true
                MultiEffect {
                    anchors.fill: parent
                    source: lightRim
                    maskEnabled: true
                    maskInverted: true
                    maskSource: shapeDownRight
                    maskThresholdMin: 0.5
                    maskSpreadAtMin: 1.0
                }
            }
            MultiEffect {
                anchors.fill: parent
                source: topLeftEdge
                maskEnabled: true
                maskSource: shape
                maskThresholdMin: 0.5
                maskSpreadAtMin: 1.0
            }

            // Softer rim along the bottom-right edges
            Rectangle {
                id: softRim
                anchors.fill: parent
                visible: false
                layer.enabled: true
                color: Qt.rgba(1, 1, 1, 0.38)
            }
            Item {
                id: bottomRightEdge
                anchors.fill: parent
                visible: false
                layer.enabled: true
                MultiEffect {
                    anchors.fill: parent
                    source: softRim
                    maskEnabled: true
                    maskInverted: true
                    maskSource: shapeUpLeft
                    maskThresholdMin: 0.5
                    maskSpreadAtMin: 1.0
                }
            }
            MultiEffect {
                anchors.fill: parent
                source: bottomRightEdge
                maskEnabled: true
                maskSource: shape
                maskThresholdMin: 0.5
                maskSpreadAtMin: 1.0
            }
        }
    }
}
