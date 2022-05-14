# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'myuiaqKmYf.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from mybs.typing import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actionaddtab = QAction(MainWindow)
        self.actionaddtab.setObjectName(u"actionaddtab")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.ftreebutton = QToolButton(self.centralwidget)
        self.ftreebutton.setObjectName(u"ftreebutton")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftreebutton.sizePolicy().hasHeightForWidth())
        self.ftreebutton.setSizePolicy(sizePolicy)
        self.ftreebutton.setIconSize(QSize(8, 8))
        self.ftreebutton.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.ftreebutton, 0, Qt.AlignLeft)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.comboBox = QComboBox(self.centralwidget)
        self.comboBox.setObjectName(u"comboBox")

        self.verticalLayout_5.addWidget(self.comboBox)

        self.ftree = QTreeView(self.centralwidget)
        self.ftree.setObjectName(u"ftree")
        self.ftree.setFrameShape(QFrame.Box)
        self.ftree.setFrameShadow(QFrame.Plain)
        self.ftree.setLineWidth(0)
        self.ftree.setEditTriggers(QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)
        self.ftree.setDragEnabled(True)
        self.ftree.setDragDropMode(QAbstractItemView.DragDrop)
        self.ftree.setDefaultDropAction(Qt.CopyAction)

        self.verticalLayout_5.addWidget(self.ftree)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)


        self.horizontalLayout.addLayout(self.horizontalLayout_2)

        self.tab = QTabWidget(self.centralwidget)
        self.tab.setObjectName(u"tab")
        self.tab.setAcceptDrops(True)
        self.tab.setTabShape(QTabWidget.Rounded)
        self.tab.setElideMode(Qt.ElideLeft)
        self.tab.setTabsClosable(True)
        self.tab.setMovable(True)
        self.tab.setTabBarAutoHide(False)

        self.horizontalLayout.addWidget(self.tab)

        self.horizontalLayout.setStretch(0, 4)
        self.horizontalLayout.setStretch(1, 7)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 8)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menudebug = QMenu(self.menubar)
        self.menudebug.setObjectName(u"menudebug")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menudebug.menuAction())

        self.retranslateUi(MainWindow)

        self.tab.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionaddtab.setText(QCoreApplication.translate("MainWindow", u"addtab", None))
        self.ftreebutton.setText(QCoreApplication.translate("MainWindow", u"<", None))
        self.menudebug.setTitle(QCoreApplication.translate("MainWindow", u"debug", None))
    # retranslateUi

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