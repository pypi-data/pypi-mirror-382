from lensepy import translate
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.spatial_images import *
from lensepy.widgets import *


class SpatialImagesController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.top_left = ImageDisplayWithCrosshair()
        self.bot_left = HistogramWidget()
        self.bot_right = XYMultiChartWidget(base_color=ORANGE_IOGS)
        self.top_right = XYMultiChartWidget()
        # Setup widgets
        self.bot_left.set_background('white')
        self.top_right.set_background('white')
        self.top_right.set_title(translate('slice_display_h'))
        self.bot_right.set_background('white')
        self.bot_right.set_title(translate('slice_display_v'))
        if self.parent.variables['bits_depth'] is not None:
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
        else:
            self.bot_left.set_bits_depth(8)
        if self.parent.variables['image'] is not None:
            self.top_left.set_image_from_array(self.parent.variables['image'])
            self.bot_left.set_image(self.parent.variables['image'])
        self.bot_left.refresh_chart()
        # Signals
        self.top_left.point_selected.connect(self.handle_xy_changed)

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


