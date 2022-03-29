from . import ui_myui

from mybs.typing import Config, QApplication, QMainWindow, QWidget, filemaster, Qt, QMenu
from mybs.typing import QCursor, QEvent, QObject, QModelIndex, QFileDialog
class MYGUI(QMainWindow):

    def __init__(self, config: Config):
        super().__init__()
        self.ui = ui_myui.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.conf = config

    # ======================== Filetree ========================== #

        # fileTree的折叠，同时改变按钮上的符号
        self.ui.ftreebutton.clicked.connect(
            lambda : self.ui.ftreebutton.setText('<' if self.chengevisible(self.ui.ftree) else '>'))

        # 装载文件树
        self.fm = filemaster()
        self.fm.setup(self.conf)
        self.ui.ftree.setModel(self.fm)

        # 
        self.ui.ftree.viewport().installEventFilter(self)
        # 菜单
        self.ui.ftree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.ftree.customContextMenuRequested.connect(self.showftreeMenu)
        self.ftreeMenu = QMenu(self.ui.ftree)
        self.ftreeMenu.addAction(u'添加文件').triggered.connect(self.addfiles)
        self.ftreeMenu_nosec = QMenu(self.ui.ftree)
        self.ftreeMenu_nosec.addAction(u'添加文件!!').triggered.connect(self.addfiles)




    # ======================== Slot ========================== #
    def adddir(self):
        pass
    def addfiles(self):
        filepaths = QFileDialog.getOpenFileNames(
            self,
            '来点文件！',
            filter='json file(*.json *.JSON);;csv file(*.csv);;excel(*.excel)')
        ind=self.ui.ftree.currentIndex()
        ind = ind.internalPointer() if ind.isValid() else self.fm.rootnode
        if ind.isfile:
            ind = ind.parent
        for i in set(filepaths[0]).difference(j.data(2) for j in ind.chi if j.isfile):
            self.fm.append(i, ind, True)
        self.fm.save()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.ui.ftree.viewport():
            if event.type() == QEvent.MouseButtonPress:
                if not self.ui.ftree.indexAt(event.pos()).isValid():
                    self.ui.ftree.setCurrentIndex(QModelIndex())
        return super().eventFilter(watched, event)

    def showftreeMenu(self, pos):
        if self.ui.ftree.currentIndex().isValid():
            self.ftreeMenu.exec_(QCursor.pos())
        else:
            self.ftreeMenu_nosec.exec_(QCursor.pos())

    def chengevisible(self, ui: QWidget) -> bool:
        '''切换可见'''
        isv = not ui.isVisible()
        ui.setVisible(isv)
        return isv


    @staticmethod
    def run(config: Config):
        app = QApplication([])
        gui = MYGUI(config)
        gui.show()
        app.exec_()

