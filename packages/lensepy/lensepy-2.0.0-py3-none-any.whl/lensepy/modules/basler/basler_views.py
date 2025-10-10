from lensepy import translate
from lensepy.utils.pyqt6 import make_hline
from lensepy.widgets import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy.modules.basler.basler_controller import BaslerController, BaslerCamera

class CameraInfosWidget(QWidget):
    """
    Widget to display image infos.
    """
    color_mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent: BaslerController = parent
        layout = QVBoxLayout()

        self.camera = self.parent.get_variables()['camera']

        label = QLabel(translate('basler_infos_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        self.label_name = LabelWidget(translate('basler_infos_name'), '')
        layout.addWidget(self.label_name)
        self.label_serial = LabelWidget(translate('basler_infos_serial'), '')
        layout.addWidget(self.label_serial)
        layout.addWidget(make_hline())

        self.label_size = LabelWidget(translate('basler_infos_size'), '', 'pixels')
        layout.addWidget(self.label_size)
        self.color_choice = self.parent.colormode
        self.label_color_mode = SelectWidget(translate('basler_infos_color_mode'), self.color_choice)
        self.label_color_mode.choice_selected.connect(self.handle_color_mode_changed)
        layout.addWidget(self.label_color_mode)
        layout.addWidget(make_hline())

        layout.addStretch()
        self.setLayout(layout)
        #self.update_infos()

    def handle_color_mode_changed(self, event):
        """
        Action performed when color mode is changed.
        """
        self.color_mode_changed.emit(event)


    def update_infos(self):
        """
        Update information from camera.
        """
        self.camera: BaslerCamera = self.parent.get_variables()['camera']
        if self.parent.camera_connected:
            self.camera.open()
            self.label_name.set_value(self.camera.get_parameter('DeviceModelName'))
            self.label_serial.set_value(self.camera.get_parameter('DeviceSerialNumber'))
            w = str(self.camera.get_parameter('SensorWidth'))
            h = str(self.camera.get_parameter('SensorHeight'))
            self.label_size.set_value(f'WxH = {w} x {h}')
            self.camera.close()
        else:
            print(f'Basler - NO CAMERA')
            self.label_name.set_value(translate('no_camera'))
            self.label_serial.set_value(translate('no_camera'))
            self.label_size.set_value('')

