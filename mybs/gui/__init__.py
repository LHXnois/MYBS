from . import ui_myui

from mybs.typing import Config, QApplication, QMainWindow, QWidget, filemaster, Qt, QMenu
from mybs.typing import QCursor, QEvent, QObject, QModelIndex, QFileDialog, QMessageBox, QStyledItemDelegate
from mybs.typing import QLineEdit, QValidator, QLabel


class MYGUI(QMainWindow):

    def __init__(self, config: Config):
        super().__init__()
        self.ui = ui_myui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.conf = config

    # ======================== Filetree ========================== #

        # fileTree的折叠，同时改变按钮上的符号
        self.ui.ftreebutton.clicked.connect(
            lambda: self.ui.ftreebutton.setText('<' if self.chengevisible(self.ui.ftree, self.ui.comboBox) else '>'))

        # 装载文件树
        self.fm = filemaster()
        self.fm.setup(self.conf)
        self.ui.ftree.setModel(self.fm)

        # 事件过滤器，实现点空白处取消选中
        self.ui.ftree.viewport().installEventFilter(self)
        #
        self.ui.ftree.clicked.connect(self.fileinfo)
        self.ui.ftree.doubleClicked.connect(self.openfile)
        # 菜单
        self.ui.ftree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.ftree.customContextMenuRequested.connect(self.showftreeMenu)
        self.ftreeMenu = QMenu(self.ui.ftree)
        self.ftreeMenu.addAction(u'添加文件').triggered.connect(self.addfiles)
        self.ftreeMenu.addAction(u'移除').triggered.connect(self.delfiles)
        self.ftreeMenu.addAction(u'添加分类').triggered.connect(self.adddir)
        self.ftreeMenu_nosec = QMenu(self.ui.ftree)
        self.ftreeMenu_nosec.addAction(
            u'添加文件!!').triggered.connect(self.addfiles)
        self.ftreeMenu_nosec.addAction(u'添加分类').triggered.connect(self.adddir)

        # 真实文件发生改变时
        self.fm.fw.fileChanged.connect(self.chenge)
        # 编辑框
        self.ui.ftree.setItemDelegate(Delegate())

        self.ui.ftree.setAcceptDrops(True)

    # ======================== statbar ========================== #

    # ======================== datatab ========================== #

    # ======================== Slot ========================== #
    def openfile(self, index: QModelIndex):
        ind = index.internalPointer()
        if ind.isfile:
            print(ind.file)
    def fileinfo(self, index: QModelIndex):
        ind = index.internalPointer()
        if i := ind.fileinfo():
            self.ui.statusbar.showMessage(i)

    def chenge(self, file):
        if file not in self.fm.fw.files():
            ind = self.fm.findfile(file)
            if self.ui.ftree.currentIndex().internalPointer() == ind:
                self.ui.ftree.setCurrentIndex(
                    self.ui.ftree.currentIndex().parent())
            self.fm.remove(ind)
            self.fm.save()

    def adddir(self):
        ind = self.ui.ftree.currentIndex()
        ind = ind.internalPointer() if ind.isValid() else self.fm.rootnode
        if ind.isfile:
            ind = ind.parent
        index = self.fm._index(self.fm.append('new folder', ind))
        self.ui.ftree.setCurrentIndex(index)
        self.ui.ftree.edit(index)
        self.fm.save()

    def delfiles(self):
        ind = self.ui.ftree.currentIndex()

        if ind.isValid():
            node = ind.internalPointer()
            if QMessageBox.question(self.ui.ftree, '删除文件！', f'确定要移除{node.data(0)}吗', QMessageBox.Yes, QMessageBox.No):
                self.ui.ftree.setCurrentIndex(ind.parent())
                self.fm.remove(node)
                self.fm.save()

    def addfiles(self):
        filepaths = QFileDialog.getOpenFileNames(
            self,
            '来点文件！',
            filter='json file(*.json *.JSON);;csv file(*.csv);;excel(*.excel)')
        ind = self.ui.ftree.currentIndex()
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

    def chengevisible(self, ui: QWidget, *uis) -> bool:
        '''切换可见'''
        isv = not ui.isVisible()
        self.ui.horizontalLayout.setStretch(0, 4 if isv else 0)
        ui.setVisible(isv)
        for i in uis:
            i.setVisible(isv)
        return isv

    @staticmethod
    def run(config: Config):
        app = QApplication([])
        gui = MYGUI(config)
        gui.show()
        app.exec_()


class Delegate(QStyledItemDelegate):

    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        # editor.setValidator(QValidator(parent))
        return editor

    def setEditorData(self, editor, index):
        data = index.data()
        editor.setText(data)

    def setModelData(self, editor, model, index):
        data = editor.text()
        txt = data
        model.setData(index, txt)

    def updateEditorGeometry(self, editor, option, index):
        r = option.rect
        editor.setGeometry(r)
