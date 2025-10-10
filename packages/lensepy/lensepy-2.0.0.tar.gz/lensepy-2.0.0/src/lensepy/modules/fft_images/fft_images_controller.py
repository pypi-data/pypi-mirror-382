from PyQt6.QtWidgets import QWidget
import numpy as np
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.fft_images.fft_images_views import *
from lensepy.pyqt6.widget_image_display import ImageDisplayWidget


class FFTImagesController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.top_left = ImageDisplayWidget()
        self.top_right = ImageDisplayWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        # Setup widgets

        # Signals

        self.process_FFT()

    def process_FFT(self):
        image = self.parent.variables['image']
        img_lum = np.zeros_like(image)
        if image.ndim == 3:
            r_img = image[..., 0].astype(float)
            g_img = image[..., 1].astype(float)
            b_img = image[..., 2].astype(float)
            # Luminance / Rec. 709
            img_lum = 0.2126 * r_img + 0.7152 * g_img + 0.0722 * b_img
        elif image.ndim == 2:
            # Déjà grayscale
            img_lum = image.astype(float)
        if img_lum is not None:
            fft_img = np.fft.fft2(img_lum)
            fft_img_shift = np.fft.fftshift(fft_img)
            magnitude_spectrum = 20 * np.log(np.abs(fft_img_shift) + 0.001)
            self.parent.variables['fft_image'] = magnitude_spectrum
        self.display_image_fft()

    def display_image_fft(self):
        """
        Display the main image and its FFT.
        :return:
        """
        image = self.parent.variables['image']
        self.top_left.set_image_from_array(image)
        if self.parent.variables['fft_image'] is not None:
            fft_image = self.parent.variables['fft_image']
            self.top_right.set_image_from_array(fft_image)


