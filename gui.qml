import QtQuick
import "ui"
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

ApplicationWindow {
    id: app

    width: 970
    height: 530
    minimumWidth: width
    maximumWidth: width
    minimumHeight: height
    maximumHeight: height

    visible: true
    title: "Mippo Launcher"

    Material.theme: Material.Dark
    Material.accent: Material.Purple

    color: "#111111"

    property string launchFontPath: Qt.resolvedUrl("font/Freedom-10eM.ttf")

    readonly property string launchFontFamily: (launchFont.status === FontLoader.Ready
                                                && launchFont.name
                                                && launchFont.name.length)
                                                ? launchFont.name
                                                : "Segoe UI"

    FontLoader {
        id: launchFont
        source: launchFontPath
    }

    ListModel {
        id: slidesModel
        ListElement { img: "slides/slide1.png"; title: "Change Logs"; buttonText: "READ MORE"; link: "https://github.com/M1PPosu/m1pplauncher/releases"; buttonVisible: true }
        ListElement { img: "slides/slide2.png"; title: "M1Lazer Temporarily Shutdown"; buttonText: "Learn More"; link: "https://discord.com/channels/1330284945146384556/1408883425816870912/1497771704993185923"; buttonVisible: true }
        ListElement { img: "slides/slide3.png"; title: "Join the Discord"; buttonText: "JOIN"; link: "https://discord.gg/2ujhGaZ6Z9"; buttonVisible: true }
    }

    readonly property int pad: 18
    readonly property int radius: 14

    readonly property color bg: "#111111"
    readonly property color surface: "#151515"
    readonly property color surface2: "#1b1b1b"
    readonly property color border: "#2a2a2a"
    readonly property color borderSoft: "#242424"

    readonly property color textStrong: "#ffffff"
    readonly property color textSoft: "#d0d0d0"
    readonly property color textMuted: "#a6a6a6"

    readonly property color accent: "#ce93d8"

    component PillButton: TabButton {
        id: t
        implicitHeight: 42
        implicitWidth: 120
        font.pixelSize: 13
        font.weight: 900

        background: Rectangle {
            radius: 12
            color: t.checked ? "#1e1e1e" : "#111111"
            border.color: t.checked ? app.border : "#00000000"
            border.width: t.checked ? 1 : 0
        }

        contentItem: Text {
            text: t.text
            color: t.checked ? app.textStrong : app.textMuted
            font.pixelSize: 13
            font.weight: 900
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: pad
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Item {
                    width: 38
                    height: 38

                    Image {
                        anchors.fill: parent
                        source: "icon.png"
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        mipmap: true
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: "Mippo Launcher v4.0b"
                        color: app.textStrong
                        font.pixelSize: 16
                        font.weight: 950
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 56
            radius: 14
            color: "#141414"
            border.color: "#242424"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 7
                spacing: 8

                TabBar {
                    id: tabBar
                    Layout.fillWidth: true
                    height: 42
                    spacing: 8

                    background: Rectangle {
                        radius: 12
                        color: "#111111"
                        border.color: "#242424"
                        border.width: 1
                    }

                    PillButton { text: "HOME" }
                    PillButton { text: "NEWS" }
                    PillButton { text: "SETTINGS" }
                    PillButton { text: "MODS" }
                    PillButton { text: "ABOUT" }

                    onCurrentIndexChanged: {
                        window.execguifn(880811, 0)
                        stackLayout.currentIndex = currentIndex
                    }
                }
            }
        }

        StackLayout {
            id: stackLayout
            Layout.fillWidth: true
            Layout.fillHeight: true

            HomePage {
                appTheme: app
                customServerChecked: typeof switch_hidelauncher !== "undefined" ? switch_hidelauncher : false
            }

            NewsPage {
                appTheme: app 
                slidesModel: slidesModel
            }

            OtherPages {
                appTheme: app
                pageName: "settings"
                customServerChecked: typeof switch_hidelauncher !== "undefined" ? switch_hidelauncher : false
                debugInfoChecked: typeof switch_launchinfo !== "undefined" ? switch_launchinfo : true
                patcherChecked: typeof switch_patcher !== "undefined" ? switch_patcher : true
                tosuChecked: typeof switch_tosu !== "undefined" ? switch_tosu : true
            }

            OtherPages {
                appTheme: app
                pageName: "mods"
                customServerChecked: typeof switch_hidelauncher !== "undefined" ? switch_hidelauncher : false
                debugInfoChecked: typeof switch_launchinfo !== "undefined" ? switch_launchinfo : true
                patcherChecked: typeof switch_patcher !== "undefined" ? switch_patcher : true
                tosuChecked: typeof switch_tosu !== "undefined" ? switch_tosu : true
            }

            OtherPages {
                appTheme: app
                pageName: "about"
                customServerChecked: typeof switch_hidelauncher !== "undefined" ? switch_hidelauncher : false
                debugInfoChecked: typeof switch_launchinfo !== "undefined" ? switch_launchinfo : true
                patcherChecked: typeof switch_patcher !== "undefined" ? switch_patcher : true
                tosuChecked: typeof switch_tosu !== "undefined" ? switch_tosu : true
            }
        }
    }
}
 