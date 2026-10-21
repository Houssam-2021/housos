// ============================================================================
// LiquidGlassClock.qml — KDE Plasma 6 Safe GPU-Accelerated Liquid Glass Clock
// Drop-in replacement for KDE Lockscreen (kscreenlocker Clock.qml) & Plasmoid.
//
// Safety guarantees for kscreenlocker (prevents "screen locker is broken"):
//   1. Uses only standard Qt 6 core modules (QtQuick, QtQuick.Layouts, QtQuick.Effects)
//      shipped in qt6-qtdeclarative on Fedora/Bazzite.
//   2. Root item is ColumnLayout with Layout.alignment / implicit sizes matching
//      upstream Plasma 6 org.kde.plasma.desktop/contents/lockscreen/Clock.qml.
//   3. Never binds ShaderEffectSource to an ancestor Item (which causes a Qt6
//      scene-graph parent-child cycle); translucent frosted glass + 3D tubular
//      specular bevels composite directly over the lockscreen wallpaper.
// ============================================================================
import QtQuick
import QtQuick.Layouts
import QtQuick.Effects

ColumnLayout {
    id: root
    spacing: 0
    Layout.alignment: Qt.AlignHCenter
    Layout.preferredWidth: 500
    Layout.preferredHeight: 390
    implicitWidth: 500
    implicitHeight: 390

    property bool use24Hour: false
    property string timeString: "3:23"
    property string dateString: "Wednesday, October 21"
    property real tubeWidth: 25

    function updateClock() {
        const now = new Date()
        let h = now.getHours()
        if (!root.use24Hour) {
            h = h % 12
            if (h === 0) h = 12
        }
        const m = String(now.getMinutes()).padStart(2, "0")
        const nextTime = h + ":" + m
        if (root.timeString !== nextTime) {
            root.timeString = nextTime
            if (maskCanvas.available) maskCanvas.requestPaint()
            if (bevelCanvas.available) bevelCanvas.requestPaint()
        }
        root.dateString = Qt.formatDate(now, "dddd, MMMM d")
    }

    Component.onCompleted: updateClock()

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.updateClock()
    }

    // Subtle Date Label Above the Ultra-Tall Digits
    Text {
        Layout.alignment: Qt.AlignHCenter
        text: root.dateString
        color: "#E8FFFFFF"
        font.family: "Inter"
        font.pixelSize: 19
        font.weight: Font.DemiBold
        font.letterSpacing: 0.6
        style: Text.Raised
        styleColor: "#55000000"
    }

    // Main Clock Stage
    Item {
        id: clockStage
        Layout.alignment: Qt.AlignHCenter
        Layout.preferredWidth: 480
        Layout.preferredHeight: 360
        width: 480
        height: 360

        // ---------------------------------------------------------------------
        // PASS 1: Ultra-Tall Condensed Numeral Alpha Mask (for soft elevation shadow)
        // ---------------------------------------------------------------------
        Canvas {
            id: maskCanvas
            anchors.fill: parent
            layer.enabled: true
            visible: false
            onAvailableChanged: if (available) requestPaint()
            onPaint: {
                const ctx = getContext("2d")
                ctx.reset()
                root.drawTimeGeometry(ctx, root.timeString, "#ffffff", root.tubeWidth, 0, 0)
            }
        }

        // Soft Drop Shadow Behind Glass Tubes
        MultiEffect {
            anchors.fill: parent
            source: maskCanvas
            shadowEnabled: true
            shadowColor: "#70050814"
            shadowBlur: 0.75
            shadowVerticalOffset: 10
            shadowHorizontalOffset: 0
            opacity: 0.55
        }

        // Soft Inner/Ambient Frosted Glow Behind the Tubes
        MultiEffect {
            anchors.fill: parent
            source: maskCanvas
            blurEnabled: true
            blurMax: 28
            blur: 0.55
            opacity: 0.22
        }

        // ---------------------------------------------------------------------
        // PASS 2: Milky Glass Sheen + 3D Tubular Specular Bevel Rim
        // ---------------------------------------------------------------------
        Canvas {
            id: bevelCanvas
            anchors.fill: parent
            layer.enabled: true
            onAvailableChanged: if (available) requestPaint()
            onPaint: {
                const ctx = getContext("2d")
                ctx.reset()

                // 1. Clip all optical bevel passes strictly inside the numeral strokes
                root.drawTimeGeometry(ctx, root.timeString, "#ffffff", root.tubeWidth, 0, 0)
                ctx.globalCompositeOperation = "source-in"

                // 2. Milky Vertical Glass Gradient (Clearer at top, glossy frost in lower-middle)
                const sheen = ctx.createLinearGradient(0, 20, 0, 340)
                sheen.addColorStop(0.00, "rgba(210, 228, 255, 0.24)")
                sheen.addColorStop(0.32, "rgba(235, 244, 255, 0.30)")
                sheen.addColorStop(0.58, "rgba(255, 255, 255, 0.54)")
                sheen.addColorStop(0.82, "rgba(240, 246, 255, 0.38)")
                sheen.addColorStop(1.00, "rgba(255, 255, 255, 0.60)")
                ctx.fillStyle = sheen
                ctx.fillRect(0, 0, width, height)

                // 3. Outer Dark/Warm Refractive Edge Ring (Physical glass thickness)
                ctx.globalCompositeOperation = "source-atop"
                root.drawTimeGeometry(ctx, root.timeString, "rgba(18, 24, 38, 0.42)", root.tubeWidth + 2, 1.5, 2.0)

                // 4. Top-Left 3D Curved Specular Highlight Band
                root.drawTimeGeometry(ctx, root.timeString, "rgba(255, 255, 255, 0.94)", root.tubeWidth - 4, -2.2, -2.2)

                // 5. Core Glass Transparency Cutout (Leaves the specular rim on the edges)
                ctx.globalCompositeOperation = "destination-out"
                root.drawTimeGeometry(ctx, root.timeString, "rgba(0, 0, 0, 0.58)", root.tubeWidth - 8, 0.8, 0.8)

                // 6. Crisp 1.5px Specular Rim Highlight Along the Tube Contour
                ctx.globalCompositeOperation = "source-over"
                root.drawTimeGeometry(ctx, root.timeString, "rgba(255, 255, 255, 0.62)", root.tubeWidth - 1.5, -0.5, -0.5)
            }
        }
    }

    // Ultra-Tall Condensed Numeral Renderer (Matches the 3:23 iOS 26 / Tahoe Geometry)
    function drawTimeGeometry(ctx, str, color, sw, ox, oy) {
        const chars = str.split("")
        const widths = []
        for (let k = 0; k < chars.length; k++) {
            widths.push(chars[k] === ":" ? 44 : 112)
        }
        const spacing = 14
        let totalW = (chars.length - 1) * spacing
        for (let k = 0; k < widths.length; k++) totalW += widths[k]
        let curX = (480 - totalW) / 2 + ox

        ctx.save()
        ctx.strokeStyle = color
        ctx.fillStyle = color
        ctx.lineWidth = sw
        ctx.lineCap = "butt"
        ctx.lineJoin = "round"

        for (let i = 0; i < chars.length; i++) {
            const ch = chars[i]
            ctx.save()
            ctx.translate(curX, oy)
            ctx.beginPath()

            if (ch === ":") {
                const r = sw * 0.56
                ctx.arc(22, 112, r, 0, Math.PI * 2)
                ctx.fill()
                ctx.beginPath()
                ctx.arc(22, 248, r, 0, Math.PI * 2)
                ctx.fill()
            } else {
                switch (ch) {
                case "0":
                    ctx.arc(55, 68, 39, Math.PI, 0, false)
                    ctx.lineTo(94, 292)
                    ctx.arc(55, 292, 39, 0, Math.PI, false)
                    ctx.closePath()
                    break
                case "1":
                    ctx.moveTo(28, 68); ctx.lineTo(62, 32); ctx.lineTo(62, 332)
                    break
                case "2":
                    ctx.moveTo(16, 108); ctx.lineTo(16, 68)
                    ctx.arc(55, 68, 39, Math.PI, 0.15 * Math.PI, false)
                    ctx.lineTo(16, 320); ctx.lineTo(16, 332); ctx.lineTo(98, 332)
                    break
                case "3":
                    ctx.moveTo(16, 108); ctx.lineTo(16, 68)
                    ctx.arc(55, 68, 39, Math.PI, 0, false)
                    ctx.lineTo(94, 134)
                    ctx.arc(55, 134, 39, 0, 0.5 * Math.PI, false)
                    ctx.moveTo(55, 173)
                    ctx.arc(55, 212, 39, -0.5 * Math.PI, 0, false)
                    ctx.lineTo(94, 292)
                    ctx.arc(55, 292, 39, 0, Math.PI, false)
                    ctx.lineTo(16, 248)
                    break
                case "4":
                    ctx.moveTo(80, 332); ctx.lineTo(80, 28)
                    ctx.lineTo(14, 236); ctx.lineTo(14, 248); ctx.lineTo(102, 248)
                    break
                case "5":
                    ctx.moveTo(92, 32); ctx.lineTo(18, 32); ctx.lineTo(18, 168)
                    ctx.arc(55, 190, 39, -0.75 * Math.PI, 0, false)
                    ctx.lineTo(94, 292)
                    ctx.arc(55, 292, 39, 0, Math.PI, false)
                    ctx.lineTo(16, 252)
                    break
                case "6":
                    ctx.moveTo(94, 104); ctx.lineTo(94, 68)
                    ctx.arc(55, 68, 39, 0, Math.PI, true)
                    ctx.lineTo(16, 292)
                    ctx.arc(55, 292, 39, Math.PI, 0, true)
                    ctx.lineTo(94, 212)
                    ctx.arc(55, 212, 39, 0, Math.PI, true)
                    break
                case "7":
                    ctx.moveTo(14, 44); ctx.lineTo(14, 32); ctx.lineTo(94, 32)
                    ctx.lineTo(94, 46); ctx.lineTo(34, 332)
                    break
                case "8":
                    ctx.arc(55, 68, 39, Math.PI, 0, false)
                    ctx.lineTo(94, 132)
                    ctx.arc(55, 132, 39, 0, Math.PI, false)
                    ctx.closePath()
                    ctx.stroke()
                    ctx.beginPath()
                    ctx.arc(55, 210, 39, Math.PI, 0, false)
                    ctx.lineTo(94, 292)
                    ctx.arc(55, 292, 39, 0, Math.PI, false)
                    ctx.closePath()
                    break
                case "9":
                    ctx.moveTo(94, 148)
                    ctx.arc(55, 148, 39, 0, Math.PI, false)
                    ctx.lineTo(16, 68)
                    ctx.arc(55, 68, 39, Math.PI, 0, false)
                    ctx.lineTo(94, 292)
                    ctx.arc(55, 292, 39, 0, Math.PI, false)
                    ctx.lineTo(16, 256)
                    break
                }
                ctx.stroke()
            }
            ctx.restore()
            curX += widths[i] + spacing
        }
        ctx.restore()
    }
}
