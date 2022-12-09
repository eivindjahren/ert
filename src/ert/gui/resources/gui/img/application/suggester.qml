import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3

ApplicationWindow {
    visible: true
    width: 600
    height: 500
    title: "Problems detected"

    property string messages: "Placeholder message"

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        TextField {
            text: messages
            font.pixelSize: 24
        }
        RowLayout {
            Button {
                text: "Copy"
            }

            Button {
                text: "Close"
            }

            Button {
                text: "Try running ERT"
            }
        }
    }

}