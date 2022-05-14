
from mybs.datamaster import datamaster as dm, SupportedDtypes
from mybs.util import DefaultValueValidator
from mybs.typing import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, Slot, QKeyEvent,
                         QSpacerItem, QContextMenuEvent, QDialog, QDialogButtonBox,
                         QSizePolicy, QAbstractItemView, QLabel, QGridLayout, QValidator,
                         Qt, QTableView, QMetaObject, Signal, QLineEdit, QComboBox,QCheckBox,
                         QMenu, QHeaderView, QListView, QStandardItem, QStandardItemModel,
                         QMessageBox,QInputDialog, QSpinBox,QDoubleSpinBox)
from mybs.gui.ui_myui import Delegate
import re

class myTableView(QWidget):
    def __init__(self, file, type, parent=None) -> None:
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 9, 9, 9)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.rnColumnButton = QPushButton(self)
        self.rnColumnButton.setObjectName(u"rnColumnButton")
        self.rnColumnButton.setText(u"rename-Col")

        self.addColumnButton = QPushButton(self)
        self.addColumnButton.setObjectName('addcolumnbutton')
        self.addColumnButton.setText(self.tr('+col'))
        self.addColumnButton.setToolTip(self.tr('add new column'))

        self.removeColumnButton = QPushButton(self)
        self.removeColumnButton.setObjectName('removecolumnbutton')
        self.removeColumnButton.setText(self.tr('-col'))
        self.removeColumnButton.setToolTip(self.tr('remove a column'))

        self.disColumnButton = QPushButton(self)
        self.disColumnButton.setObjectName('discolumnbutton')
        self.disColumnButton.setText(self.tr('dis'))
        self.disColumnButton.setToolTip(self.tr('dis'))
        self.startsub = QPushButton(self)
        self.startsub.setObjectName('ssub')
        self.startsub.setText(self.tr('查找替换'))

        self.horizontalLayout.addWidget(self.rnColumnButton)
        self.horizontalLayout.addWidget(self.addColumnButton)
        self.horizontalLayout.addWidget(self.removeColumnButton)
        self.horizontalLayout.addWidget(self.disColumnButton)
        self.horizontalLayout.addWidget(self.startsub)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tableView = QTableView(self)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.tableView.setGridStyle(Qt.DashDotLine)
        self.tableView.setAlternatingRowColors(True)
        self.verticalLayout.addWidget(self.tableView)
        QMetaObject.connectSlotsByName(self)

        self.dm = dm(file, type)
        self.tableView.setModel(self.dm)
        self.tableView.setItemDelegate(Delegate())

        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.horizontalHeader().setSelectionMode(QHeaderView.SingleSelection)
        self.tableView.horizontalHeader().sectionPressed.connect(self.onhheadclicked)
        self.tableView.horizontalHeader().setSectionsMovable(True)

        self.tableView.verticalHeader().setSelectionMode(QHeaderView.SingleSelection)
        self.tableView.verticalHeader().sectionPressed.connect(self.onvheadclicked)
        self.tableView.verticalHeader().setSectionsMovable(True)

        self.ctrl = False
        self.selectedcol = []
        self.selectedrow = []

        self.removeColumnButton.clicked.connect(self.delcolumn)
        self.addColumnButton.clicked.connect(self.showaddcolumn)
        self.rnColumnButton.clicked.connect(self.rename)
        self.disColumnButton.clicked.connect(self.showdis)
        self.startsub.clicked.connect(self.showsub)
        



    def onhheadclicked(self, index):
        if not self.ctrl:
            self.selectedcol.clear()
            self.selectedrow.clear()
        if index in self.selectedcol:
            self.selectedcol.remove(index)
        else:
            self.selectedcol.append(index)
        print(self.selectedcol)

    def onvheadclicked(self, index):
        if not self.ctrl:
            self.selectedrow.clear()
            self.selectedcol.clear()
        if index in self.selectedrow:
            self.selectedrow.remove(index)
        else:
            self.selectedrow.append(index)
        print(self.selectedrow)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self.tableView)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self.ctrl = True
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self.ctrl = False
        return super().keyReleaseEvent(event)

    def deleterow(self):
        self.selectedrow.sort()
        if QMessageBox.question(self, '删除行！', f'确定要移除{", ".join(self.selectedrow)}吗', QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
            for i in self.selectedrow[::-1]:
                self.dm.removeRow(i)
    def delcolumn(self):
        self.selectedcol.sort()
        col = [self.dm.headerData(i, Qt.Horizontal, Qt.DisplayRole) for i in self.selectedcol]
        if QMessageBox.question(self, '删除列！', f'确定要移除{", ".join(col)}吗', QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
            for i in self.selectedcol[::-1]:
                self.dm.removeColumn(i)
    def showaddcolumn(self):
        dialog = AddAttributesDialog(self)
        dialog.acceptvalue.connect(self.dm.addDataFrameColumn)
        dialog.show()
    def rename(self):
        renames = {}
        for i in self.selectedcol:
            oldn = self.dm.headerData(i, Qt.Horizontal, Qt.DisplayRole)
            name = QInputDialog.getText(self,'改名',f'{oldn} 的新名字：',text=oldn)
            if name[1]:
                renames[oldn] = name[0]
        print(renames)
        if renames:
            self.dm.rename(columns=renames)

    def allowsort(self, boo):
        self.tableView.setSortingEnabled(boo)
        self.tableView.horizontalHeader().setProperty("showSortIndicator", boo)
    def showdis(self):
        if len(self.selectedcol)!=1:
            return
        col = self.selectedcol[0]
        if (dtype:=self.dm._data.dtypes[col]) in SupportedDtypes.numTypes():

            dialog = DisDialog(col, self, dtype not in SupportedDtypes.floatTypes())
            dialog.acceptvalue.connect(self.dm.dis)
            dialog.show()
    def showsub(self):
        if len(self.selectedcol)!=1:
            return
        col = self.selectedcol[0]
        dialog = subDialog(col, self, self.dm._data.dtypes[col])
        dialog.acceptvalue.connect(self.dm.sub)
        dialog.show()

class AddAttributesDialog(QDialog):

    acceptvalue = Signal(str, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUi()

    def initUi(self):
        self.setModal(True)
        self.resize(303, 168)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)

        self.verticalLayout = QVBoxLayout(self)

        self.dialogHeading = QLabel(
            self.tr('Add a new attribute column'), self)

        self.gridLayout = QGridLayout()

        self.columnNameLineEdit = QLineEdit(self)
        self.columnNameLabel = QLabel(self.tr('Name'), self)
        self.dataTypeComboBox = QComboBox(self)

        self.dataTypeComboBox.addItems(SupportedDtypes.names())

        self.columnTypeLabel = QLabel(self.tr('Type'), self)
        self.defaultValueLineEdit = QLineEdit(self)
        self.lineEditValidator = DefaultValueValidator(self)
        self.defaultValueLineEdit.setValidator(self.lineEditValidator)
        self.defaultValueLabel = QLabel(self.tr('Inital Value(s)'), self)

        self.gridLayout.addWidget(self.columnNameLabel, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.columnNameLineEdit, 0, 1, 1, 1)

        self.gridLayout.addWidget(self.columnTypeLabel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.dataTypeComboBox, 1, 1, 1, 1)

        self.gridLayout.addWidget(self.defaultValueLabel, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.defaultValueLineEdit, 2, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.dialogHeading)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.dataTypeComboBox.currentIndexChanged.connect(
            self.updateValidatorDtype)
        self.updateValidatorDtype(self.dataTypeComboBox.currentIndex())

    def accept(self):
        super().accept()

        newColumn = self.columnNameLineEdit.text()
        dtype = SupportedDtypes.dtype(self.dataTypeComboBox.currentText())

        defaultValue = self.defaultValueLineEdit.text()
        res, defaultValue, _ = self.lineEditValidator.validate(defaultValue, 0)
        if res == QValidator.Invalid:
            defaultValue = dtype.type()
        self.acceptvalue.emit(newColumn, dtype, defaultValue)

    def updateValidatorDtype(self, index):
        (dtype, name) = SupportedDtypes.tupleAt(index)
        self.defaultValueLineEdit.clear()
        self.lineEditValidator.validateType(dtype)

class DisDialog(QDialog):

    acceptvalue = Signal(list, int)
    class sub(QWidget):
        
        def __init__(self, parent, isint=True) -> None:
            super().__init__(parent)
            self.hlayout = QHBoxLayout(self)
            self.input = QSpinBox(self) if isint else QDoubleSpinBox(self)
            self.signal = False
            self.check = QCheckBox(self)
            self.check.setChecked(self.signal)
            self.check.setText('point')
            self.newname = QLineEdit(self)
            self.hlayout.addWidget(self.check)
            self.hlayout.addWidget(self.input)
            self.hlayout.addWidget(self.newname)

        def getdata(self):
            return self.input.value(), self.check.isChecked(), self.newname.text()
    def __init__(self, col, parent=None, isint=True):
        super().__init__(parent)
        self.isint = isint
        self.col = col

        self.initUi()

    def initUi(self):
        self.setModal(True)
        self.resize(303, 168)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)

        self.verticalLayout = QVBoxLayout(self)

        self.dialogHeading = QLabel(
            self.tr('离散化'), self)

        self.gridLayout = QGridLayout()

        
        self.sublist=[]
        self.add()
        self.defaultlayout = QHBoxLayout()
        self.columnTypeLabel = QLabel(self.tr('default'), self)
        self.defaultValueLineEdit = QLineEdit(self)
        self.defaultlayout.addWidget(self.columnTypeLabel)
        self.defaultlayout.addWidget(self.defaultValueLineEdit)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.addbutt = QPushButton(self)
        self.addbutt.setObjectName('add')
        self.addbutt.setText(self.tr('add'))

        self.verticalLayout.addWidget(self.dialogHeading)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.addLayout(self.defaultlayout)
        self.verticalLayout.addWidget(self.addbutt)
        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.addbutt.clicked.connect(self.add)

        

    def accept(self):
        super().accept()

        data = [i.getdata() for i in self.sublist] + [self.defaultValueLineEdit.text()]
        
        self.acceptvalue.emit(data, self.col)

    def add(self):
        self.sublist.append(self.sub(self, self.isint))
        self.gridLayout.addWidget(self.sublist[-1])


class subDialog(QDialog):

    acceptvalue = Signal( object, int, object)
    
    def __init__(self, col, parent=None, detype=None):
        super().__init__(parent)
        self.detype = detype
        self.col = col
        self.va = DefaultValueValidator(self)
        self.va.validateType(self.detype)
        self.initUi()

    def initUi(self):
        self.setModal(True)
        self.resize(303, 168)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)

        self.verticalLayout = QVBoxLayout(self)

        self.dialogHeading = QLabel(
            self.tr('chazhaotihuan'), self)

        self.gridLayout = QGridLayout()

        self.selectcol = QComboBox(self)
        self.selectcol.addItems(['正则','表达式'])
        self.selectcol.setCurrentIndex(0)
        
        self.defaultlayout = QHBoxLayout()
        self.columnTypeLabel = QLabel(self.tr('选择查找方式'), self)
        self.defaultlayout.addWidget(self.columnTypeLabel)
        self.defaultlayout.addWidget(self.selectcol)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.rule = QLineEdit('规则', self)
        self.nv = QLineEdit('替换值', self)


        self.verticalLayout.addLayout(self.defaultlayout)
        self.verticalLayout.addWidget(self.rule)
        self.verticalLayout.addWidget(self.nv)
        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


    

    def accept(self):
        super().accept()
        text = self.nv.text()
        res, text,_ = self.va.validate(text,0)
        if res == QValidator.Invalid:
            return
        if self.selectcol.currentIndex()==0:
            def func(x):
                return re.match(self.rule.text(), str(x)) is not None
                    
        elif self.selectcol.currentIndex()==1:
            def func(x):
                return eval(self.rule.text())
                    
        
        
        self.acceptvalue.emit(func, self.col, text)

