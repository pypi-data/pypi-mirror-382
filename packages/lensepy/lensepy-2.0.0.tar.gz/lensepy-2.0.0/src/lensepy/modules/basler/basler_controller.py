import time
from PyQt6.QtCore import QObject, QThread
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.basler.basler_views import *
from lensepy.modules.basler.basler_models import *
from lensepy.widgets import *


class BaslerController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """
        :param parent:
        """
        super().__init__(parent)
        self.top_left = ImageDisplayWidget()
        self.bot_left = HistogramWidget()
        self.bot_right = QWidget()
        self.top_right = QWidget()
        # Setup widgets
        self.bot_left.set_background('white')
        # Variables
        self.camera_connected = False       # Camera is connected
        self.thread = None
        self.worker = None
        self.colormode = []
        self.colormode_bits_depth = []

        # Signals

        # Init Camera
        self.init_camera()
        self.top_right = CameraInfosWidget(self)
        self.top_right.update_infos()
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
        # Signals
        self.top_right.color_mode_changed.connect(self.handle_color_mode_changed)
        # Start thread
        self.start_live()

    def init_camera(self):
        """

        :return:
        """
        # Get color mode list
        colormode_get = self.parent.xml_app.get_sub_parameter('camera','colormode')
        colormode_get = colormode_get.split(',')
        for colormode in colormode_get:
            colormode_v = colormode.split(':')
            self.colormode.append(colormode_v[0])
            self.colormode_bits_depth.append(int(colormode_v[1]))
        # Init Camera
        self.parent.variables["camera"] = BaslerCamera()
        self.camera_connected = self.parent.variables["camera"].find_first_camera()
        if self.camera_connected:
            camera = self.parent.variables["camera"]
            first_mode_color = self.colormode[0]
            camera.open()
            camera.set_parameter("PixelFormat", first_mode_color)
            camera.initial_params["PixelFormat"] = first_mode_color
            camera.close()
            first_bits_depth = self.colormode_bits_depth[0]
            self.parent.variables["bits_depth"] = first_bits_depth

    def start_live(self):
        """
        Start live acquisition from camera.
        """
        if self.camera_connected:
            self.thread = QThread()
            self.worker = ImageLive(self)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.image_ready.connect(self.handle_image_ready)
            self.worker.finished.connect(self.thread.quit)

            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.thread.deleteLater)

            self.thread.start()

    def stop_live(self):
        """
        Stop live mode, i.e. continuous image acquisition.
        """
        if self.worker is not None:
            # Arrêter le worker
            self.worker._running = False

            # Attendre la fin du thread
            if self.thread is not None:
                self.thread.quit()
                self.thread.wait()  # bloque jusqu'à la fin

            # Supprimer les références
            self.worker = None
            self.thread = None

    def handle_image_ready(self):
        """
        Action performed when a new image is ready.
        :return:
        """
        # Update Image
        image = self.parent.variables['image'].copy()
        self.top_left.set_image_from_array(image)
        # Update Histo
        self.bot_left.set_image(image, checked=False)

    def display_image(self, image: np.ndarray):
        """
        Display the image given as a numpy array.
        :param image:   numpy array containing the data.
        :return:
        """
        self.top_left.set_image_from_array(image)

    def handle_color_mode_changed(self, event):
        """
        Action performed when the color mode changed.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Read available formats
            available_formats = []
            try:
                if camera.camera_device is not None:
                    camera.open()
                    available_formats = list(camera.camera_device.PixelFormat.Symbolics)
                    camera.close()
            except Exception as e:
                print(f"Unable to read PixelFormat.Symbolics: {e}")
            # Select new format
            idx = int(event)
            new_format = self.colormode[idx] if idx < len(self.colormode) else None

            if new_format is None:
                return
            if new_format in available_formats:
                camera.open()
                camera.set_parameter("PixelFormat", new_format)
                camera.initial_params["PixelFormat"] = new_format
                camera.close()
            else:
                print(f"Format {new_format} not in available formats: {available_formats}")
            # Change bits depth
            self.parent.variables['bits_depth'] = self.colormode_bits_depth[idx]
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            self.top_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            if 'Bayer' in new_format:
                self.bot_left.reinit_checkbox('RGB')
            elif 'Mono' in new_format:
                self.bot_left.reinit_checkbox('Gray')
            # Restart live
            camera.open()
            self.start_live()


class ImageLive(QObject):
    """
    Worker for image acquisition.
    Based on threads.
    """
    image_ready = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._running = False

    def run(self):
        """
        Main process of the thread to acquire images.
        """
        camera = self.controller.parent.variables.get("camera", None)
        if camera is None:
            print("No camera found, stopping thread.")
            return

        self._running = True
        camera.open()
        camera.camera_acquiring = True

        while self._running:
            if self.controller is None or self.controller.parent is None:
                break

            if camera is not None:
                image = camera.get_image()
            if self.controller is not None:
                self.controller.parent.variables["image"] = camera.get_image()
                self.image_ready.emit()
            # time.sleep(0.001)

        if camera is not None and getattr(camera, "is_open", False):
            camera.camera_acquiring = False
            camera.close()
            self.finished.emit()

    def stop(self):
        """Stop the worker."""
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