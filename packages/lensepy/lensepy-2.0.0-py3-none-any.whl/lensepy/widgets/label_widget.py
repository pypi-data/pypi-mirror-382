"""
label_widget.py
===============

PyQt6 widget for displaying a labeled value with units.
Useful for dashboards or control panels where a parameter
needs to be displayed with a title and unit label.

Features
--------

- Horizontal layout: title | value | units
- Centered value label
- Lightweight and reusable for various parameters

Usage Example
-------------

.. code-block:: python

    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = LabelWidget("Temperature", "25.0", "°C")
    widget.set_value("26.5")
    widget.show()
    sys.exit(app.exec())


Author : Julien VILLEMEJANE / LEnsE - IOGS
Date   : 2025-10-09
"""


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from lensepy.css import *


class LabelWidget(QWidget):
    def __init__(self, title: str, value: str, units: str = None):
        super().__init__()
        widget_w = QWidget()
        layout_w = QHBoxLayout()
        widget_w.setLayout(layout_w)

        self.title = QLabel(title)
        self.value = QLabel(value)
        self.title.setStyleSheet(styleH2)
        self.value.setStyleSheet(styleH2)
        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_w.addWidget(self.title, 2)
        layout_w.addWidget(self.value, 2)
        if units is not None:
            self.units = QLabel(units)
            self.units.setStyleSheet(styleH3)
            self.units.setStyleSheet(styleH3)
            layout_w.addWidget(self.units, 1)
        else:
            self.units = QLabel('')
        self.setLayout(layout_w)

    def set_value(self, value):
        """Update widget value."""
        self.value.setText(value)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    # Create Qt application
    app = QApplication(sys.argv)

    # Create LabelWidget instance
    widget = LabelWidget("Temperature", "25.0", "°C")
    widget.setWindowTitle("Label Widget Test")
    widget.show()

    # Update value after creation
    widget.set_value("26.5")

    # Run main loop
    sys.exit(app.exec())