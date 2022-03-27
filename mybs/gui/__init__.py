from . import ui_myui
from PySide6.QtWidgets import QApplication, QMainWindow, QFileSystemModel
from PySide6.QtCore import QDir
from mybs.typing import Config

class MYGUI(QMainWindow):

    def __init__(self, config: Config):
        super().__init__()
        self.ui = ui_myui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.config = config


    @staticmethod
    def run(config: Config):
        app = QApplication([])
        gui = MYGUI(config)
        gui.show()
        app.exec_()

