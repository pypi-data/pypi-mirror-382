from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _app.main_manager import MainManager


class TemplateController:
    """

    """

    controller_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        """

        """
        self.parent: MainManager = parent
        self.top_left = QWidget()
        self.top_right = QWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()

    def init_view(self):
        self.parent.main_window.top_left_container.deleteLater()
        self.parent.main_window.top_right_container.deleteLater()
        self.parent.main_window.bot_left_container.deleteLater()
        self.parent.main_window.bot_right_container.deleteLater()
        # Update new containers
        self.parent.main_window.top_left_container = self.top_left
        self.parent.main_window.bot_left_container = self.bot_left
        self.parent.main_window.top_right_container = self.top_right
        self.parent.main_window.bot_right_container = self.bot_right
        self.update_view()

    def update_view(self):
        # Display mode value in XML
        mode = self.parent.xml_module.get_parameter_xml('display')
        if mode == 'MODE2':
            self.parent.main_window.set_mode2()
        else:
            self.parent.main_window.set_mode1()
        # Update display mode
        self.parent.main_window.update_containers()

    def handle_controller(self, event):
        """
        Action performed when the controller changed.
        :param event:
        """
        self.controller_changed.emit(event)

    def get_variables(self):
        """
        Get variables dictionary from the main manager.
        :return:
        """
        return self.parent.variables
