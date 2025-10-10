"""
image_display_widget.py
=======================

PyQt6 widget for displaying images from numpy arrays in a QGraphicsView.
Supports both grayscale and RGB images, with optional text overlay and
customizable bits depth.

Features
--------

- Supports grayscale and RGB images
- Converts higher bit-depth images to 8-bit for display
- Optional overlay text
- Maintains aspect ratio in QGraphicsView
- Customizable background color

Usage Example
-------------

.. code-block:: python

    import sys
    import numpy as np
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = ImageDisplayWidget(bg_color='white')

    # Create a test RGB image 256x256
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image_from_array(test_image, text="Test Image")
    widget.show()
    sys.exit(app.exec())


Author : Julien VILLEMEJANE / LEnsE - IOGS
Date   : 2025-10-09
"""

import numpy as np
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont, QPainter
from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsView,
    QVBoxLayout, QGraphicsTextItem, QWidget
)


class ImageDisplayWidget(QWidget):
    """Widget d'affichage d'image depuis un array NumPy, avec ajustement automatique à la vue."""

    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent)
        self.bits_depth = 8
        self.zoom = zoom
        self.pixmap_item = None
        self.text_item = None

        # --- Scene & View ---
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() |
                                 QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scene.setBackgroundBrush(QColor(bg_color))

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
    def set_image_from_array(self, pixels_array: np.ndarray, text: str = ''):
        """Affiche une image NumPy (grayscale ou RGB)."""
        if pixels_array is None:
            return

        # Nettoie la scène sans la recréer (meilleur pour les performances)
        self.scene.clear()
        self.pixmap_item = None
        self.text_item = None

        qimage = self._convert_array_to_qimage(pixels_array)
        if qimage is None:
            return

        # Crée le pixmap et l'ajoute à la scène
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        # Ajoute le texte (facultatif)
        if text:
            font = QFont('Arial', 12)
            self.text_item = QGraphicsTextItem(text)
            self.text_item.setFont(font)
            self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
            self.text_item.setPos(5, pixmap.height() - 25)
            self.scene.addItem(self.text_item)

        # Ajustement automatique (avec délai 0 pour attendre la taille réelle du widget)
        QTimer.singleShot(0, self._update_view_fit)

    def set_bits_depth(self, value_depth: int):
        """Définit la profondeur de bits des pixels."""
        self.bits_depth = value_depth

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _convert_array_to_qimage(self, pixels: np.ndarray) -> QImage | None:
        """Convertit un tableau numpy en QImage compatible avec PyQt."""
        pixels = np.ascontiguousarray(pixels)
        if pixels.ndim == 2:
            # Grayscale
            if self.bits_depth > 8:
                scale = 2 ** (self.bits_depth - 8)
                pixels = (pixels / scale).astype(np.uint8)
            else:
                pixels = pixels.astype(np.uint8)
            h, w = pixels.shape
            return QImage(pixels.data, w, h, pixels.strides[0], QImage.Format.Format_Grayscale8)

        elif pixels.ndim == 3:
            h, w, c = pixels.shape
            if c == 3:
                pixels = pixels.astype(np.uint8)
                return QImage(pixels.data, w, h, pixels.strides[0], QImage.Format.Format_RGB888)
            else:
                raise ValueError(f"Unsupported number of channels: {c}")

        else:
            raise ValueError(f"Unsupported image shape: {pixels.shape}")

    def _update_view_fit(self):
        """Adapte la vue à la taille de l'image, sans scrollbars."""
        if not self.pixmap_item:
            return
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        """Ajuste l'image automatiquement lors du redimensionnement."""
        super().resizeEvent(event)
        self._update_view_fit()


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = ImageDisplayWidget(bg_color='white')

    # Create a test RGB image 256x256
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image_from_array(test_image, text="Test Image")
    widget.show()
    sys.exit(app.exec())