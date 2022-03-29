from .typing import Config, List, Union
from .typing import QAbstractItemModel, Optional, Qt, QModelIndex
from .util import load_jsons, save_jsons
from os import path


class treenode:
    def __init__(self, parent, name: str, isfile: bool = False) -> None:
        self.parent = parent
        self.datas = [path.basename(name), 'file', name] if isfile else [name, 'dir']
        self.isfile = isfile
        self.chi = []
        self.parent: treenode
        self.datas: List[str]
        self.chi: List[treenode]

    def append(self, name, isfile=False):
        child = treenode(self, name, isfile)
        self.chi.append(child)
        return child

    def child(self, row):
        return self.chi[row]

    def childCount(self):
        return len(self.chi)

    def columnCount(self):
        return len(self.datas)

    def data(self, column):
        if column < len(self.datas):
            return self.datas[column]
        return None

    def row(self):
        if self.parent:
            return self.parent.chi.index(self)
        return 0

    def todict(self):
        return {
            i.datas[2] if i.isfile else i.datas[0]: None if i.isfile else i.todict() for i in self.chi
        }


class filemaster(QAbstractItemModel):
    columns = ('name', 'type', 'path')

    editable = None
    dragable = False

    def __init__(self, parent=None, columns=None):

        if columns is not None:
            self.columns = columns

        QAbstractItemModel.__init__(self, parent=parent)
        self.rootnode = treenode(None, '/')

        if self.editable is None:
            self.editable = [False, ] * len(self.columns)

    def vqEdited(self, pnode, col, value):
        return value

    def appends(self, name: str, chi: dict, parent=None):
        node = self.append(name, parent, chi is None)
        if chi:
            for k, v in chi.items():
                self.appends(k, v, node)

    def append(self, name, parent: Optional[treenode] = None, isfile=False):
        if parent is None:
            parent = self.rootnode

        i = len(parent.chi)
        self.beginInsertRows(self.createIndex(parent.row(), 0, parent), i, i)
        node = parent.append(name, isfile)
        self.endInsertRows()
        self.layoutChanged.emit()
        return node

    def sort(self, colnum, order=0):
        # cmpf = VQTreeSorter(colnum, order)
        self.layoutAboutToBeChanged.emit()
        self.rootnode.chi = sorted(
            self.rootnode.chi, key=lambda item: item.datas[colnum], reverse=order)
        # self.rootnode.children.sort(key=cmpf)
        self.layoutChanged.emit()

    def flags(self, index):
        if not index.isValid():
            return 0
        flags = QAbstractItemModel.flags(self, index)
        col = index.column()
        if self.editable[col]:
            flags |= Qt.ItemIsEditable
        if self.dragable:
            flags |= Qt.ItemIsDragEnabled
        return flags

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())

        if role == Qt.UserRole:
            return item

        return None

    def setData(self, index, value, role=Qt.EditRole):

        node = index.internalPointer()
        if not node:
            return False

        # If this is the edit role, fire the vqEdited thing
        if role == Qt.EditRole:
            value = self.vqEdited(node, index.column(), value)
            if value is None:
                return False

        node.datas[index.column()] = value
        self.dataChanged.emit(index, index)

        return True

    def headerData(self, column, orientation, role):
        if (orientation == Qt.Horizontal and
                role == Qt.DisplayRole):
            return self.columns[column]

        return None

    def index(self, row, column, parent):

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        pitem = parent.internalPointer()
        if not pitem:
            pitem = self.rootnode

        item = pitem.child(row)
        if not item:
            return QModelIndex()

        return self.createIndex(row, column, item)

    def parent(self, index):

        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if not item:
            return QModelIndex()

        pitem = item.parent

        if pitem == self.rootnode:
            return QModelIndex()

        if pitem is None:
            return QModelIndex()

        return self.createIndex(pitem.row(), 0, pitem)

    def rowCount(self, parent=QModelIndex()):

        if parent.column() > 0:
            return 0

        pitem = parent.internalPointer()
        if not pitem:
            pitem = self.rootnode

        return len(pitem.chi)

    def setup(self, conf: Config) -> None:
        self.conf = conf
        self.fdp = conf.fdpath
        if path.exists(conf.fdpath):
            files = load_jsons(self.fdp)
        else:
            files = {}
        for k, v in files.items():
            self.appends(k, v)
        self.save()

    def save(self):
        return save_jsons(self.rootnode.todict(), self.fdp)
