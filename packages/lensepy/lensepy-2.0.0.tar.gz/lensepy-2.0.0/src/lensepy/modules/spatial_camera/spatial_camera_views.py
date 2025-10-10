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
    """ImageDisplayWidget avec sélection d’un point et affichage d’un réticule (crosshair)."""

    point_selected = pyqtSignal(float, float)

    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent, bg_color, zoom)

        # Couleurs et styles du crosshair
        self.crosshair_pen_h = QPen(QColor(BLUE_IOGS), 2, Qt.PenStyle.SolidLine)
        self.crosshair_pen_v = QPen(QColor(ORANGE_IOGS), 2, Qt.PenStyle.DashLine)

        # Lignes du crosshair
        self.h_line = None
        self.v_line = None

        self.selected_point = None
        self.dragging = False

        # Active la détection de clics et mouvements sur la scène
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

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
        pos = self.view.mapToScene(event.pos())
        x, y = pos.x(), pos.y()
        self.selected_point = QPointF(x, y)
        self._draw_crosshair(x, y)
        self.point_selected.emit(x, y)

    def _draw_crosshair(self, x, y):
        """Dessine ou déplace les lignes du crosshair."""
        scene_rect = self.scene.sceneRect()

        if self.h_line is None:
            self.h_line = QGraphicsLineItem()
            self.h_line.setPen(self.crosshair_pen_h)
            self.scene.addItem(self.h_line)

        if self.v_line is None:
            self.v_line = QGraphicsLineItem()
            self.v_line.setPen(self.crosshair_pen_v)
            self.scene.addItem(self.v_line)

        # Met à jour la position des lignes
        self.h_line.setLine(scene_rect.left(), y, scene_rect.right(), y)
        self.v_line.setLine(x, scene_rect.top(), x, scene_rect.bottom())
