from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class DefaultTopLeftWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel('Top Left')
        layout.addWidget(label)
        self.setLayout(layout)

class DefaultBotLeftWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel('Bot Left')
        layout.addWidget(label)
        self.setLayout(layout)