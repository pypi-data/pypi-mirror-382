import time

from PyQt6.QtCore import QObject, QThread

from lensepy import translate
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.spatial_camera import *
from lensepy.modules.basler.basler_controller import BaslerController
from lensepy.widgets import *

class SpatialCameraController(TemplateController):
    """Controller for camera acquisition."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.top_left = ImageDisplayWithCrosshair()
        self.bot_left = HistogramWidget()
        self.bot_right = XYMultiChartWidget(base_color=ORANGE_IOGS)
        self.top_right = XYMultiChartWidget()
        # Setup widgets
        self.bot_left.set_background('white')
        # Variables
        self.thread = None
        self.worker = None
        # Signals
        self.top_left.point_selected.connect(self.handle_xy_changed)
        # Init widgets
        if self.parent.variables['bits_depth'] is not None:
            self.top_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
        else:
            self.bot_left.set_bits_depth(8)
        if self.parent.variables['image'] is not None:
            self.top_left.set_image_from_array(self.parent.variables['image'])
            self.bot_left.set_image(self.parent.variables['image'])
        self.bot_left.refresh_chart()
        # Init worker
        self.image_worker = ImageLive(self)
        self.image_worker.image_ready.connect(self.display_image)  # Slot GUI
        camera = self.parent.variables["camera"]
        if camera is not None:
            print(f'Mode : {camera.get_parameter("PixelFormat")}')
        self.start_live()

    def start_live(self):
        """
        Start live acquisition from camera.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            self.thread = QThread()
            self.worker = ImageLive(self)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.image_ready.connect(self.handle_image_ready)
            self.worker.finished.connect(self.thread.quit)

            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.thread.deleteLater)

            self.thread.start()

    def display_image(self, image: np.ndarray):
        """Met à jour l'image dans le widget GUI."""
        self.top_left.set_image_from_array(image)

    def handle_image_ready(self, image):
        """
        Action performed when a new image is ready.
        """
        # Update Image
        self.parent.variables['image'] = image.copy()
        self.top_left.set_image_from_array(image)
        # Update Histo
        self.bot_left.set_image(image, checked=False)

    def handle_xy_changed(self, x, y):
        """
        Action performed when the XY coordinates changed.
        """
        x_data = self.parent.variables['image'][int(y),:]
        xx_x = np.linspace(1, len(x_data), len(x_data))
        y_data = self.parent.variables['image'][:,int(x)]
        yy_x = np.linspace(1, len(y_data), len(y_data))
        x_mean = np.round(np.mean(x_data), 1)
        x_min = np.round(np.min(x_data), 1)
        x_max = np.round(np.max(x_data), 1)
        y_mean = np.round(np.mean(y_data), 1)
        y_min = np.round(np.min(y_data), 1)
        y_max = np.round(np.max(y_data), 1)
        self.top_right.set_data(xx_x, x_data, x_label='position', y_label='intensity')
        self.top_right.refresh_chart()
        self.top_right.set_information(f'Mean = {x_mean} / Min = {x_min} / Max = {x_max}')
        self.bot_right.set_data(yy_x, y_data, x_label='position', y_label='intensity')
        self.bot_right.refresh_chart()
        self.bot_right.set_information(f'Mean = {y_mean} / Min = {y_min} / Max = {y_max}')

    def display_image(self, image: np.ndarray):
        """
        Display the image given as a numpy array.
        :param image:   numpy array containing the data.
        :return:
        """
        self.top_left.set_image_from_array(image)


class ImageLive(QObject):
    """Worker thread pour acquisition d'image."""
    image_ready = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._running = False

    def run(self):
        camera = self.controller.parent.variables.get("camera", None)
        if camera is None:
            print("No camera found, stopping thread.")
            return

        self._running = True
        camera.open()
        camera.camera_acquiring = True

        while self._running:
            image = camera.get_image()
            # Émet l'image au thread GUI
            self.image_ready.emit(image)
            time.sleep(0.01)  # petite pause pour éviter 100% CPU

        camera.camera_acquiring = False
        camera.close()
        self.finished.emit()

    def stop(self):
        self._running = False
        time.sleep(0.01)
        try:
            camera = self.controller.parent.variables.get("camera", None)
            if camera is not None and getattr(camera, "is_open", False):
                camera.close()
        except Exception as e:
            print(f"Camera close error during stop: {e}")
        finally:
            self.controller = None
