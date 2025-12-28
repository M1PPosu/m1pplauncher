import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

ApplicationWindow {
    minimumWidth: 600
    minimumHeight: 600
    maximumHeight: minimumHeight
    maximumWidth: minimumWidth
    visible: true
    title: "M1PP Launcher"
    Material.theme: Material.Dark
    Material.accent: Material.Purple
    color: "#111111"
    GroupBox {
        objectName: "step1"
        width: 600
        height: 600
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "Welcome to the M1PP Launcher\nInstallation wizard!"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            color: "#ffffff"
            font.pixelSize: 16
            font.weight: 400
            text: "This installer will guide you through the process of installing\nM1PP Launcher on your PC. Click the 'Next' button to continue"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Button {
            id: nextbtn
            onClicked: window.display_step(2)
            text: "Next"
            y: 490
            x: 390
            width: 160
        }
        Button {
            id: prevbtn
            text: "Previous"
            y: 490
            x: 50
            width: 160
            enabled: false
        }
    }
    GroupBox {
        objectName: "step2"
        visible: false
        width: 600
        height: 600
        x: 0
        y: 0
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "License"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            objectName: "installf"
            color: "#ffffff"
            font.pixelSize: 16
            font.weight: 400
            text: "This software is licensed under the GPL v3\nlicense. You can access the full license terms by clicking\nthe button below this notice."
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        Button {
            onClicked: window.display_step(93)
            text: "View license"
            y: 420
            x: 390
            width: 330
            anchors.horizontalCenter: parent.horizontalCenter
        }
        Button {
            onClicked: window.display_step(3)
            text: "I accept"
            y: 490
            x: 390
            width: 330
            anchors.horizontalCenter: parent.horizontalCenter
        }
        
    }
    GroupBox {
        objectName: "step3"
        visible: false
        width: 600
        height: 600
        x: 0
        y: 0
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "Install osu!stable"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        Text {
            color: "#ffffff"
            font.pixelSize: 16
            font.weight: 400
            text: "We weren't able to auto-detect your osu! installation.\nPlease download osu! using the button below.\nAfter installing, click Next to continue."
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        Button {
            onClicked: window.display_step(2942)
            text: "Download osu!stable"
            y: 420
            x: 390
            width: 330
            anchors.horizontalCenter: parent.horizontalCenter
        }
        Button {
            onClicked: window.display_step(78)
            text: "Next"
            y: 490
            x: 390
            width: 330
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
    GroupBox {
        objectName: "step4"
        width: 600
        height: 600
        visible: false
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "Select installation path"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            color: "#ffffff"
            font.pixelSize: 16
            font.weight: 400
            text: "Select the folder where you want to install M1PP Launcher\n\n\n\n\n\n"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        TextField {
            placeholderText: qsTr("Installation path")
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            objectName: "pathsel"
            width: 500
            x: 45
            
        }
        Button {
            onClicked: window.display_step(79)
            objectName: "pathselbtn"
            text: "Browse files"
            anchors.horizontalCenter: parent.horizontalCenter
            y: 335
            width: 200
        }
        Button {
            onClicked: window.display_step(5)
            text: "Next"
            y: 490
            x: 390
            width: 160
        }
        Button {
            onClicked: window.display_step(33)
            text: "Previous"
            y: 490
            x: 50
            width: 160
        }
    }
    GroupBox {
        objectName: "step5"
        width: 600
        height: 600
        visible: false
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "Summary"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        
        Rectangle {
            y: 240
            radius: 8
            color: "#1d1d1d"
            anchors.horizontalCenter: parent.horizontalCenter
            width: 470
            height: 100
                        
            Text {
                objectName: "summarytext"
                color: "#ffffff"
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                y: 30
                font.pixelSize: 14
                text: ""
            }
        }
        Button {
            onClicked: window.display_step(6)
            text: "Next"
            y: 490
            x: 390
            width: 160
        }
        Button {
            onClicked: window.display_step(4)
            text: "Previous"
            y: 490
            x: 50
            width: 160
        }
    }
    GroupBox {
        objectName: "step6"
        width: 600
        height: 600
        visible: false
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "Installing..."
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        Text {
            objectName: "curtext"
            color: "#ffffff"
            font.pixelSize: 16
            font.weight: 400
            text: "Installing: main.exe\n\n"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        ProgressBar {
            objectName: "curbar"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            width: 490
            value: 0.0
        }

    }
    GroupBox {
        objectName: "step7"
        visible: false
        width: 600
        height: 600
        x: 0
        y: 0
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "Setup complete"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            color: "#ffffff"
            font.pixelSize: 16
            font.weight: 400
            text: "M1PP Launcher has been installed! You can now launch it\nfrom your application menu."
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Button {
            onClicked: window.display_step(8)
            text: "Close"
            y: 490
            x: 390
            width: 330
            anchors.horizontalCenter: parent.horizontalCenter
        }
        
    }

    GroupBox {
        objectName: "step89"
        visible: false
        width: 600
        height: 600
        x: 0
        y: 0
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "Setup failed"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            objectName: "errpath"
            color: "#ffffff"
            font.pixelSize: 16
            font.weight: 400
            text: "An error has occured during the installation.\nSetup logs are located at unknown"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Button {
            onClicked: window.display_step(8)
            text: "Close"
            y: 490
            x: 390
            width: 330
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
    GroupBox {
        objectName: "step999"
        width: 600
        height: 600
        visible: false
        Text {
            color: "#ffffff"
            y: 50
            font.pixelSize: 30
            font.weight: 700
            text: "Select game path"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            color: "#ffffff"
            font.pixelSize: 16
            font.weight: 400
            text: "Select the folder containing your osu! stable installation\n\n\n\n\n\n"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        TextField {
            placeholderText: qsTr("Installation path")
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            objectName: "opathsel"
            width: 500
            x: 45
            
        }
        Button {
            onClicked: window.display_step(99979)
            objectName: "opathselbtn"
            text: "Browse files"
            anchors.horizontalCenter: parent.horizontalCenter
            y: 335
            width: 200
        }
        Button {
            onClicked: window.display_step(9990)
            text: "Next"
            y: 490
            x: 390
            width: 160
        }
    }  
}