#!/usr/bin/env python3
"""Generate the HoussamOS desktop widgets (Rainmeter-style Plasma plasmoids os.houssam.widget.<type>).

Each widget sits on Plasma's standard background, which the HoussamOS glass theme draws as frosted
glass with live blur, and takes its colours from the current theme (Kirigami.Theme, which follows
the colour scheme `hosctl theme set` applies; the accent is the highlight colour). `hosctl widget
add <type> [--options JSON]` places them; the options are the config keys listed per widget.

Usage: python branding/make_widgets.py
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "system_files/usr/share/plasma/plasmoids"
PREFIX = "os.houssam.widget."

HEADER = '''import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami
'''

# Runs a command and hands its output to a callback (Plasma's "executable" data engine)
SHELL_QML = '''import QtQuick
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
'''

# A label and a value with a thin bar under it (system, disk widgets)
METER_QML = HEADER + '''
ColumnLayout {
    property string label
    property string valueText
    property real fraction: 0
    spacing: 4

    RowLayout {
        Layout.fillWidth: true
        PlasmaComponents.Label { text: label; opacity: 0.75 }
        Item { Layout.fillWidth: true }
        PlasmaComponents.Label { text: valueText; font.weight: Font.DemiBold }
    }
    Rectangle {
        Layout.fillWidth: true
        implicitHeight: 6
        radius: 3
        color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.15)
        Rectangle {
            width: parent.width * Math.max(0, Math.min(1, fraction))
            height: parent.height
            radius: 3
            color: Kirigami.Theme.highlightColor
            Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutQuart } }
        }
    }
}
'''

CONFIG_MODEL = '''import QtQuick
import org.kde.plasma.configuration

ConfigModel {
    ConfigCategory {
        name: "General"
        icon: "configure"
        source: "configGeneral.qml"
    }
}
'''


def config_xml(entries):
    rows = "\n".join(f'    <entry name="{n}" type="{t}"><default>{d}</default></entry>' for n, t, d in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<kcfg xmlns="http://www.kde.org/standards/kcfg/1.0"\n'
            '      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            '      xsi:schemaLocation="http://www.kde.org/standards/kcfg/1.0 http://www.kde.org/standards/kcfg/1.0/kcfg.xsd">\n'
            '  <kcfgfile name=""/>\n  <group name="General">\n' + rows + '\n  </group>\n</kcfg>\n')


WIDGETS = {}


def widget(type_, name, description, icon, category, qml, config=(), config_page=None, extra=None):
    WIDGETS[type_] = dict(name=name, description=description, icon=icon, category=category, qml=qml,
                          config=config, config_page=config_page, extra=extra or {})


widget("clock", "Clock", "Big clock with the date", "preferences-system-time", "Date and Time", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property date now: new Date()
    readonly property bool twelveHour: Qt.locale().timeFormat(Locale.ShortFormat).toLowerCase().indexOf("a") >= 0

    Timer {
        interval: 1000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: root.now = new Date()
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 8
        spacing: 0
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: Qt.formatTime(root.now, (root.twelveHour ? "h:mm" : "hh:mm") + (Plasmoid.configuration.showSeconds ? ":ss" : ""))
            color: Kirigami.Theme.textColor
            font.pixelSize: Kirigami.Units.gridUnit * 4
            font.weight: Font.Light
            font.features: { "tnum": 1 }
        }
        PlasmaComponents.Label {
            Layout.alignment: Qt.AlignHCenter
            text: Qt.formatDate(root.now, Qt.locale(), Locale.LongFormat)
            opacity: 0.75
        }
    }
}
''', config=[("showSeconds", "Bool", "false")], config_page=('''
    property alias cfg_showSeconds: seconds.checked
    PlasmaComponents.CheckBox { id: seconds; Kirigami.FormData.label: "Seconds:"; text: "Show seconds" }
'''))

widget("date", "Date", "Today's day and date", "view-calendar-day", "Date and Time", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property date now: new Date()
    Timer { interval: 60000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.now = new Date() }

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 15
        Layout.preferredHeight: Kirigami.Units.gridUnit * 6
        spacing: Kirigami.Units.largeSpacing * 2
        Text {
            text: Qt.formatDate(root.now, "d")
            color: Kirigami.Theme.highlightColor
            font.pixelSize: Kirigami.Units.gridUnit * 4
            font.weight: Font.DemiBold
        }
        ColumnLayout {
            spacing: 0
            Text {
                text: Qt.formatDate(root.now, "dddd")
                color: Kirigami.Theme.textColor
                font.pixelSize: Kirigami.Units.gridUnit * 1.6
                font.weight: Font.DemiBold
            }
            PlasmaComponents.Label { text: Qt.formatDate(root.now, "MMMM yyyy"); opacity: 0.75 }
        }
    }
}
''')

widget("weather", "Weather", "Current weather and today's range (Open-Meteo)", "weather-few-clouds", "Environment and Weather", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property string place: ""
    property real temp: NaN
    property real high: NaN
    property real low: NaN
    property real wind: NaN
    property int code: -1
    property string error: ""
    readonly property string city: Plasmoid.configuration.city
    readonly property bool fahrenheit: Plasmoid.configuration.unit === "fahrenheit"

    function describe(c) {
        if (c === 0) return ["Clear", "weather-clear"];
        if (c <= 2) return ["Partly cloudy", "weather-few-clouds"];
        if (c === 3) return ["Cloudy", "weather-clouds"];
        if (c === 45 || c === 48) return ["Fog", "weather-fog"];
        if (c >= 51 && c <= 57) return ["Drizzle", "weather-showers-scattered"];
        if (c >= 61 && c <= 67) return ["Rain", "weather-showers"];
        if (c >= 71 && c <= 77) return ["Snow", "weather-snow"];
        if (c >= 80 && c <= 82) return ["Showers", "weather-showers"];
        if (c === 85 || c === 86) return ["Snow showers", "weather-snow-scattered"];
        if (c >= 95) return ["Thunderstorm", "weather-storm"];
        return ["", "weather-none-available"];
    }

    function get(url, done) {
        const xhr = new XMLHttpRequest();
        xhr.onreadystatechange = () => {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                try { done(JSON.parse(xhr.responseText)); } catch (e) { root.error = "Weather service answered strangely"; }
            } else {
                root.error = "No weather right now (offline?)";
            }
        };
        xhr.open("GET", url);
        xhr.send();
    }

    function refresh() {
        if (!city) { error = "Pick a city in the widget settings"; return; }
        get("https://geocoding-api.open-meteo.com/v1/search?count=1&name=" + encodeURIComponent(city), geo => {
            if (!geo.results || !geo.results.length) { root.error = "Couldn't find " + city; return; }
            const g = geo.results[0];
            root.place = g.name;
            get("https://api.open-meteo.com/v1/forecast?latitude=" + g.latitude + "&longitude=" + g.longitude
                + "&current=temperature_2m,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
                + (root.fahrenheit ? "&temperature_unit=fahrenheit" : ""), w => {
                root.temp = w.current.temperature_2m;
                root.code = w.current.weather_code;
                root.wind = w.current.wind_speed_10m;
                root.high = w.daily.temperature_2m_max[0];
                root.low = w.daily.temperature_2m_min[0];
                root.error = "";
            });
        });
    }

    onCityChanged: refresh()
    onFahrenheitChanged: refresh()
    Timer { interval: 30 * 60 * 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.refresh() }

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 17
        Layout.preferredHeight: Kirigami.Units.gridUnit * 7
        spacing: Kirigami.Units.largeSpacing * 2
        Kirigami.Icon {
            Layout.preferredWidth: Kirigami.Units.iconSizes.huge
            Layout.preferredHeight: Kirigami.Units.iconSizes.huge
            source: root.describe(root.code)[1]
        }
        ColumnLayout {
            spacing: 0
            Text {
                text: isNaN(root.temp) ? "--" : Math.round(root.temp) + "°"
                color: Kirigami.Theme.textColor
                font.pixelSize: Kirigami.Units.gridUnit * 3
                font.weight: Font.Light
            }
            PlasmaComponents.Label {
                text: root.error || (root.place + " · " + root.describe(root.code)[0])
                opacity: 0.8
                elide: Text.ElideRight
                Layout.maximumWidth: Kirigami.Units.gridUnit * 11
            }
            PlasmaComponents.Label {
                visible: !root.error && !isNaN(root.high)
                text: "↑ " + Math.round(root.high) + "°  ↓ " + Math.round(root.low) + "°  ·  " + Math.round(root.wind) + " km/h"
                opacity: 0.6
            }
        }
    }
}
''', config=[("city", "String", ""), ("unit", "String", "celsius")], config_page=('''
    property alias cfg_city: cityField.text
    property string cfg_unit
    PlasmaComponents.TextField { id: cityField; Kirigami.FormData.label: "City:"; placeholderText: "e.g. Oujda" }
    PlasmaComponents.ComboBox {
        Kirigami.FormData.label: "Units:"
        model: ["celsius", "fahrenheit"]
        currentIndex: Math.max(0, model.indexOf(page.cfg_unit))
        onActivated: page.cfg_unit = currentText
    }
'''))

widget("system", "System", "CPU, memory, graphics card and temperatures", "utilities-system-monitor", "System Information", HEADER + '''
import org.kde.ksysguard.sensors as Sensors

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation

    Sensors.Sensor { id: cpu; sensorId: "cpu/all/usage"; updateRateLimit: 1500 }
    Sensors.Sensor { id: ram; sensorId: "memory/physical/usedPercent"; updateRateLimit: 1500 }
    Sensors.Sensor { id: ramUsed; sensorId: "memory/physical/used"; updateRateLimit: 1500 }
    Sensors.Sensor { id: gpu; sensorId: "gpu/gpu1/usage"; updateRateLimit: 1500 }
    Sensors.Sensor { id: cpuTemp; sensorId: "cpu/all/averageTemperature"; updateRateLimit: 3000 }
    Sensors.Sensor { id: gpuTemp; sensorId: "gpu/gpu1/temperature"; updateRateLimit: 3000 }

    function has(s) { return s.value !== undefined && s.value !== null && s.formattedValue !== ""; }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 10
        spacing: Kirigami.Units.largeSpacing
        Meter { Layout.fillWidth: true; label: "CPU"; valueText: Math.round(cpu.value || 0) + " %"; fraction: (cpu.value || 0) / 100 }
        Meter { Layout.fillWidth: true; label: "Memory"; valueText: root.has(ramUsed) ? ramUsed.formattedValue : Math.round(ram.value || 0) + " %"; fraction: (ram.value || 0) / 100 }
        Meter { Layout.fillWidth: true; visible: root.has(gpu); label: "Graphics"; valueText: Math.round(gpu.value || 0) + " %"; fraction: (gpu.value || 0) / 100 }
        RowLayout {
            Layout.fillWidth: true
            visible: root.has(cpuTemp) || root.has(gpuTemp)
            PlasmaComponents.Label { text: "Temperatures"; opacity: 0.75 }
            Item { Layout.fillWidth: true }
            PlasmaComponents.Label {
                text: (root.has(cpuTemp) ? "CPU " + Math.round(cpuTemp.value) + "°" : "")
                    + (root.has(cpuTemp) && root.has(gpuTemp) ? "  ·  " : "")
                    + (root.has(gpuTemp) ? "GPU " + Math.round(gpuTemp.value) + "°" : "")
                font.weight: Font.DemiBold
            }
        }
    }
}
''', extra={"Meter.qml": METER_QML})

widget("disk", "Disk", "Free space and disk activity", "drive-harddisk", "System Information", HEADER + '''
import org.kde.ksysguard.sensors as Sensors

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Sensors.Sensor { id: used; sensorId: "disk/all/usedPercent"; updateRateLimit: 5000 }
    Sensors.Sensor { id: free; sensorId: "disk/all/free"; updateRateLimit: 5000 }
    Sensors.Sensor { id: readRate; sensorId: "disk/all/read"; updateRateLimit: 1500 }
    Sensors.Sensor { id: writeRate; sensorId: "disk/all/write"; updateRateLimit: 1500 }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 6
        spacing: Kirigami.Units.largeSpacing
        Meter { Layout.fillWidth: true; label: "Disk"; valueText: (free.formattedValue || "--") + " free"; fraction: (used.value || 0) / 100 }
        RowLayout {
            Layout.fillWidth: true
            PlasmaComponents.Label { text: "Read " + (readRate.formattedValue || "--"); opacity: 0.75 }
            Item { Layout.fillWidth: true }
            PlasmaComponents.Label { text: "Write " + (writeRate.formattedValue || "--"); opacity: 0.75 }
        }
    }
}
''', extra={"Meter.qml": METER_QML})

widget("network", "Network", "Download and upload speed", "network-wired", "System Information", HEADER + '''
import org.kde.ksysguard.sensors as Sensors

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Sensors.Sensor { id: down; sensorId: "network/all/download"; updateRateLimit: 1000 }
    Sensors.Sensor { id: up; sensorId: "network/all/upload"; updateRateLimit: 1000 }

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 5
        spacing: Kirigami.Units.largeSpacing * 3
        Repeater {
            model: [["↓", "Download", down], ["↑", "Upload", up]]
            delegate: ColumnLayout {
                id: rate
                required property var modelData
                required property int index
                spacing: 0
                Text {
                    text: rate.modelData[0] + " " + (rate.modelData[2].formattedValue || "--")
                    color: rate.index === 0 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    font.pixelSize: Kirigami.Units.gridUnit * 1.5
                    font.weight: Font.DemiBold
                }
                PlasmaComponents.Label { text: rate.modelData[1]; opacity: 0.7 }
            }
        }
    }
}
''')

widget("battery", "Battery", "Battery charge", "battery-good", "System Information", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property int percent: -1
    property string status: ""

    Shell { id: shell }
    Timer {
        interval: 30000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: shell.exec("sh -c 'for b in /sys/class/power_supply/BAT*; do [ -e \\"$b/capacity\\" ] && cat \\"$b/capacity\\" \\"$b/status\\" && break; done'", (out, code) => {
            const lines = out.trim().split("\\n");
            root.percent = lines.length >= 2 ? parseInt(lines[0]) : -1;
            root.status = lines.length >= 2 ? lines[1] : "";
        })
    }

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 14
        Layout.preferredHeight: Kirigami.Units.gridUnit * 5
        spacing: Kirigami.Units.largeSpacing * 2
        Kirigami.Icon {
            Layout.preferredWidth: Kirigami.Units.iconSizes.large
            Layout.preferredHeight: Kirigami.Units.iconSizes.large
            source: root.percent < 0 ? "battery-missing" : (root.status === "Charging" ? "battery-charging" : (root.percent > 60 ? "battery-good" : (root.percent > 20 ? "battery-low" : "battery-caution")))
        }
        ColumnLayout {
            spacing: 0
            Text {
                text: root.percent < 0 ? "No battery" : root.percent + " %"
                color: root.percent >= 0 && root.percent <= 15 ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.textColor
                font.pixelSize: Kirigami.Units.gridUnit * 2
                font.weight: Font.DemiBold
            }
            PlasmaComponents.Label { text: root.percent < 0 ? "This PC runs on mains power" : root.status; opacity: 0.7 }
        }
    }
}
''', extra={"Shell.qml": SHELL_QML})

widget("media", "Media", "What's playing, with controls", "media-playback-start", "Multimedia", HEADER + '''
import org.kde.plasma.private.mpris as Mpris

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Mpris.Mpris2Model { id: mpris }
    readonly property var player: mpris.currentPlayer
    readonly property bool playing: player ? player.playbackStatus === Mpris.PlaybackStatus.Playing : false

    fullRepresentation: RowLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 20
        Layout.preferredHeight: Kirigami.Units.gridUnit * 6
        spacing: Kirigami.Units.largeSpacing
        Rectangle {
            Layout.preferredWidth: Kirigami.Units.gridUnit * 5
            Layout.preferredHeight: Kirigami.Units.gridUnit * 5
            radius: 12
            clip: true
            color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.1)
            Image { anchors.fill: parent; source: root.player ? root.player.artUrl : ""; fillMode: Image.PreserveAspectCrop; visible: status === Image.Ready }
            Kirigami.Icon { anchors.centerIn: parent; width: parent.width / 2; height: width; source: "media-optical-audio"; visible: !root.player || !root.player.artUrl }
        }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            PlasmaComponents.Label { Layout.fillWidth: true; text: root.player && root.player.track ? root.player.track : "Nothing playing"; font.weight: Font.DemiBold; elide: Text.ElideRight }
            PlasmaComponents.Label { Layout.fillWidth: true; text: root.player ? root.player.artist : ""; opacity: 0.7; elide: Text.ElideRight }
            RowLayout {
                enabled: !!root.player
                PlasmaComponents.ToolButton { icon.name: "media-skip-backward"; onClicked: root.player.Previous() }
                PlasmaComponents.ToolButton { icon.name: root.playing ? "media-playback-pause" : "media-playback-start"; onClicked: root.playing ? root.player.Pause() : root.player.Play() }
                PlasmaComponents.ToolButton { icon.name: "media-skip-forward"; onClicked: root.player.Next() }
            }
        }
    }
}
''')

widget("calendar", "Calendar", "This month at a glance", "view-calendar-month", "Date and Time", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property date today: new Date()
    property int month: today.getMonth()
    property int year: today.getFullYear()
    readonly property int firstDay: Qt.locale().firstDayOfWeek
    Timer { interval: 60000; running: true; repeat: true; onTriggered: root.today = new Date() }

    function cells() {
        const first = new Date(year, month, 1);
        const offset = (first.getDay() - firstDay + 7) % 7;
        const days = new Date(year, month + 1, 0).getDate();
        const out = [];
        for (let i = 0; i < 42; i++) {
            const d = i - offset + 1;
            out.push(d >= 1 && d <= days ? d : 0);
        }
        return out;
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 15
        RowLayout {
            Layout.fillWidth: true
            PlasmaComponents.ToolButton { icon.name: "go-previous"; onClicked: { if (root.month === 0) { root.month = 11; root.year--; } else root.month--; } }
            PlasmaComponents.Label {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: Qt.locale().standaloneMonthName(root.month) + " " + root.year
                font.weight: Font.DemiBold
            }
            PlasmaComponents.ToolButton { icon.name: "go-next"; onClicked: { if (root.month === 11) { root.month = 0; root.year++; } else root.month++; } }
        }
        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: 7
            columnSpacing: 2
            rowSpacing: 2
            Repeater {
                model: 7
                PlasmaComponents.Label {
                    required property int index
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    text: Qt.locale().dayName((index + root.firstDay) % 7, Locale.NarrowFormat)
                    opacity: 0.6
                }
            }
            Repeater {
                model: root.cells()
                Rectangle {
                    required property int modelData
                    readonly property bool isToday: modelData === root.today.getDate() && root.month === root.today.getMonth() && root.year === root.today.getFullYear()
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: height / 2
                    color: isToday ? Kirigami.Theme.highlightColor : "transparent"
                    PlasmaComponents.Label {
                        anchors.centerIn: parent
                        text: modelData > 0 ? modelData : ""
                        color: parent.isToday ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
                    }
                }
            }
        }
    }
}
''')

widget("notes", "Notes", "A sticky note on the desktop", "knotes", "Utilities", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Timer { id: save; interval: 800; onTriggered: Plasmoid.configuration.text = area.text }

    fullRepresentation: PlasmaComponents.ScrollView {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 12
        PlasmaComponents.TextArea {
            id: area
            text: Plasmoid.configuration.text
            placeholderText: "Write a note..."
            wrapMode: TextEdit.Wrap
            background: null
            onTextChanged: save.restart()
        }
    }
}
''', config=[("text", "String", "")])

widget("todo", "To-do", "A small to-do list", "checkbox", "Utilities", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    ListModel { id: tasks }

    function load() {
        tasks.clear();
        try {
            JSON.parse(Plasmoid.configuration.items || "[]").forEach(t => tasks.append({ text: String(t.text), done: !!t.done }));
        } catch (e) {}
    }
    function store() {
        const out = [];
        for (let i = 0; i < tasks.count; i++) out.push({ text: tasks.get(i).text, done: tasks.get(i).done });
        Plasmoid.configuration.items = JSON.stringify(out);
    }
    Component.onCompleted: load()

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 14
        PlasmaComponents.Label { text: "To do"; font.weight: Font.DemiBold; font.pixelSize: Kirigami.Units.gridUnit * 1.2 }
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: tasks
            delegate: RowLayout {
                required property int index
                required property string text
                required property bool done
                width: ListView.view.width
                PlasmaComponents.CheckBox {
                    checked: done
                    onToggled: { tasks.setProperty(index, "done", checked); root.store(); }
                }
                PlasmaComponents.Label { Layout.fillWidth: true; text: parent.text; opacity: done ? 0.5 : 1; font.strikeout: done; elide: Text.ElideRight }
                PlasmaComponents.ToolButton { icon.name: "edit-delete-remove"; onClicked: { tasks.remove(index); root.store(); } }
            }
        }
        PlasmaComponents.TextField {
            Layout.fillWidth: true
            placeholderText: "Add a task and press Enter"
            onAccepted: {
                if (text.trim()) { tasks.append({ text: text.trim(), done: false }); root.store(); text = ""; }
            }
        }
    }
}
''', config=[("items", "String", "[]")])

QUOTES = [
    ["The best way to predict the future is to create it.", "Peter Drucker"],
    ["Simplicity is the ultimate sophistication.", "Leonardo da Vinci"],
    ["Stay hungry, stay foolish.", "Stewart Brand"],
    ["Well done is better than well said.", "Benjamin Franklin"],
    ["It always seems impossible until it's done.", "Nelson Mandela"],
    ["Make it work, make it right, make it fast.", "Kent Beck"],
    ["Small steps every day.", "Unknown"],
    ["Done is better than perfect.", "Sheryl Sandberg"],
    ["Knowledge is power.", "Francis Bacon"],
    ["What we think, we become.", "Buddha"],
    ["Patience is bitter, but its fruit is sweet.", "Jean-Jacques Rousseau"],
    ["The secret of getting ahead is getting started.", "Mark Twain"],
    ["Quality is not an act, it is a habit.", "Will Durant"],
    ["Seek knowledge from the cradle to the grave.", "Proverb"],
]

widget("quote", "Quote", "A new quote every day (click for another)", "format-text-blockquote", "Utilities", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    readonly property var quotes: @QUOTES@
    property int pick: Math.floor(Date.now() / 86400000) % quotes.length

    fullRepresentation: MouseArea {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 18
        Layout.preferredHeight: Kirigami.Units.gridUnit * 7
        onClicked: root.pick = (root.pick + 1) % root.quotes.length
        ColumnLayout {
            anchors.fill: parent
            Text {
                Layout.fillWidth: true
                Layout.fillHeight: true
                text: "“" + root.quotes[root.pick][0] + "”"
                color: Kirigami.Theme.textColor
                wrapMode: Text.WordWrap
                font.pixelSize: Kirigami.Units.gridUnit * 1.2
                font.italic: true
                verticalAlignment: Text.AlignVCenter
            }
            PlasmaComponents.Label { Layout.alignment: Qt.AlignRight; text: "— " + root.quotes[root.pick][1]; color: Kirigami.Theme.highlightColor }
        }
    }
}
'''.replace("@QUOTES@", json.dumps(QUOTES, ensure_ascii=False)))

widget("countdown", "Countdown", "Days left until a date", "chronometer", "Date and Time", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property date now: new Date()
    readonly property date target: new Date(Plasmoid.configuration.target)
    readonly property real left: Math.max(0, target - now)
    Timer { interval: 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.now = new Date() }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 7
        spacing: 0
        PlasmaComponents.Label { text: Plasmoid.configuration.label; opacity: 0.75 }
        Text {
            text: isNaN(root.target) ? "Set a date" : Math.floor(root.left / 86400000) + " days"
            color: Kirigami.Theme.highlightColor
            font.pixelSize: Kirigami.Units.gridUnit * 3
            font.weight: Font.DemiBold
        }
        PlasmaComponents.Label {
            visible: !isNaN(root.target)
            text: root.left === 0 ? "It's here! 🎉" : Math.floor(root.left / 3600000) % 24 + " h " + Math.floor(root.left / 60000) % 60 + " min " + Math.floor(root.left / 1000) % 60 + " s"
            opacity: 0.7
        }
    }
}
''', config=[("target", "String", "2027-01-01T00:00:00"), ("label", "String", "New Year")], config_page=('''
    property alias cfg_label: labelField.text
    property alias cfg_target: targetField.text
    PlasmaComponents.TextField { id: labelField; Kirigami.FormData.label: "Name:" }
    PlasmaComponents.TextField { id: targetField; Kirigami.FormData.label: "Date:"; placeholderText: "2027-01-01T00:00:00" }
'''))

RECENT_PY = '''#!/usr/bin/python3
"""Prints the 5 Steam games played most recently as JSON (for the steam-recent widget)."""
import glob, json, os, re
home = os.path.expanduser("~")
roots = [os.path.join(home, ".local/share/Steam"), os.path.join(home, ".steam/steam"),
         os.path.join(home, ".var/app/com.valvesoftware.Steam/.local/share/Steam")]
libraries = set()
for root in roots:
    vdf = os.path.join(root, "steamapps/libraryfolders.vdf")
    if os.path.isfile(vdf):
        libraries.add(os.path.join(root, "steamapps"))
        for path in re.findall(r'"path"\\s+"([^"]+)"', open(vdf, encoding="utf-8", errors="replace").read()):
            libraries.add(os.path.join(path.replace("\\\\\\\\", "/"), "steamapps"))
games = {}
for lib in libraries:
    for acf in glob.glob(os.path.join(lib, "appmanifest_*.acf")):
        text = open(acf, encoding="utf-8", errors="replace").read()
        get = lambda key: (re.search(r'"%s"\\s+"([^"]*)"' % key, text) or [None, ""])[1]
        appid, name = get("appid"), get("name")
        if appid and name and "Proton" not in name and "Steam Linux Runtime" not in name and "Steamworks" not in name:
            games[appid] = {"appid": appid, "name": name, "played": int(get("LastPlayed") or 0)}
print(json.dumps(sorted(games.values(), key=lambda g: -g["played"])[:5]))
'''

widget("steam-recent", "Recent games", "Your last played Steam games (click to play)", "steam", "Games", HEADER + '''
PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    property var games: []
    readonly property string script: Qt.resolvedUrl("../code/recent.py").toString().replace("file://", "")

    Shell { id: shell }
    Timer {
        interval: 5 * 60 * 1000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: shell.exec("python3 '" + root.script + "'", (out, code) => {
            try { root.games = JSON.parse(out); } catch (e) { root.games = []; }
        })
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Layout.preferredHeight: Kirigami.Units.gridUnit * 13
        PlasmaComponents.Label { text: "Recently played"; font.weight: Font.DemiBold; font.pixelSize: Kirigami.Units.gridUnit * 1.2 }
        PlasmaComponents.Label { visible: root.games.length === 0; text: "No Steam games yet"; opacity: 0.7 }
        Repeater {
            model: root.games
            PlasmaComponents.ItemDelegate {
                required property var modelData
                Layout.fillWidth: true
                icon.name: "steam_icon_" + modelData.appid
                text: modelData.name
                onClicked: shell.exec("steam steam://rungameid/" + modelData.appid, () => {})
            }
        }
        Item { Layout.fillHeight: true }
    }
}
''', extra={"Shell.qml": SHELL_QML})


def config_page_qml(body):
    """Plasma reads the cfg_* properties from the page itself, the controls go in its form."""
    lines = body.strip("\n").splitlines()
    props = "\n".join(l for l in lines if l.strip().startswith("property "))
    controls = "\n".join("    " + l for l in lines if not l.strip().startswith("property "))
    return HEADER + '''import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    id: page
''' + props + '''
    Kirigami.FormLayout {
''' + controls + '''
    }
}
'''


def main():
    for old in OUT.glob(PREFIX + "*"):
        shutil.rmtree(old)
    for type_, w in WIDGETS.items():
        pkg = OUT / (PREFIX + type_)
        (pkg / "contents/ui").mkdir(parents=True)
        meta = {
            "KPackageStructure": "Plasma/Applet",
            "KPlugin": {"Id": PREFIX + type_, "Name": "HoussamOS " + w["name"], "Description": w["description"],
                        "Icon": w["icon"], "Category": w["category"], "Authors": [{"Name": "Houssam"}],
                        "License": "GPL-2.0-or-later", "Version": "1.0",
                        "Website": "https://github.com/Houssam-2021/housos", "FormFactors": ["desktop"]},
            "X-Plasma-API-Minimum-Version": "6.0",
        }
        (pkg / "metadata.json").write_text(json.dumps(meta, indent=4, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (pkg / "contents/ui/main.qml").write_text(w["qml"], encoding="utf-8", newline="\n")
        for name, text in w["extra"].items():
            (pkg / "contents/ui" / name).write_text(text, encoding="utf-8", newline="\n")
        if w["config"]:
            (pkg / "contents/config").mkdir(parents=True)
            (pkg / "contents/config/main.xml").write_text(config_xml(w["config"]), encoding="utf-8", newline="\n")
        if w["config_page"]:
            (pkg / "contents/config/config.qml").write_text(CONFIG_MODEL, encoding="utf-8", newline="\n")
            (pkg / "contents/ui/configGeneral.qml").write_text(config_page_qml(w["config_page"]), encoding="utf-8", newline="\n")
        if type_ == "steam-recent":
            (pkg / "contents/code").mkdir(parents=True)
            (pkg / "contents/code/recent.py").write_text(RECENT_PY, encoding="utf-8", newline="\n")
        print(f"{PREFIX}{type_}")


if __name__ == "__main__":
    main()
