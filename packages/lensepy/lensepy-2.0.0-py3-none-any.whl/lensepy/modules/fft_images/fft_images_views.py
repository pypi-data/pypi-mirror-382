import cv2
import numpy as np
from lensepy import translate
from lensepy.css import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QWidget, QLabel, QPushButton, QFrame, QCheckBox, QSizePolicy
)
from lensepy.images.conversion import resize_image_ratio
import pyqtgraph as pg


class ImagesOpeningWidget(QWidget):
    """
    Widget to display image opening options.
    """

    image_opened = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()

        h_line = QFrame()
        h_line.setFrameShape(QFrame.Shape.HLine)  # Trait horizontal
        h_line.setFrameShadow(QFrame.Shadow.Sunken)  # Effet "enfoncé" (optionnel)
        layout.addWidget(h_line)

        label = QLabel(translate('image_opening_dialog'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.open_button = QPushButton(translate('image_opening_button'))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.setFixedHeight(BUTTON_HEIGHT)
        self.open_button.clicked.connect(self.handle_opening)
        layout.addWidget(self.open_button)

        layout.addStretch()
        self.setLayout(layout)

    def handle_opening(self):
        sender = self.sender()
        if sender == self.open_button:
            self.open_button.setStyleSheet(actived_button)
            im_ok = self.open_image()
            if im_ok:
                self.open_button.setStyleSheet(unactived_button)

    def open_image(self) -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   "", "Images (*.png *.jpg *.jpeg)")
        if file_path != '':
            image_array = imread_rgb(file_path)
            self.parent.get_variables()['image'] = image_array
            self.image_opened.emit('image_opened')
            return True
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return False


class ImagesInfosWidget(QWidget):
    """
    Widget to display image infos.
    """
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        layout = QVBoxLayout()

        self.image = None

        label = QLabel(translate('image_infos_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        layout.addWidget(make_hline())

        self.label_w = LabelWidget(translate("image_infos_label_w"), '', 'pixels')
        layout.addWidget(self.label_w)
        self.label_h = LabelWidget(translate("image_infos_label_h"), '', 'pixels')
        layout.addWidget(self.label_h)

        layout.addWidget(make_hline())

        self.label_type = LabelWidget(translate("image_infos_label_type"), '', '')
        layout.addWidget(self.label_type)

        layout.addStretch()
        self.setLayout(layout)
        self.hide()

    def update_infos(self, image: np.ndarray):
        """
        Update information from image.
        :param image:   Displayed image.
        """
        self.image = image
        if self.image is not None:
            self.show()
            self.label_w.set_value(f'{self.image.shape[1]}')
            self.label_h.set_value(f'{self.image.shape[0]}')
            if self.image.ndim == 2:
                self.label_type.set_value(f'GrayScale')
            else:
                self.label_type.set_value(f'RGB')
        else:
            self.hide()




# TO MOVE TO LENSEPY  --> version 2


class FFTViewerWidget(QWidget):
    def __init__(self, image: np.ndarray, parent=None):
        """
        Display the FFT of an image (from a ndarray).
        :param image_path:  Path of the image.
        """
        super().__init__()
        self.parent = parent

        img_lum = None
        if image.ndim == 3:
            r_img = image[..., 0].astype(float)
            g_img = image[..., 1].astype(float)
            b_img = image[..., 2].astype(float)
            # Luminance / Rec. 709
            img_lum = 0.2126 * r_img + 0.7152 * g_img + 0.0722 * b_img
        elif image.ndim == 2:
            # Déjà grayscale
            img_lum = image.astype(float)

        # Process FFT
        if img_lum is not None:
            fft_img = np.fft.fft2(img_lum)
            fft_img_shift = np.fft.fftshift(fft_img)
            magnitude_spectrum = 20 * np.log(np.abs(fft_img_shift) + 0.001)

        # Display FFT
        layout = QVBoxLayout(self)
        self.graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graph_widget)

        view = self.graph_widget.addViewBox()
        img_item = pg.ImageItem(magnitude_spectrum)
        view.addItem(img_item)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from matplotlib import pyplot as plt
    app = QApplication(sys.argv)
    image = cv2.imread('./robot.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    w = FFTViewerWidget(image)
    w.resize(800, 600)
    w.show()

    # Exemple : image RGB aléatoire


    sys.exit(app.exec())
