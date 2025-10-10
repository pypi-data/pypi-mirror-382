from PyQt6.QtWidgets import QWidget
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.default.default_views import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _app.main_manager import MainManager

class DefaultController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.top_left = DefaultTopLeftWidget()
        self.bot_left = DefaultBotLeftWidget()


        