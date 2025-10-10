import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QScrollArea, QSizePolicy, QCheckBox
)
from pyqtgraph import PlotWidget, mkPen, mkBrush
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QGraphicsLineItem
from lensepy.css import *
from lensepy.widgets import ImageDisplayWidget


class ImageDisplayWithCrosshair(ImageDisplayWidget):
    """ImageDisplayWidget avec sélection d’un point et affichage d’un réticule (croix)."""

    point_selected = pyqtSignal(float, float)  # (x, y) dans l'image

    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent, bg_color, zoom)
        self.crosshair_color_h = QColor(BLUE_IOGS)
        self.crosshair_pen_h = QPen(self.crosshair_color_h, 2, Qt.PenStyle.SolidLine)
        self.crosshair_color_v = QColor(ORANGE_IOGS)
        self.crosshair_pen_v = QPen(self.crosshair_color_v, 2, Qt.PenStyle.DashLine)
        self.h_line = None
        self.v_line = None
        self.selected_point = None
        self.dragging = False  # nouveau flag pour suivre le drag

        # Active la détection de clics et mouvements sur la scène
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    # ----------------------------------------------------------------------
    # Event handling : on intercepte les clics et mouvements sur la vue
    # ----------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj is self.view.viewport():
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self._update_point(event)
            elif event.type() == event.Type.MouseMove and self.dragging:
                self._update_point(event)
            elif event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = False
        return super().eventFilter(obj, event)

    def _update_point(self, event):
        """Convertit la position du curseur en coordonnées scène et met à jour la croix."""
        pos = self.view.mapToScene(event.pos())
        x, y = pos.x(), pos.y()
        self.selected_point = QPointF(x, y)
        self._draw_crosshair(x, y)
        self.point_selected.emit(x, y)

    # ----------------------------------------------------------------------
    # Crosshair drawing
    # ----------------------------------------------------------------------
    def _draw_crosshair(self, x, y):
        """Dessine ou met à jour les lignes du réticule."""
        scene_rect = self.scene.sceneRect()

        # Supprime les anciennes lignes si elles existent
        if self.h_line:
            self.scene.removeItem(self.h_line)
        if self.v_line:
            self.scene.removeItem(self.v_line)

        # Crée les nouvelles lignes
        self.h_line = QGraphicsLineItem(scene_rect.left(), y, scene_rect.right(), y)
        self.v_line = QGraphicsLineItem(x, scene_rect.top(), x, scene_rect.bottom())

        self.v_line.setPen(self.crosshair_pen_v)
        self.scene.addItem(self.v_line)
        self.h_line.setPen(self.crosshair_pen_h)
        self.scene.addItem(self.h_line)


class SliderBloc(QWidget):
    """
    Slider block combining a numeric input and a horizontal slider.
    Emits the current value whenever it changes.
    """

    slider_changed = pyqtSignal(float)

    def __init__(self, name: str, unit: str, min_value: float, max_value: float,
                 integer: bool = False) -> None:
        super().__init__()

        self.integer = integer
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.ratio = 1 if integer else 100
        self.value = round(min_value + (max_value - min_value) / 3, 2)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- First line: label + input + unit ---
        self._init_value_line(name)

        # --- Second line: slider + min/max labels ---
        self._init_slider_line()

        self.update_block()

    # ----------------------------
    # Initialization subfunctions
    # ----------------------------

    def _styled_label(self, text: str, style: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(style)
        return label

    def _init_value_line(self, name: str):
        line = QHBoxLayout()
        self.label_name = self._styled_label(f"{name}:", styleH2)
        self.lineedit_value = QLineEdit(str(self.value))
        self.lineedit_value.editingFinished.connect(self.input_changed)
        self.label_unit = self._styled_label(self.unit, styleH3)

        for widget in (self.label_name, self.lineedit_value, self.label_unit):
            line.addWidget(widget)
        line.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setLayout(line)
        self.layout.addWidget(container)

    def _init_slider_line(self):
        line = QHBoxLayout()
        self.label_min_value = self._styled_label(f"{self.min_value} {self.unit}", styleH3)
        self.label_max_value = self._styled_label(f"{self.max_value} {self.unit}", styleH3)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(self.min_value * self.ratio), int(self.max_value * self.ratio))
        self.slider.valueChanged.connect(self.slider_position_changed)

        for widget in (self.label_min_value, self.slider, self.label_max_value):
            line.addWidget(widget)
        line.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setLayout(line)
        self.layout.addWidget(container)

    # ----------------------------
    # Event handling
    # ----------------------------

    def slider_position_changed(self):
        self.value = self.slider.value() / self.ratio
        if self.integer:
            self.value = int(self.value)
        self.lineedit_value.setText(str(self.value))
        self.slider_changed.emit(self.value)

    def input_changed(self):
        """Triggered when user edits the numeric value."""
        try:
            val = float(self.lineedit_value.text())
        except ValueError:
            val = self.value  # revert to last valid value

        self.value = self._clamp(val, self.min_value, self.max_value)
        self.update_block()
        self.slider_changed.emit(self.value)

    # ----------------------------
    # Utilities
    # ----------------------------

    def update_block(self):
        """Sync text and slider position."""
        val = int(self.value) if self.integer else self.value
        self.lineedit_value.setText(str(val))
        self.slider.blockSignals(True)
        self.slider.setValue(int(val * self.ratio))
        self.slider.blockSignals(False)

    def get_value(self) -> float:
        return self.value

    def set_value(self, value: float):
        self.value = int(value) if self.integer else float(value)
        self.update_block()

    def set_min_max_slider_values(self, min_value: float, max_value: float, value: float | None = None):
        """Update slider bounds and optionally reset its current value."""
        self.min_value, self.max_value = min_value, max_value
        self.slider.setRange(int(min_value * self.ratio), int(max_value * self.ratio))
        if value is not None:
            self.set_value(value)
        self.label_min_value.setText(f"{min_value} {self.unit}")
        self.label_max_value.setText(f"{max_value} {self.unit}")

    def set_enabled(self, enabled: bool):
        """Enable or disable the whole block."""
        self.slider.setEnabled(enabled)
        self.lineedit_value.setEnabled(enabled)

    @staticmethod
    def _clamp(val, vmin, vmax):
        return max(vmin, min(vmax, val))

