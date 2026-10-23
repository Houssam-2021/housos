import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

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
