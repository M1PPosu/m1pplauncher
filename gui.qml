import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

ApplicationWindow {
    minimumWidth: 970
    minimumHeight: 530
    maximumHeight: minimumHeight
    maximumWidth: minimumWidth
    visible: true
    title: "M1PP Launcher"
    Material.theme: Material.Dark
    Material.accent: Material.Purple
    color: "#111111"

    ColumnLayout {
        anchors.fill: parent
        Layout.fillHeight: true
        height: 200
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            height: 57
            font.pixelSize: 14
            background: Rectangle { color: "#111111" }
            Layout.topMargin: 7
            Layout.leftMargin: 47
            Layout.rightMargin: 47
            TabButton { 
                text: "HOME"
                implicitHeight: 57
            }
            TabButton { 
                text: "NEWS"
                implicitHeight: 57
            }
            TabButton { 
                text: "SETTINGS"
                implicitHeight: 57
            }
            TabButton { 
                text: "MODS"
                implicitHeight: 57
            }
            TabButton { 
                text: "ABOUT"
                implicitHeight: 57
            }

            onCurrentIndexChanged: {
                window.execguifn(880811, 0)
                stackLayout.currentIndex = currentIndex
            }
        }

        // StackLayout for each tab's content
        StackLayout {
            id: stackLayout
            Layout.fillWidth: true
            Layout.fillHeight: true
            Material.accent: Material.Purple
            // Tab 1 Content
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: "#111111"
                    
                                        
                    TabBar {
                        id: toggleBar
                        objectName: "serversel"
                        width: 280
                        y: 48
                        background: Rectangle { color: "#111111" }
                        anchors.horizontalCenter: parent.horizontalCenter
                        TabButton {
                            text: "osu!stable"
                            Layout.alignment:Qt.AlignHCenter
                        }

                        TabButton {
                            text: "osu!lazer"
                            Layout.alignment:Qt.AlignHCenter
                        }

                        onCurrentIndexChanged: {
                            window.execguifn(880811, 0)
                        }
                    }
                    TextField {
                        visible: false
                        placeholderText: qsTr("Custom server")
                        objectName: "serverinp"
                        width: 280
                        y: 48
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    Button {
                        objectName: "playbtn"
                        text: "LAUNCH"
                        y: 138
                        background: Rectangle {
                            radius: 3
                            color: "#ce93d8"
                        }
                        width: 147
                        anchors.horizontalCenter: parent.horizontalCenter
                        onClicked: window.execguifn(2137, 0)
                    }
                    Rectangle {
                        objectName: "dbg2"
                        y: 208
                        radius: 8
                        color: "#1d1d1d"
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: 548
                        height: 220
                        
                        Text {
                            objectName: "dbg1"
                            color: "#ffffff"
                            anchors.horizontalCenter: parent.horizontalCenter
                            horizontalAlignment: Text.AlignHCenter
                            y: 50
                            font.pixelSize: 14
                            font.weight: 600
                            text: "Launch info"
                        }
                        Text {
                            objectName: "dbg"
                            color: "#ffffff"
                            anchors.horizontalCenter: parent.horizontalCenter
                            horizontalAlignment: Text.AlignHCenter
                            y: 50
                            font.pixelSize: 14
                            text: "\n\nClient channel: NULL\nLoaded mods: NULL\nConnection: NULL\nCustom server: NULL"
                        }
                    }
                }
            }

            // Tab 2 Content
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: "#111111"
                    Rectangle {
                        y: 45
                        radius: 14
                        color: "#1d1d1d"
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: 876
                        height: 388
                        Image {
                                    objectName: "newsimg"
                                    source: 'unknown.png'
                                    width: parent.width
                                    height: parent.height
                                    anchors.centerIn: parent
                                    fillMode: Image.PreserveAspectCrop
                                    layer.enabled: true
                                    layer.effect: OpacityMask {
                                        maskSource: mask
                                    }
                                }
                        Image {
                                    id: imgfade
                                    source: 'fade.png'
                                    width: parent.width
                                    height: parent.height
                                    anchors.centerIn: parent
                                    fillMode: Image.PreserveAspectCrop
                                    layer.enabled: true
                                    layer.effect: OpacityMask {
                                        maskSource: mask
                                    }
                                }
                            
                                Rectangle {
                                    id: mask
                                    width: parent.width
                                    height: parent.height
                                    radius: 14
                                    visible: false
                                }
                        Text {
                            objectName: "newstext"
                            color: "#ffffff"
                            y: 313
                            x: 26
                            font.pixelSize: 24
                            font.weight: 600
                            text: "You are offline"
                        }
                        Button {
                            objectName: "newsbtn"
                            text: "READ MORE"
                            y: 300
                            x: 700
                            width: 147
                            visible: false
                            onClicked: window.execguifn(420, 0)
                        }
                    }    
                }
            }

            // Tab 3 Content
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: "#111111"
                    Text {
                        color: "#ffffff"
                        y: 30
                        x: 40
                        font.pixelSize: 20
                        font.weight: 800
                        text: "General"
                    }
                    Switch {
                        objectName: "id111"
                        text: qsTr("Use custom server")
                        y: 96
                        x: 40
                        checked: switch_hidelauncher
                        onClicked: window.execguifn(111, checked)
                    }
                    Switch {
                        objectName: "id11"
                        text: qsTr("Show launch info")
                        y: 146
                        x: 40
                        checked: switch_launchinfo
                        onClicked: window.execguifn(11, checked)
                    }
                }
            }

            // Tab 4 Content
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: "#111111"
                    Text {
                        color: "#ffffff"
                        y: 30
                        x: 40
                        font.pixelSize: 20
                        font.weight: 800
                        text: "Mods"
                    }
                    Switch {
                        objectName: "id0"
                        text: qsTr("RelaxPatcher (rushiiMachine)")
                        y: 96
                        x: 40
                        checked: switch_hidelauncher
                        onClicked: window.execguifn(0, checked)
                    }
                    Switch {
                        objectName: "id1"
                        text: qsTr("tosu (KotRik & Cherry)")
                        y: 146
                        x: 40
                        checked: switch_launchinfo
                        onClicked: window.execguifn(1, checked)
                    }
                    Button {
                        id: cmodlink
                        text: "Custom mods"
                        x: 40
                        y: 256
                        width: 147
                        onClicked: window.execguifn(6969, 0)
                    }
                }
            }

            // Tab 5 Content
            Item {
                Button {
                    id: ghlink
                    text: "GitHub"
                    y: 158
                    width: 147
                    anchors.horizontalCenter: parent.horizontalCenter
                    onClicked: window.execguifn(990, 0)
                }
                Button {
                    id: dclink
                    text: "Discord"
                    y: 208
                    width: 147
                    anchors.horizontalCenter: parent.horizontalCenter
                    onClicked: window.execguifn(991, 0)
                }
            }
        }
    }
}