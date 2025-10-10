import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from pyqtgraph import mkPen, PlotWidget

from lensepy.css import *


class XYMultiChartWidget(QWidget):
    """
    Widget to display XY curves:
    – either all curves on a single plot (multi_chart=False)
    – or one curve per vertically stacked plot (multi_chart=True)
    """

    def __init__(self, parent=None, multi_chart=True,
                 base_color=None, max_points=2000):
        super().__init__(parent)
        self.multi_chart = multi_chart
        self.__show_grid = True
        self.background_color = "white"
        self.base_color = base_color
        self.max_points = max_points

        # Data
        self.plot_x_data = []
        self.plot_y_data = []
        self.y_names = []
        self.x_label = ""
        self.y_label = ""

        # Color management
        if self.base_color is not None:
            base_colors = [base_color, BLUE_IOGS, ORANGE_IOGS, GREEN_IOGS, RED_IOGS]
        else:
            base_colors = [BLUE_IOGS, ORANGE_IOGS, GREEN_IOGS, RED_IOGS]
        self.pen = [
            mkPen(color=c, style=Qt.PenStyle.SolidLine, width=2.5) for c in base_colors
        ]

        # Main layout
        self.layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel('', alignment=Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "background-color: darkgray; font-weight:bold; color:white; font-size:20px;"
        )
        self.layout.addWidget(self.title_label)

        # Chart container
        self.charts_container = QWidget()
        self.charts_layout = QVBoxLayout(self.charts_container)
        self.charts_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_layout.setSpacing(10)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.charts_container)
        self.layout.addWidget(self.scroll_area)

        self.info_label = QLabel(text='', alignment=Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: gray; font-size: 14px;")
        self.layout.addWidget(self.info_label)

        # Internal variables
        self.plot_widgets = []
        self.curves = []

        self.set_background(self.background_color)

    # -------------------- API publique --------------------

    def set_title(self, title: str):
        """Set the title of the chart."""
        self.title_label.setText(title)

    def set_information(self, info: str):
        """Set the information text displayed below the charts."""
        self.info_label.setText(info)

    def set_background(self, css_color: str):
        """Set the background color."""
        self.background_color = css_color
        self.setStyleSheet(f"background:{css_color};")
        for pw in self.plot_widgets:
            pw.setBackground(css_color)

    def set_data(self, x_axis, y_axis, y_names=None, x_label='', y_label=''):
        """Set data to display."""
        if not isinstance(y_axis[0], (list, np.ndarray)):
            y_axis = [y_axis]
        if not isinstance(x_axis[0], (list, np.ndarray)):
            x_axis = [x_axis] * len(y_axis)

        self.plot_x_data = [np.array(x) for x in x_axis]
        self.plot_y_data = [np.array(y) for y in y_axis]
        self.y_names = y_names if y_names else [f"Curve {i+1}" for i in range(len(y_axis))]
        self.x_label = x_label
        self.y_label = y_label

    def show_grid(self, value=True):
        """Display the grid on the chart."""
        self.__show_grid = value
        for pw in self.plot_widgets:
            pw.showGrid(x=value, y=value)

    def refresh_chart(self, last=0):
        """Update chart."""
        # Décide du mode
        if not self.plot_widgets:
            # Create plots once
            if self.multi_chart:
                self._init_multiple_charts()
            else:
                self._init_single_chart()

        # Update data to display
        if self.multi_chart:
            for i, (x, y) in enumerate(zip(self.plot_x_data, self.plot_y_data)):
                if i >= len(self.plot_widgets):
                    continue
                x_plot, y_plot = self._slice_and_decimate(x, y, last)
                pw = self.plot_widgets[i]
                curve = self.curves[i]
                curve.setData(x_plot, y_plot)
        else:
            pw = self.plot_widgets[0]
            for i, (x, y) in enumerate(zip(self.plot_x_data, self.plot_y_data)):
                x_plot, y_plot = self._slice_and_decimate(x, y, last)
                self.curves[i].setData(x_plot, y_plot)

    # -------------------- Plots Initialization --------------------

    def _configure_plot_widget(self, pw: PlotWidget):
        pw.setBackground(self.background_color)
        pw.showGrid(x=self.__show_grid, y=self.__show_grid)
        pw.setMouseEnabled(x=False, y=False)
        pw.setMenuEnabled(False)

    def _init_single_chart(self):
        plot_widget = PlotWidget()
        self._configure_plot_widget(plot_widget)
        self.plot_widgets.append(plot_widget)
        self.charts_layout.addWidget(plot_widget)

        legend = plot_widget.addLegend()
        self.curves = []

        for i, y in enumerate(self.plot_y_data):
            curve = plot_widget.plot([], [], pen=self.pen[i % len(self.pen)],
                                     name=self.y_names[i])
            self.curves.append(curve)

        styles = {"color": "black", "font-size": "14px"}
        if self.x_label:
            plot_widget.setLabel("bottom", self.x_label, **styles)
        if self.y_label:
            plot_widget.setLabel("left", self.y_label, **styles)

    def _init_multiple_charts(self):
        self.plot_widgets = []
        self.curves = []

        for i, y in enumerate(self.plot_y_data):
            plot_widget = PlotWidget()
            self._configure_plot_widget(plot_widget)
            self.plot_widgets.append(plot_widget)
            self.charts_layout.addWidget(plot_widget)

            curve = plot_widget.plot([], [], pen=self.pen[i % len(self.pen)],
                                     name=self.y_names[i])
            self.curves.append(curve)

            plot_widget.setTitle(self.y_names[i], color="black", size="12pt")
            styles = {"color": "black", "font-size": "14px"}
            if self.x_label:
                plot_widget.setLabel("bottom", self.x_label, **styles)
            if self.y_label:
                plot_widget.setLabel("left", self.y_label, **styles)

    # -------------------- Décimation et slicing --------------------

    def _slice_and_decimate(self, x, y, last):
        if last > 0 and len(x) > last:
            x, y = x[-last:], y[-last:]
        # Decimate if too many points
        n = len(x)
        if n > self.max_points:
            step = n // self.max_points
            x = x[::step]
            y = y[::step]
        return x, y