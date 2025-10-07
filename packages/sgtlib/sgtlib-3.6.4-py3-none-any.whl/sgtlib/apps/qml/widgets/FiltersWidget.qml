import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Imagine as Imagine

ColumnLayout {
    id: imgFilterButtons
    Layout.preferredHeight: 32
    Layout.preferredWidth: parent.width
    Layout.topMargin: 10
    Layout.bottomMargin: 5
    visible: mainController.display_image()
    enabled: mainController.enable_img_controls()


    RowLayout {
        Layout.alignment: Qt.AlignHCenter

        Imagine.Button {
            id: btnShowImgHistogram
            text: "Image Histogram"
            padding: 5
            enabled: mainController.enable_img_controls()
            onClicked: imgHistogramWindow.visible = true
        }

        Rectangle {
            width: 1
            height: 18
            color: "#d0d0d0"
        }

        Imagine.Button {
            id: btnShowImgColors
            text: "Image Colors"
            padding: 5
            enabled: mainController.enable_img_controls()
            onClicked: imgColorsWindow.visible = true
        }

    }


    Connections {
        target: mainController

        function onImageChangedSignal() {
            // Force refresh
            imgFilterButtons.visible = mainController.display_image();
            imgFilterButtons.enabled = mainController.enable_img_controls();
        }

        function onShowImageFilterControls(allow) {

            if (allow) {
                btnShowImgHistogram.enabled = mainController.enable_img_controls();
                btnShowImgColors.enabled = mainController.enable_img_controls();
            } else {
                btnShowImgHistogram.enabled = allow;
                btnShowImgColors.enabled = allow;
            }

        }

    }

}