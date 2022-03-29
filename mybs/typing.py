from typing import Union, Optional, List
from .configer import Config
from PySide6.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QWidget, QMenu, QFileDialog
from PySide6.QtCore import QDir, QAbstractItemModel
from PySide6.QtCore import Qt, QModelIndex, QEvent, QObject
from PySide6.QtGui import QCursor
from .filemaster import filemaster