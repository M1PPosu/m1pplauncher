import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

ApplicationWindow {
    id: app
    width: 980
    height: 660
    minimumWidth: width
    maximumWidth: width
    minimumHeight: height
    maximumHeight: height

    visible: true
    title: "M1PP Launcher Installer"

    Material.theme: Material.Dark
    Material.accent: Material.Purple

    color: "#0b0c10"

    readonly property int pad: 26
    readonly property int radius: 14

    readonly property color panel: "#11141b"
    readonly property color panel2: "#151a23"
    readonly property color border: "#232a38"
    readonly property color textStrong: "#ffffff"
    readonly property color textSoft: "#b8bfd0"
    readonly property color textMuted: "#8e97ac"

    readonly property color btnBg: "#1b2230"
    readonly property color btnBgHover: "#232c3d"
    readonly property color btnBorder: "#2b354a"

    readonly property color primaryBg: "#b986ff"
    readonly property color primaryBgHover: "#caa2ff"
    readonly property color primaryText: "#0b0c10"

    readonly property int currentIndex:
        step1.visible   ? 0 :
        step2.visible   ? 1 :
        step3.visible   ? 2 :
        step4.visible   ? 3 :
        step5.visible   ? 4 :
        step6.visible   ? 5 :
        step7.visible   ? 6 :
        step89.visible  ? 6 :
        step999.visible ? 2 :
        0

    component GhostButton: Button {
        id: b
        property bool compact: false
        height: compact ? 34 : 38
        padding: 14

        font.pixelSize: 13
        font.weight: 600

        contentItem: Text {
            text: b.text
            color: b.enabled ? app.textStrong : "#6f7688"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        background: Rectangle {
            radius: 10
            color: b.enabled ? (b.hovered ? app.btnBgHover : app.btnBg) : "#141923"
            border.color: b.enabled ? app.btnBorder : "#1a2030"
            border.width: 1
        }
    }

    component PrimaryButton: Button {
        id: b
        property bool compact: false
        height: compact ? 34 : 38
        padding: 14

        font.pixelSize: 13
        font.weight: 700

        contentItem: Text {
            text: b.text
            color: b.enabled ? app.primaryText : "#6f7688"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        background: Rectangle {
            radius: 10
            color: b.enabled ? (b.hovered ? app.primaryBgHover : app.primaryBg) : "#141923"
            border.color: b.enabled ? "transparent" : "#1a2030"
            border.width: 1
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: pad
        spacing: 18

        Rectangle {
            Layout.preferredWidth: 260
            Layout.fillHeight: true
            radius: radius
            color: panel
            border.color: border
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Text {
                        text: "M1PP Launcher"
                        color: textStrong
                        font.pixelSize: 18
                        font.weight: 800
                        Layout.fillWidth: true
                    }
                    Text {
                        text: "Installer"
                        color: textSoft
                        font.pixelSize: 12
                        font.weight: 500
                        Layout.fillWidth: true
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: border
                    opacity: 0.8
                }

                Text {
                    text: "Steps"
                    color: textMuted
                    font.pixelSize: 12
                    font.weight: 700
                    Layout.fillWidth: true
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    function stepOpacity(idx) {
                        if (idx < app.currentIndex) return 0.85
                        if (idx === app.currentIndex) return 1.0
                        return 0.45
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        opacity: stepOpacity(0)

                        Rectangle {
                            width: 8; height: 8
                            radius: 8
                            color: (app.currentIndex >= 0) ? Material.accentColor : "#3a4256"
                        }
                        Text {
                            text: "Welcome"
                            color: (app.currentIndex === 0) ? textStrong : textSoft
                            font.pixelSize: 13
                            font.weight: (app.currentIndex === 0) ? 800 : 500
                            Layout.fillWidth: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        opacity: stepOpacity(1)

                        Rectangle {
                            width: 8; height: 8
                            radius: 8
                            color: (app.currentIndex >= 1) ? Material.accentColor : "#3a4256"
                        }
                        Text {
                            text: "License"
                            color: (app.currentIndex === 1) ? textStrong : textSoft
                            font.pixelSize: 13
                            font.weight: (app.currentIndex === 1) ? 800 : 500
                            Layout.fillWidth: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        opacity: stepOpacity(2)

                        Rectangle {
                            width: 8; height: 8
                            radius: 8
                            color: (app.currentIndex >= 2) ? Material.accentColor : "#3a4256"
                        }
                        Text {
                            text: "Install osu!stable"
                            color: (app.currentIndex === 2) ? textStrong : textSoft
                            font.pixelSize: 13
                            font.weight: (app.currentIndex === 2) ? 800 : 500
                            Layout.fillWidth: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        opacity: stepOpacity(3)

                        Rectangle {
                            width: 8; height: 8
                            radius: 8
                            color: (app.currentIndex >= 3) ? Material.accentColor : "#3a4256"
                        }
                        Text {
                            text: "Install path"
                            color: (app.currentIndex === 3) ? textStrong : textSoft
                            font.pixelSize: 13
                            font.weight: (app.currentIndex === 3) ? 800 : 500
                            Layout.fillWidth: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        opacity: stepOpacity(4)

                        Rectangle {
                            width: 8; height: 8
                            radius: 8
                            color: (app.currentIndex >= 4) ? Material.accentColor : "#3a4256"
                        }
                        Text {
                            text: "Summary"
                            color: (app.currentIndex === 4) ? textStrong : textSoft
                            font.pixelSize: 13
                            font.weight: (app.currentIndex === 4) ? 800 : 500
                            Layout.fillWidth: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        opacity: stepOpacity(5)

                        Rectangle {
                            width: 8; height: 8
                            radius: 8
                            color: (app.currentIndex >= 5) ? Material.accentColor : "#3a4256"
                        }
                        Text {
                            text: "Installing"
                            color: (app.currentIndex === 5) ? textStrong : textSoft
                            font.pixelSize: 13
                            font.weight: (app.currentIndex === 5) ? 800 : 500
                            Layout.fillWidth: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        opacity: stepOpacity(6)

                        Rectangle {
                            width: 8; height: 8
                            radius: 8
                            color: (app.currentIndex >= 6) ? Material.accentColor : "#3a4256"
                        }
                        Text {
                            text: "Complete"
                            color: (app.currentIndex === 6) ? textStrong : textSoft
                            font.pixelSize: 13
                            font.weight: (app.currentIndex === 6) ? 800 : 500
                            Layout.fillWidth: true
                        }
                    }
                }

                Item { Layout.fillHeight: true }

                Rectangle {
                    Layout.fillWidth: true
                    radius: 12
                    color: "#121826"
                    border.color: "#2b354a"
                    border.width: 1
                    height: 62

                    Rectangle {
                        width: 4
                        radius: 4
                        anchors.left: parent.left
                        anchors.leftMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                        height: parent.height - 18
                        color: Material.accentColor
                    }

                    Text {
                        text: "Tip: If you hit an error, open logs from\nthe failure screen."
                        color: textSoft
                        font.pixelSize: 12
                        anchors.left: parent.left
                        anchors.leftMargin: 22
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: radius
            color: panel
            border.color: border
            border.width: 1

            Rectangle {
                height: 3
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                color: Material.accentColor
                opacity: 0.95
                radius: 2
            }

            Item {
                anchors.fill: parent
                anchors.margins: 22

                Item {
                    id: step1
                    objectName: "step1"
                    anchors.fill: parent
                    visible: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Install M1PP Launcher"
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                text: "This wizard will install M1PP Launcher and configure osu! to launch with your private server settings."
                                color: textSoft
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: radius
                            color: panel2
                            border.color: border
                            border.width: 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10

                                Text {
                                    text: "What this will do"
                                    color: textStrong
                                    font.pixelSize: 15
                                    font.weight: 800
                                    Layout.fillWidth: true
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 1
                                    color: border
                                    opacity: 0.7
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 10

                                    Rectangle {
                                        Layout.fillWidth: true
                                        radius: 12
                                        color: "#0f1420"
                                        border.color: "#2b354a"
                                        border.width: 1
                                        implicitHeight: row1.implicitHeight + 22

                                        RowLayout {
                                            id: row1
                                            anchors.fill: parent
                                            anchors.margins: 11
                                            spacing: 10

                                            Rectangle { width: 8; height: 8; radius: 8; color: Material.accentColor; opacity: 0.95 }

                                            Text {
                                                text: "Detect your osu!stable install (or ask you to select it)"
                                                color: textSoft
                                                font.pixelSize: 13
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        radius: 12
                                        color: "#0f1420"
                                        border.color: "#2b354a"
                                        border.width: 1
                                        implicitHeight: row2.implicitHeight + 22

                                        RowLayout {
                                            id: row2
                                            anchors.fill: parent
                                            anchors.margins: 11
                                            spacing: 10

                                            Rectangle { width: 8; height: 8; radius: 8; color: Material.accentColor; opacity: 0.95 }

                                            Text {
                                                text: "Install M1PP Launcher into your chosen folder"
                                                color: textSoft
                                                font.pixelSize: 13
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        radius: 12
                                        color: "#0f1420"
                                        border.color: "#2b354a"
                                        border.width: 1
                                        implicitHeight: row3.implicitHeight + 22

                                        RowLayout {
                                            id: row3
                                            anchors.fill: parent
                                            anchors.margins: 11
                                            spacing: 10

                                            Rectangle { width: 8; height: 8; radius: 8; color: Material.accentColor; opacity: 0.95 }

                                            Text {
                                                text: "Set up required files and mods folder"
                                                color: textSoft
                                                font.pixelSize: 13
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        radius: 12
                                        color: "#0f1420"
                                        border.color: "#2b354a"
                                        border.width: 1
                                        implicitHeight: row4.implicitHeight + 22

                                        RowLayout {
                                            id: row4
                                            anchors.fill: parent
                                            anchors.margins: 11
                                            spacing: 10

                                            Rectangle { width: 8; height: 8; radius: 8; color: Material.accentColor; opacity: 0.95 }

                                            Text {
                                                text: "Finish and let you launch normally"
                                                color: textSoft
                                                font.pixelSize: 13
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }
                                }

                                Item { Layout.fillHeight: true }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            GhostButton {
                                text: "Previous"
                                enabled: false
                                Layout.preferredWidth: 120
                            }

                            Item { Layout.fillWidth: true }

                            PrimaryButton {
                                text: "Next"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(2)
                            }
                        }
                    }
                }

                Item {
                    id: step2
                    objectName: "step2"
                    anchors.fill: parent
                    visible: false

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "License"
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                objectName: "installf"
                                text: "This software is licensed under the GPL v3\nlicense. You can access the full license terms by clicking\nthe button below this notice."
                                color: textSoft
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 96
                            radius: radius
                            color: panel2
                            border.color: border
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 12

                                Rectangle {
                                    width: 4
                                    Layout.fillHeight: true
                                    radius: 4
                                    color: Material.accentColor
                                    opacity: 0.95
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4

                                    Text {
                                        text: "GPL v3"
                                        color: textStrong
                                        font.pixelSize: 14
                                        font.weight: 800
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }

                                    Text {
                                        text: "Use the button below to view the full license terms."
                                        color: textSoft
                                        font.pixelSize: 13
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }

                        Item { Layout.fillHeight: true }
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            GhostButton {
                                text: "View license"
                                Layout.preferredWidth: 140
                                onClicked: window.display_step(93)
                            }

                            Item { Layout.fillWidth: true }

                            PrimaryButton {
                                text: "I accept"
                                Layout.preferredWidth: 140
                                onClicked: window.display_step(3)
                            }
                        }
                    }
                }

                Item {
                    id: step3
                    objectName: "step3"
                    anchors.fill: parent
                    visible: false

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Install osu!stable"
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                text: "We weren't able to auto-detect your osu! installation.\nPlease download osu! using the button below.\nAfter installing, click Next to continue."
                                color: textSoft
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }

                        Item { Layout.fillHeight: true }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            GhostButton {
                                text: "Download osu!stable"
                                Layout.preferredWidth: 170
                                onClicked: window.display_step(2942)
                            }

                            Item { Layout.fillWidth: true }

                            PrimaryButton {
                                text: "Next"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(78)
                            }
                        }
                    }
                }

                Item {
                    id: step4
                    objectName: "step4"
                    anchors.fill: parent
                    visible: false

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Select installation path"
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                text: "Select the folder where you want to install M1PP Launcher"
                                color: textSoft
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }

                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            Rectangle {
                                width: Math.min(parent.width, 620)
                                height: 260
                                anchors.centerIn: parent
                                radius: radius
                                color: panel2
                                border.color: border
                                border.width: 1

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 22
                                    spacing: 14

                                    Text {
                                        text: "Installation path"
                                        color: textMuted
                                        font.pixelSize: 12
                                        font.weight: 700
                                        Layout.fillWidth: true
                                    }

                                    TextField {
                                        objectName: "pathsel"
                                        Layout.fillWidth: true
                                        placeholderText: qsTr("")
                                        font.pixelSize: 13

                                        leftPadding: 14
                                        rightPadding: 14
                                        topPadding: 10
                                        bottomPadding: 10

                                        background: Rectangle {
                                            radius: 10
                                            color: "#0f1420"
                                            border.color: "#2b354a"
                                            border.width: 1
                                        }
                                    }

                                    Item { Layout.fillHeight: true }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 10

                                        GhostButton {
                                            objectName: "pathselbtn"
                                            text: "Browse files"
                                            compact: true
                                            Layout.preferredWidth: 130
                                            onClicked: window.display_step(79)
                                        }

                                        Item { Layout.fillWidth: true }
                                    }
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            GhostButton {
                                text: "Previous"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(33)
                            }

                            Item { Layout.fillWidth: true }

                            PrimaryButton {
                                text: "Next"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(5)
                            }
                        }
                    }
                }

                Item {
                    id: step5
                    objectName: "step5"
                    anchors.fill: parent
                    visible: false

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Summary"
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                text: ""
                                color: textSoft
                                font.pixelSize: 13
                                Layout.fillWidth: true
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: radius
                            color: panel2
                            border.color: border
                            border.width: 1

                            Text {
                                objectName: "summarytext"
                                anchors.centerIn: parent
                                width: parent.width - 60
                                wrapMode: Text.WordWrap
                                horizontalAlignment: Text.AlignHCenter
                                color: textSoft
                                font.pixelSize: 13
                                text: ""
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            GhostButton {
                                text: "Previous"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(4)
                            }

                            Item { Layout.fillWidth: true }

                            PrimaryButton {
                                text: "Next"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(6)
                            }
                        }
                    }
                }

                Item {
                    id: step6
                    objectName: "step6"
                    anchors.fill: parent
                    visible: false

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Installing..."
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                text: ""
                                color: textSoft
                                font.pixelSize: 13
                                Layout.fillWidth: true
                            }
                        }

                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            ColumnLayout {
                                anchors.centerIn: parent
                                width: Math.min(parent.width, 620)
                                spacing: 14

                                Text {
                                    objectName: "curtext"
                                    text: "Installing: main.exe\n\n"
                                    color: textSoft
                                    font.pixelSize: 13
                                    wrapMode: Text.WordWrap
                                    horizontalAlignment: Text.AlignHCenter
                                    Layout.fillWidth: true
                                }

                                ProgressBar {
                                    objectName: "curbar"
                                    Layout.fillWidth: true
                                    value: 0.0
                                }
                            }
                        }
                    }
                }

                Item {
                    id: step7
                    objectName: "step7"
                    anchors.fill: parent
                    visible: false

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Setup complete"
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                text: "M1PP Launcher has been installed! You can now launch it\nfrom your application menu."
                                color: textSoft
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }

                        Item { Layout.fillHeight: true }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            Item { Layout.fillWidth: true }

                            PrimaryButton {
                                text: "Close"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(8)
                            }
                        }
                    }
                }

                Item {
                    id: step89
                    objectName: "step89"
                    anchors.fill: parent
                    visible: false

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Setup failed"
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                objectName: "errpath"
                                text: "An error has occured during the installation.\nSetup logs are located at unknown"
                                color: textSoft
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }

                        Item { Layout.fillHeight: true }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            GhostButton {
                                text: "Open logs folder"
                                Layout.preferredWidth: 160
                                onClicked: window.display_step(8901)
                            }

                            Item { Layout.fillWidth: true }

                            PrimaryButton {
                                text: "Close"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(8)
                            }
                        }
                    }
                }

                Item {
                    id: step999
                    objectName: "step999"
                    anchors.fill: parent
                    visible: false

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Select game path"
                                color: textStrong
                                font.pixelSize: 30
                                font.weight: 900
                                Layout.fillWidth: true
                            }
                            Text {
                                text: "Select the folder containing your osu! stable installation"
                                color: textSoft
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }

                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            Rectangle {
                                width: Math.min(parent.width, 620)
                                height: 260
                                anchors.centerIn: parent
                                radius: radius
                                color: panel2
                                border.color: border
                                border.width: 1

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 22
                                    spacing: 14

                                    Text {
                                        text: "Installation path"
                                        color: textMuted
                                        font.pixelSize: 12
                                        font.weight: 700
                                        Layout.fillWidth: true
                                    }

                                    TextField {
                                        objectName: "opathsel"
                                        Layout.fillWidth: true
                                        placeholderText: qsTr("")
                                        font.pixelSize: 13

                                        leftPadding: 14
                                        rightPadding: 14
                                        topPadding: 10
                                        bottomPadding: 10

                                        background: Rectangle {
                                            radius: 10
                                            color: "#0f1420"
                                            border.color: "#2b354a"
                                            border.width: 1
                                        }
                                    }

                                    Item { Layout.fillHeight: true }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 10

                                        GhostButton {
                                            objectName: "opathselbtn"
                                            text: "Browse files"
                                            compact: true
                                            Layout.preferredWidth: 130
                                            onClicked: window.display_step(99979)
                                        }

                                        Item { Layout.fillWidth: true }
                                    }
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            Item { Layout.fillWidth: true }

                            PrimaryButton {
                                text: "Next"
                                Layout.preferredWidth: 120
                                onClicked: window.display_step(9990)
                            }
                        }
                    }
                }
            }
        }
    }
}
