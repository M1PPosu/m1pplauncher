import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

Item {
    id: page

    property var appTheme
    property var slidesModel

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

    Rectangle {
        anchors.fill: parent
        color: page.appTheme.bg

        Card {
            anchors.fill: parent
            fill: "#151515"
            stroke: "#242424"
            clip: true

            Rectangle {
                id: newsMask
                width: parent.width
                height: parent.height
                radius: page.appTheme.radius
                visible: false
            }

            SwipeView {
                id: newsCarousel
                anchors.fill: parent
                interactive: true
                currentIndex: 0
                clip: true

                Repeater {
                    model: page.slidesModel

                    delegate: Item {
                        width: newsCarousel.width
                        height: newsCarousel.height
                        clip: true

                        Image {
                            anchors.fill: parent
                            source: "../" + img
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
                running: page.slidesModel.count > 1
                onTriggered: newsCarousel.currentIndex = (newsCarousel.currentIndex + 1) % newsCarousel.count
            }

            Image {
                source: "../fade.png"
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
                count: page.slidesModel.count
                currentIndex: newsCarousel.currentIndex
                interactive: true
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 110
                radius: page.appTheme.radius
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
                            color: page.appTheme.textMuted
                            font.pixelSize: 12
                            font.weight: 900
                        }

                        Text {
                            color: page.appTheme.textStrong
                            font.pixelSize: 22
                            font.weight: 950
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                            text: page.slidesModel.count > 0 ? page.slidesModel.get(newsCarousel.currentIndex).title : "No news available"
                        }
                    }

                    SecondaryButton {
                        Layout.preferredWidth: 160
                        visible: page.slidesModel.count > 0 && page.slidesModel.get(newsCarousel.currentIndex).buttonVisible
                        text: page.slidesModel.count > 0 ? page.slidesModel.get(newsCarousel.currentIndex).buttonText : ""
                        onClicked: if (page.slidesModel.count > 0) Qt.openUrlExternally(page.slidesModel.get(newsCarousel.currentIndex).link)
                    }
                }
            }
        }
    }
}
