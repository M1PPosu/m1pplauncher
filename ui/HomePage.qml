import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

Item {
    id: page

    property var appTheme
    property bool customServerChecked: false

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

    component PrimaryButton: Button {
        id: b
        height: 44
        padding: 14
        hoverEnabled: true

        scale: b.down ? 0.985 : (b.hovered ? 1.01 : 1.0)
        Behavior on scale { NumberAnimation { duration: 110; easing.type: Easing.OutCubic } }

        background: Item {
            anchors.fill: parent

            Rectangle {
                id: bg
                anchors.fill: parent
                radius: 12

                color: !b.enabled ? "#3a3a3a"
                     : (b.down ? "#b980c5"
                     : (b.hovered ? Qt.lighter(page.appTheme.accent, 1.06) : page.appTheme.accent))

                border.width: 1
                border.color: !b.enabled ? "#2a2a2a"
                             : (b.hovered ? "#3a2a3f" : "#2a2a2a")

                Behavior on color { ColorAnimation { duration: 120 } }
                Behavior on border.color { ColorAnimation { duration: 120 } }

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    height: 1
                    radius: 1
                    color: "#ffffff"
                    opacity: b.enabled && b.hovered && !b.down ? 0.16 : 0.0
                    Behavior on opacity { NumberAnimation { duration: 120 } }
                }
            }

            DropShadow {
                anchors.fill: bg
                source: bg
                horizontalOffset: 0
                verticalOffset: b.down ? 3 : 7
                radius: b.down ? 14 : 20
                samples: 26
                color: "#000000"
                opacity: !b.enabled ? 0.0 : (b.hovered ? 0.40 : 0.28)
                Behavior on opacity { NumberAnimation { duration: 120 } }
                Behavior on verticalOffset { NumberAnimation { duration: 120 } }
                Behavior on radius { NumberAnimation { duration: 120 } }
            }
        }

        contentItem: RowLayout {
            id: labelRow
            anchors.fill: parent
            anchors.leftMargin: 18
            anchors.rightMargin: 18
            spacing: 0

            property string label: b.text.toUpperCase()

            Repeater {
                model: labelRow.label.length

                delegate: Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Text {
                        anchors.centerIn: parent
                        anchors.horizontalCenterOffset: 1
                        anchors.verticalCenterOffset: 1
                        text: labelRow.label.charAt(index)
                        color: "#000000"
                        opacity: 0.45
                        font.family: page.appTheme.launchFontFamily
                        font.pixelSize: 30
                        font.weight: 1000
                        renderType: Text.NativeRendering
                    }

                    Text {
                        anchors.centerIn: parent
                        text: labelRow.label.charAt(index)
                        color: "#ffffff"
                        font.family: page.appTheme.launchFontFamily
                        font.pixelSize: 30
                        font.weight: 1000
                        renderType: Text.NativeRendering
                    }
                }
            }
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

    Rectangle {
        anchors.fill: parent
        color: page.appTheme.bg

        RowLayout {
            anchors.fill: parent
            spacing: 12

            Card {
                id: launchCard
                fill: "#151515"
                stroke: "#242424"
                Layout.fillHeight: true
                Layout.preferredWidth: dbgCard.visible ? 430 : 0
                Layout.fillWidth: !dbgCard.visible

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Text {
                            text: "Launch"
                            color: page.appTheme.textStrong
                            font.pixelSize: 18
                            font.weight: 950
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: "#242424"; opacity: 0.9 }

                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 46

                        TabBar {
                            id: toggleBar
                            objectName: "serversel"
                            anchors.fill: parent

                            background: Rectangle {
                                radius: 12
                                color: "#121212"
                                border.color: "#2a2a2a"
                                border.width: 1
                            }

                            TabButton { text: "osu!stable"; implicitHeight: 42; font.pixelSize: 13; font.weight: 900 }
                            TabButton { text: "osu!lazer"; enabled: false; opacity: 0.45; implicitHeight: 42; font.pixelSize: 13; font.weight: 900 }

                            visible: !page.customServerChecked
                            onCurrentIndexChanged: window.execguifn(880811, 0)
                        }

                        TextField {
                            objectName: "serverinp"
                            anchors.fill: parent
                            visible: page.customServerChecked
                            placeholderText: qsTr("Custom server domain e.g:(m1pposu.dev)")

                            leftPadding: 14
                            rightPadding: 14
                            topPadding: 10
                            bottomPadding: 10
                            color: page.appTheme.textStrong

                            background: Rectangle {
                                radius: 12
                                color: "#121212"
                                border.color: "#2a2a2a"
                                border.width: 1
                            }
                        }
                    }

                    Card {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 120
                        shadow: false
                        fill: "#1b1b1b"
                        stroke: "#242424"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                Text {
                                    text: "Shortcuts"
                                    color: page.appTheme.textStrong
                                    font.pixelSize: 13
                                    font.weight: 900
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                Text {
                                    text: "Quick access"
                                    color: page.appTheme.textMuted
                                    font.pixelSize: 11
                                    font.weight: 800
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                SecondaryButton { text: "Mods folder"; Layout.fillWidth: true; onClicked: window.execguifn(6969, 0) }
                                SecondaryButton { text: "Discord"; Layout.fillWidth: true; onClicked: window.execguifn(991, 0) }
                                SecondaryButton { text: "GitHub"; Layout.fillWidth: true; onClicked: window.execguifn(990, 0) }
                            }

                            Text {
                                text: 'Tip: Enable "Use custom server" in Settings to connect to another server.'
                                color: page.appTheme.textMuted
                                font.pixelSize: 11
                                font.weight: 650
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    PrimaryButton {
                        objectName: "playbtn"
                        text: "LAUNCH"
                        Layout.fillWidth: true
                        onClicked: window.execguifn(2137, 0)
                    }
                }
            }

            Card {
                id: dbgCard
                objectName: "dbg2"
                Layout.fillWidth: true
                Layout.fillHeight: true
                fill: "#151515"
                stroke: "#242424"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Text {
                            objectName: "dbg1"
                            text: "Launch info"
                            color: page.appTheme.textStrong
                            font.pixelSize: 16
                            font.weight: 950
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: "#242424"; opacity: 0.9 }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 12
                        color: "#121212"
                        border.color: "#2a2a2a"
                        border.width: 1
                        clip: true

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8

                            TabBar {
                                id: infoTabs
                                Layout.fillWidth: true
                                height: 34
                                spacing: 8

                                background: Rectangle {
                                    radius: 10
                                    color: "#141414"
                                    border.color: "#242424"
                                    border.width: 1
                                }

                                TabButton { text: "STATUS"; font.pixelSize: 12; font.weight: 900; implicitHeight: 30 }
                                TabButton { text: "CONSOLE"; font.pixelSize: 12; font.weight: 900; implicitHeight: 30 }

                                onCurrentIndexChanged: infoStack.currentIndex = currentIndex
                            }

                            StackLayout {
                                id: infoStack
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                currentIndex: infoTabs.currentIndex

                                Item {
                                    Flickable {
                                        anchors.fill: parent
                                        contentWidth: width
                                        contentHeight: dbgText.implicitHeight
                                        clip: true

                                        Text {
                                            id: dbgText
                                            objectName: "dbg"
                                            width: parent.width
                                            color: page.appTheme.textSoft
                                            font.pixelSize: 13
                                            font.weight: 650
                                            wrapMode: Text.WordWrap
                                            text: "Client channel: NULL\nLoaded mods: NULL\nConnection: NULL\nCustom server: NULL"
                                        }
                                    }
                                }

                                Item {
                                    Flickable {
                                        id: consoleFlick
                                        anchors.fill: parent
                                        contentWidth: width
                                        contentHeight: consoleText.implicitHeight
                                        clip: true

                                        Text {
                                            id: consoleText
                                            width: parent.width
                                            color: "#cfcfcf"
                                            font.pixelSize: 12
                                            font.family: "Consolas"
                                            wrapMode: Text.Wrap
                                            text: (typeof consoleOut !== "undefined" && consoleOut && consoleOut.text !== undefined) ? consoleOut.text : ""
                                            onTextChanged: consoleFlick.contentY = Math.max(0, consoleFlick.contentHeight - consoleFlick.height)
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
}
