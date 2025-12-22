import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Controls.Material 6.5

ApplicationWindow {
    width: 360
    height: 140
    visible: true
    title: "Updater"

    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint

    Material.theme: Material.Dark
    Material.accent: Material.Purple

    Rectangle {
        anchors.fill: parent
        radius: 12
        color: "#1e1e1e"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Label {
            id: statusLabel
            text: "Starting…"
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
        }

        ProgressBar {
            id: updatebar
            from: 0
            to: 100
            value: 0
            Layout.fillWidth: true
        }

        Label {
            text: Math.round(updatebar.value) + "%"
            opacity: 0.7
            Layout.alignment: Qt.AlignHCenter
        }
    }

    Connections {
        target: updater

        function onProgressChanged(v) {
            updatebar.value = v
        }

        function onStatusChanged(text) {
            statusLabel.text = text
        }

        function onFinished(ok) {
            if (ok) {
                Qt.quit()
            }
        }
    }
}
