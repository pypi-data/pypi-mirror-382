"""
histogram_widget.py
===================

PyQt6 widget for displaying the histogram of an image (grayscale or RGB)
as bar charts. Allows visualization of the R, G, B channels and luminance
with filtering options and customizable appearance.

Classes
-------
HistogramWidget(QWidget)
    Main widget for displaying an image histogram.

Features
--------
- Graphical display using pyqtgraph
- Supports grayscale and RGB images
- Automatic bit-depth handling (8, 16…)
- Channel selection via checkboxes
- Customizable background color
- Optimized for large images

Usage Example
-------------

.. code-block:: python

    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    widget = HistogramWidget()
    widget.setWindowTitle("Histogram Widget Test")
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image(test_image)
    widget.set_bits_depth(8)
    widget.set_background('w')

    widget.show()
    sys.exit(app.exec())


Author : Julien VILLEMEJANE / LEnsE - IOGS
Date   : 2025-10-09
"""


import numpy as np
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QCheckBox, QApplication
import pyqtgraph as pg
from lensepy.utils.images import resize_image_ratio


class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = None
        self.bits_depth = 8

        # Layout principal
        layout = QVBoxLayout(self)

        # Zone graphique
        self.plot = pg.PlotWidget()
        self.plot.setLabel('bottom', 'Intensity')
        self.plot.setLabel('left', 'Frequency')
        layout.addWidget(self.plot)

        # BarGraphItems for each channel
        self.bar_r = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(255, 0, 0, 150))
        self.bar_g = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(0, 255, 0, 150))
        self.bar_b = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(0, 0, 255, 150))
        self.bar_l = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(200, 200, 200, 150))

        self.plot.addItem(self.bar_r)
        self.plot.addItem(self.bar_g)
        self.plot.addItem(self.bar_b)
        self.plot.addItem(self.bar_l)

        # Checkboxes
        box_layout = QHBoxLayout()
        self.chk_r = QCheckBox("R")
        self.chk_g = QCheckBox("G")
        self.chk_b = QCheckBox("B")
        self.chk_l = QCheckBox("Lum.")
        for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
            chk.setChecked(True)
            chk.stateChanged.connect(self.refresh_chart)
            box_layout.addWidget(chk)
        layout.addLayout(box_layout)

    def reinit_checkbox(self, mode: str):
        """
        Update checkbox visibility.
        :param mode:    'RGB' or 'Gray'
        """
        # Detect if RGB or Grayscale
        if mode == 'Gray':
            for chk in [self.chk_r, self.chk_g, self.chk_b]:
                chk.setEnabled(False)
                chk.setChecked(False)
            self.chk_l.setEnabled(False)
            self.chk_l.setChecked(True)
        elif mode == 'RGB':
            for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
                chk.setChecked(True)
                chk.setEnabled(True)


    def set_image(self, img: np.ndarray, checked: bool = True):
        """Définit l'image (numpy array, 2D pour gris ou 3D pour RGB)."""
        self.image = img.copy()
        # Detect if RGB or Grayscale
        if img.ndim == 2:
            # Grayscale image
            # Update checkboxes
            if checked:
                for chk in [self.chk_r, self.chk_g, self.chk_b]:
                    chk.setEnabled(False)
                    chk.setChecked(False)
                self.chk_l.setEnabled(False)
                self.chk_l.setChecked(True)
        else:
            # RGB image
            if checked:
                for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
                    chk.setChecked(True)
                    chk.setEnabled(True)
        self.refresh_chart()

    def set_bits_depth(self, depth: int):
        """Définit la profondeur en bits (8, 16...)."""
        self.bits_depth = depth
        self.refresh_chart()

    def set_background(self, color):
        """
        Change la couleur de fond du graphique.
        color : ex. 'k' (noir), 'w' (blanc), '#202020', (r,g,b), (r,g,b,a)
        """
        self.plot.setBackground(color)

    def refresh_chart(self):
        """Recalcule et affiche les histogrammes sous forme de barres."""
        # Empty graphe if no image
        if self.image is None:
            for bar in [self.bar_r, self.bar_g, self.bar_b, self.bar_l]:
                self.plot.removeItem(bar)
            return

        max_val = 2 ** self.bits_depth - 1
        hist_range = (0, max_val)

        # Remove all the data
        for bar in [self.bar_r, self.bar_g, self.bar_b, self.bar_l]:
            self.plot.removeItem(bar)

        image = self.image
        # Fast mode
        if self.image.shape[0] * self.image.shape[1] > 1000000:
            image = resize_image_ratio(image, self.image.shape[0]//4,  self.image.shape[1]//4)


        if image.ndim == 2:
            # Grayscale image
            if self.chk_l.isChecked():
                hist, bins = np.histogram(image, bins=max_val+1, range=hist_range)
                self.bar_l.setOpts(x=bins[:-1], height=hist, width=1)
                self.plot.addItem(self.bar_l)

        elif image.ndim == 3 and image.shape[2] >= 3:
            # RGB image
            if self.chk_r.isChecked():
                hist_r, bins = np.histogram(image[:, :, 0], bins=max_val+1, range=hist_range)
                self.bar_r.setOpts(x=bins[:-1], height=hist_r, width=1)
                self.plot.addItem(self.bar_r)

            if self.chk_g.isChecked():
                hist_g, bins = np.histogram(image[:, :, 1], bins=256, range=hist_range)
                self.bar_g.setOpts(x=bins[:-1], height=hist_g, width=1)
                self.plot.addItem(self.bar_g)

            if self.chk_b.isChecked():
                hist_b, bins = np.histogram(image[:, :, 2], bins=256, range=hist_range)
                self.bar_b.setOpts(x=bins[:-1], height=hist_b, width=1)
                self.plot.addItem(self.bar_b)

            if self.chk_l.isChecked():
                lum = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
                hist_l, bins = np.histogram(lum, bins=256, range=hist_range)
                self.bar_l.setOpts(x=bins[:-1], height=hist_l, width=1)
                self.plot.addItem(self.bar_l)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = HistogramWidget()
    widget.setWindowTitle("Histogram Widget Test")

    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image(test_image)
    widget.set_bits_depth(8)
    widget.set_background('w')

    widget.show()
    sys.exit(app.exec())