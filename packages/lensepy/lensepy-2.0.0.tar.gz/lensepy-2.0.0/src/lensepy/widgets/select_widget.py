"""
select_widget.py
================

PyQt6 widget that provides a labeled selection list (combo box) with optional units.
Emits a signal when the selection changes, allowing easy integration in GUI dashboards.

Features
--------

- Labeled combo box for selection
- Optional units label
- Emits a signal on selection change
- Easily integrated into dashboards and control panels

Usage Example
-------------

.. code-block:: python

    import sys
    from PyQt6.QtWidgets import QApplication
    from select_widget import SelectWidget

    def on_choice_changed(index_str):
        print(f"Selected index: {index_str}")

    app = QApplication(sys.argv)

    widget = SelectWidget("Mode", ["Auto", "Manual", "Off"], units="units")
    widget.choice_selected.connect(on_choice_changed)
    widget.show()

    sys.exit(app.exec())


Author : Julien VILLEMEJANE / LEnsE - IOGS
Date   : 2025-10-09
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QComboBox
from lensepy.css import *


class SelectWidget(QWidget):
    """
    Widget including a select list.
    """
    choice_selected = pyqtSignal(str)

    def __init__(self, title: str, values: list, units: str = None):
        """

        :param title:   Title of the widget.
        :param values:  Values of the selection list.
        :param units:   Units of the data.
        """
        super().__init__()
        # Graphical objects
        self.label_title = QLabel(title)
        self.label_title.setStyleSheet(styleH2)
        self.combo_box = QComboBox()
        self.combo_box.addItems(values)
        self.combo_box.currentIndexChanged.connect(self.handle_choice_selected)
        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.label_title, 2)
        layout.addWidget(self.combo_box, 2)
        if units is not None:
            self.label_units = QLabel(units)
            layout.addWidget(self.label_units, 1)
        self.setLayout(layout)

    def handle_choice_selected(self):
        """
        Action performed when the colormode choice changed.
        """
        index = self.get_selected_index()
        value = self.get_selected_value()
        self.choice_selected.emit(str(index))

    def get_selected_value(self) -> str:
        """Get the selected value."""
        return self.combo_box.currentText()

    def get_selected_index(self) -> str:
        """Get the index of the selection."""
        return self.combo_box.currentIndex()

    def set_values(self, values: list[str]):
        """Update the list of values.
        :param values: List of values.
        """
        self.combo_box.clear()
        self.combo_box.addItems(values)

    def set_title(self, title: str):
        """
        Change the title of the selection object.
        :param title:   Title of the selection object.
        """
        self.label_title.setText(title)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication


    def on_choice_changed(index_str):
        print(f"Selected index: {index_str}")

    app = QApplication(sys.argv)

    widget = SelectWidget("Mode", ["Auto", "Manual", "Off"], units="units")
    widget.choice_selected.connect(on_choice_changed)
    widget.show()

    sys.exit(app.exec())