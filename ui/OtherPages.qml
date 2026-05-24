import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

Item {
    id: page

    property var appTheme
    property string pageName: "settings"

    property bool customServerChecked: false
    property bool debugInfoChecked: true
    property bool patcherChecked: true
    property bool tosuChecked: true

    component Card: Item {
        id: card
        property int r: page.appTheme.radius
        property color fill: page.appTheme.surface
        property color stroke: page.appTheme.borderSoft 
        property int strokeWidth: 1
        property bool shadow: true

        implicitWidth: 520
        implicitHeight: 200

        Rectangle {
            id: plate
            anchors.fill: parent
            radius: card.r
            color: card.fill
            border.color: card.stroke
            border.width: card.strokeWidth
        }

        DropShadow {
            anchors.fill: plate
            source: plate
            horizontalOffset: 0
            verticalOffset: 6
            radius: 18
            samples: 26
            color: "#000000"
            opacity: card.shadow ? 0.35 : 0.0
            visible: card.shadow
        }
    }

    component SecondaryButton: Button {
        id: b
        height: 40
        hoverEnabled: true
        padding: 14

        font.pixelSize: 13
        font.weight: 800

        background: Rectangle {
            radius: 12
            color: b.down ? "#222222" : (b.hovered ? "#1c1c1c" : "#161616")
            border.color: "#2a2a2a"
            border.width: 1
        }

        contentItem: Text {
            text: b.text
            color: "#ffffff"
            font.pixelSize: 13
            font.weight: 800
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }

    Loader {
        anchors.fill: parent
        sourceComponent: page.pageName === "settings" ? settingsPage
                       : page.pageName === "mods" ? modsPage
                       : aboutPage
    }

    Component {
        id: settingsPage

        Item {
            Rectangle {
                anchors.fill: parent
                color: page.appTheme.bg

                Card {
                    anchors.fill: parent
                    fill: "#151515"
                    stroke: "#242424"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12

                        Text {
                            text: "Settings"
                            color: page.appTheme.textStrong
                            font.pixelSize: 18
                            font.weight: 950
                            Layout.fillWidth: true
                        }

                        Text {
                            text: "General launcher behavior"
                            color: page.appTheme.textMuted
                            font.pixelSize: 12
                            font.weight: 700
                            Layout.fillWidth: true
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: "#242424"; opacity: 0.9 }

                        Card {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 200
                            shadow: false
                            fill: "#1b1b1b"
                            stroke: "#242424"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                Switch {
                                    id: useCustomServer
                                    objectName: "id111"
                                    text: qsTr("Use custom server (osu!stable only.)")
                                    checked: page.customServerChecked
                                    onClicked: window.execguifn(111, checked ? 1 : 0)
                                }

                                Switch {
                                    objectName: "id11"
                                    text: qsTr("Show launch info")
                                    checked: page.debugInfoChecked
                                    onClicked: window.execguifn(11, checked ? 1 : 0)
                                }

                                Item { Layout.fillHeight: true }
                            }
                        }

                        Item { Layout.fillHeight: true }
                    }
                }
            }
        }
    }

    Component {
        id: modsPage

        Item {
            Rectangle {
                anchors.fill: parent
                color: page.appTheme.bg

                Card {
                    anchors.fill: parent
                    fill: "#151515"
                    stroke: "#242424"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12

                        Text {
                            text: "Mods"
                            color: page.appTheme.textStrong
                            font.pixelSize: 18
                            font.weight: 950
                            Layout.fillWidth: true
                        }

                        Text {
                            text: "Enable built-in mods and manage custom .mmod files"
                            color: page.appTheme.textMuted
                            font.pixelSize: 12
                            font.weight: 700
                            Layout.fillWidth: true
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: "#242424"; opacity: 0.9 }

                        Card {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 260
                            shadow: false
                            fill: "#1b1b1b"
                            stroke: "#242424"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                Switch {
                                    objectName: "id0"
                                    text: qsTr("RelaxPatcher (rushiiMachine)")
                                    checked: page.patcherChecked
                                    onClicked: window.execguifn(0, checked ? 1 : 0)
                                }

                                Switch {
                                    objectName: "id1"
                                    text: qsTr("tosu (KotRik & Cherry)")
                                    checked: page.tosuChecked
                                    onClicked: window.execguifn(1, checked ? 1 : 0)
                                }

                                Item { Layout.fillHeight: true }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10

                                    SecondaryButton {
                                        text: "Open custom mods folder"
                                        Layout.preferredWidth: 220
                                        onClicked: window.execguifn(6969, 0)
                                    }

                                    Item { Layout.fillWidth: true }

                                    Text {
                                        text: "Drop .mmod files into /mods"
                                        color: page.appTheme.textMuted
                                        font.pixelSize: 12
                                        font.weight: 700
                                        horizontalAlignment: Text.AlignRight
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }
                                }
                            }
                        }

                        Item { Layout.fillHeight: true }
                    }
                }
            }
        }
    }

    Component {
        id: aboutPage

        Item {
            Rectangle {
                anchors.fill: parent
                color: page.appTheme.bg

                Card {
                    anchors.fill: parent
                    fill: "#151515"
                    stroke: "#242424"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            Item {
                                width: 44
                                height: 44

                                Image {
                                    anchors.fill: parent
                                    source: "../icon.png"
                                    fillMode: Image.PreserveAspectFit
                                    smooth: true
                                    mipmap: true
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Text {
                                    text: "About"
                                    color: page.appTheme.textStrong
                                    font.pixelSize: 18
                                    font.weight: 950
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                Text {
                                    text: "Support, links, and quick reference"
                                    color: page.appTheme.textMuted
                                    font.pixelSize: 12
                                    font.weight: 700
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                            }
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: "#242424"; opacity: 0.9 }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: 12

                            Card {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                shadow: false
                                fill: "#1b1b1b"
                                stroke: "#242424"

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 14
                                    spacing: 10

                                    Text {
                                        text: "Overview"
                                        color: page.appTheme.textStrong
                                        font.pixelSize: 13
                                        font.weight: 900
                                    }

                                    Text {
                                        text: "Mippo Launcher routes osu!stable to private servers and can load built-in or custom mods."
                                        color: page.appTheme.textSoft
                                        font.pixelSize: 13
                                        font.weight: 650
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }

                                    Item { Layout.fillHeight: true }

                                    Text {
                                        text: "When reporting issues, include your latest log file."
                                        color: page.appTheme.textMuted
                                        font.pixelSize: 11
                                        font.weight: 700
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                }
                            }

                            Card {
                                Layout.preferredWidth: 320
                                Layout.fillHeight: true
                                shadow: false
                                fill: "#1b1b1b"
                                stroke: "#242424"

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 14
                                    spacing: 10

                                    Text {
                                        text: "Links"
                                        color: page.appTheme.textStrong
                                        font.pixelSize: 13
                                        font.weight: 900
                                    }

                                    SecondaryButton { text: "GitHub"; Layout.fillWidth: true; onClicked: window.execguifn(990, 0) }
                                    SecondaryButton { text: "Discord"; Layout.fillWidth: true; onClicked: Qt.openUrlExternally("https://discord.gg/8pwCjTFHbT") }
                                    SecondaryButton { text: "Ko-fi"; Layout.fillWidth: true; onClicked: Qt.openUrlExternally("https://ko-fi.com/m1ppo") }

                                    Item { Layout.fillHeight: true }

                                    Text {
                                        text: "License: GPLv3"
                                        color: page.appTheme.textMuted
                                        font.pixelSize: 11
                                        font.weight: 800
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
