import QtQuick
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
        ListElement { img: "slides/slide1.png"; title: "Change Logs"; buttonText: "READ MORE"; link: "https://github.com/M1PPosu/m1pplauncher"; buttonVisible: true }
        ListElement { img: "slides/slide2.png"; title: "Check out our Brand-New Hytale Server!!"; buttonText: "Learn More"; link: "https://discord.gg/SD9uztGnRR"; buttonVisible: true }
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

    component Card: Item {
        id: card
        property int r: app.radius
        property color fill: app.surface
        property color stroke: app.borderSoft
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
                     : (b.hovered ? Qt.lighter(app.accent, 1.06) : app.accent))

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
                        font.family: app.launchFontFamily
                        font.pixelSize: 30
                        font.weight: 1000
                        renderType: Text.NativeRendering
                    }

                    Text {
                        anchors.centerIn: parent
                        text: labelRow.label.charAt(index)
                        color: "#ffffff"
                        font.family: app.launchFontFamily
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

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: pad
        spacing: 12

        // header
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
                        text: "Mippo Launcher v4.0B"
                        color: app.textStrong
                        font.pixelSize: 16
                        font.weight: 950
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }

                    Text {
                        text: "osu!stable • osu!lazer • mods • server routing"
                        color: app.textMuted
                        font.pixelSize: 11
                        font.weight: 700
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }
            }
        } 
        // nav bar
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

            // home
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: app.bg

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
                                        color: app.textStrong
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
                                        TabButton { text: "osu!lazer"; implicitHeight: 42; font.pixelSize: 13; font.weight: 900 }

                                        visible: !useCustomServer.checked
                                        onCurrentIndexChanged: window.execguifn(880811, 0)
                                    }

                                    TextField {
                                        objectName: "serverinp"
                                        anchors.fill: parent
                                        visible: useCustomServer.checked
                                        placeholderText: qsTr("Custom server domain e.g:(m1pposu.dev)")

                                        leftPadding: 14
                                        rightPadding: 14
                                        topPadding: 10
                                        bottomPadding: 10
                                        color: app.textStrong

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
                                                color: app.textStrong
                                                font.pixelSize: 13
                                                font.weight: 900
                                                Layout.fillWidth: true
                                                elide: Text.ElideRight
                                            }

                                            Text {
                                                text: "Quick access"
                                                color: app.textMuted
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
                                            text: "Tip: Enable “Use custom server” in Settings to connect to another server."
                                            color: app.textMuted
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
                                        color: app.textStrong
                                        font.pixelSize: 16
                                        font.weight: 950
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }

                                    Rectangle {
                                        height: 28
                                        radius: 10
                                        color: "#161616"
                                        border.color: "#2a2a2a"
                                        border.width: 2

                                        Layout.preferredWidth: liveRow.implicitWidth + 20
                                        Layout.minimumWidth: Layout.preferredWidth
                                        Layout.maximumWidth: Layout.preferredWidth

                                        RowLayout {
                                            id: liveRow
                                            Layout.alignment: Qt.AlignVCenter
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 10 
                                            anchors.topMargin: 0
                                            anchors.bottomMargin: 0
                                            spacing: 8
                                            //keep in mind, this is a complete lie. This is by any means NOT a rectangle. no diddy
                                            Rectangle {
                                                width: 8
                                                height: 8
                                                radius: 999
                                                color: "#35d07f"
                                                opacity: 0.95
                                            }

                                            Text {
                                                text: "Online"
                                                color: "#cfcfcf"
                                                font.pixelSize: 13
                                                font.weight: 800
                                                
                                                Layout.alignment: Qt.AlignVCenter
                                                verticalAlignment: Text.AlignVCenter
                                                baselineOffset: 0
                                            }
                                        }
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
                                                        color: app.textSoft
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

            // news
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: app.bg

                    Card {
                        anchors.fill: parent
                        fill: "#151515"
                        stroke: "#242424"
                        clip: true

                        Rectangle {
                            id: newsMask
                            width: parent.width
                            height: parent.height
                            radius: app.radius
                            visible: false
                        }

                        SwipeView {
                            id: newsCarousel
                            anchors.fill: parent
                            interactive: true
                            currentIndex: 0
                            clip: true

                            Repeater {
                                model: slidesModel
                                delegate: Item {
                                    width: newsCarousel.width
                                    height: newsCarousel.height
                                    clip: true

                                    Image {
                                        anchors.fill: parent
                                        source: img
                                        fillMode: Image.PreserveAspectCrop
                                        smooth: true
                                        mipmap: true
                                        layer.enabled: true
                                        layer.effect: OpacityMask { maskSource: newsMask }
                                    }
                                }
                            }
                        }

                        Timer {
                            interval: 5000
                            repeat: true
                            running: slidesModel.count > 1
                            onTriggered: newsCarousel.currentIndex = (newsCarousel.currentIndex + 1) % newsCarousel.count
                        }

                        Image {
                            source: "fade.png"
                            anchors.fill: parent
                            fillMode: Image.PreserveAspectCrop
                            layer.enabled: true
                            layer.effect: OpacityMask { maskSource: newsMask }
                            opacity: 0.95
                        }

                        PageIndicator {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 118
                            count: slidesModel.count
                            currentIndex: newsCarousel.currentIndex
                            interactive: true
                        }

                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            height: 110
                            radius: app.radius
                            color: "#121212"
                            opacity: 0.90
                            border.color: "#2a2a2a"
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 12

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    Text {
                                        text: "Latest"
                                        color: app.textMuted
                                        font.pixelSize: 12
                                        font.weight: 900
                                    }

                                    Text {
                                        color: app.textStrong
                                        font.pixelSize: 22
                                        font.weight: 950
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                        text: slidesModel.count > 0 ? slidesModel.get(newsCarousel.currentIndex).title : "No news available"
                                    }
                                }

                                SecondaryButton {
                                    Layout.preferredWidth: 160
                                    visible: slidesModel.count > 0 && slidesModel.get(newsCarousel.currentIndex).buttonVisible
                                    text: slidesModel.count > 0 ? slidesModel.get(newsCarousel.currentIndex).buttonText : ""
                                    onClicked: if (slidesModel.count > 0) Qt.openUrlExternally(slidesModel.get(newsCarousel.currentIndex).link)
                                }
                            }
                        }
                    }
                }
            }

            // settings
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: app.bg

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
                                color: app.textStrong
                                font.pixelSize: 18
                                font.weight: 950
                                Layout.fillWidth: true
                            }

                            Text {
                                text: "General launcher behavior"
                                color: app.textMuted
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
                                        checked: switch_hidelauncher
                                        onClicked: window.execguifn(111, checked ? 1 : 0)
                                    }

                                    Switch {
                                        objectName: "id11"
                                        text: qsTr("Show launch info")
                                        checked: switch_launchinfo
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

            // mods
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: app.bg

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
                                color: app.textStrong
                                font.pixelSize: 18
                                font.weight: 950
                                Layout.fillWidth: true
                            }

                            Text {
                                text: "Enable built-in mods and manage custom .mmod files"
                                color: app.textMuted
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
                                        checked: switch_patcher
                                        onClicked: window.execguifn(0, checked ? 1 : 0)
                                    }

                                    Switch {
                                        objectName: "id1"
                                        text: qsTr("tosu (KotRik & Cherry)")
                                        checked: switch_tosu
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
                                            color: app.textMuted
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

            // about
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: app.bg

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
                                        text: "About"
                                        color: app.textStrong
                                        font.pixelSize: 18
                                        font.weight: 950
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }

                                    Text {
                                        text: "Support, links, and quick reference"
                                        color: app.textMuted
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
                                            color: app.textStrong
                                            font.pixelSize: 13
                                            font.weight: 900
                                        }

                                        Text {
                                            text: "Mippo Launcher routes osu!stable and osu!lazer to private servers and can load built-in or custom mods."
                                            color: app.textSoft
                                            font.pixelSize: 13
                                            font.weight: 650
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }

                                        Item { Layout.fillHeight: true }

                                        Text {
                                            text: "When reporting issues, include your latest log file."
                                            color: app.textMuted
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
                                            color: app.textStrong
                                            font.pixelSize: 13
                                            font.weight: 900
                                        }

                                        SecondaryButton { text: "GitHub"; Layout.fillWidth: true; onClicked: window.execguifn(990, 0) }
                                        SecondaryButton { text: "Discord"; Layout.fillWidth: true; onClicked: Qt.openUrlExternally("https://discord.gg/8pwCjTFHbT") }
                                        SecondaryButton { text: "Ko-fi"; Layout.fillWidth: true; onClicked: Qt.openUrlExternally("https://ko-fi.com/m1ppo") }

                                        Item { Layout.fillHeight: true }

                                        Text {
                                            text: "License: GPLv3"
                                            color: app.textMuted
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
}
