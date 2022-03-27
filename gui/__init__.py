from . import ui_myui
from PySide6.QtWidgets import QApplication, QMainWindow, QFileSystemModel
from PySide6.QtCore import QDir


class MYGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = ui_myui.Ui_MainWindow()
        self.ui.setupUi(self)
        
        
    @staticmethod
    def run():
        app = QApplication([])
        gui = MYGUI()
        gui.show()
        app.exec_()

