from pathlib import Path
from .typing import Config, List, Union
from .typing import QAbstractItemModel, Optional, Qt, QModelIndex, QFileSystemWatcher, QAbstractListModel, QIcon
from .util import load_jsons, save_jsons



class treenode:
    def __init__(self, parent, name: str, isfile: bool = False) -> None:
        self.parent = parent
        if isfile:
            self.file = Path(name)
        self.datas = [self.file.name, 'file', name] if isfile else [
            name, 'dir']
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

    def findfile(self, name):
        if self.isfile and self.data(2) == name:
            return self
        for i in self.chi:
            if ans := i.findfile(name):
                return ans

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

    def fileinfo(self):
        if self.isfile:
            return self.file.name
    def read(self):
        pass


class filemaster(QAbstractItemModel):
    columns = ('name', 'type', 'path')

    editable = None
    dragable = True

    def __init__(self, parent=None, columns=None):

        if columns is not None:
            self.columns = columns

        QAbstractItemModel.__init__(self, parent=parent)
        self.rootnode = treenode(None, '/')
        self.fw = QFileSystemWatcher(parent)

        if self.editable is None:
            self.editable = [False, ] * len(self.columns)

    def vqEdited(self, pnode, col, value):
        return value

    def findfile(self, name: str):
        return self.rootnode.findfile(name)

    def removeRow(self, row: int, parent):
        if parent is None:
            parent = self.rootnode
        i = len(parent.chi)
        self.beginRemoveRows(self._index(parent), i, i)
        parent.chi.pop(row)
        self.endRemoveRows()
        self.layoutChanged.emit()

    def remove(self, node: treenode):
        parent = node.parent
        if parent is None:
            return
        i = len(parent.chi)
        self.beginRemoveRows(self._index(parent), i, i)
        parent.chi.pop(node.row())
        self.endRemoveRows()
        self.layoutChanged.emit()

    def appends(self, name: str, chi: dict, parent=None):
        node = self.append(name, parent, chi is None)
        if chi and node:
            for k, v in chi.items():
                self.appends(k, v, node)

    def append(self, name, parent: Optional[treenode] = None, isfile=False):
        if parent is None:
            parent = self.rootnode
        if isfile and not self.fw.addPath(name):
            return
        i = len(parent.chi)
        self.beginInsertRows(self._index(parent), i, i)
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
        ind = index.internalPointer()
        if not ind.isfile:
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

        if role == Qt.DecorationRole and index.column() == 0:
            if item.isfile:
                return QIcon.fromTheme('text-html')
            return QIcon.fromTheme('folder')

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
        self.save()
        return True

    def headerData(self, column, orientation, role):
        if (orientation == Qt.Horizontal and
                role == Qt.DisplayRole):
            return self.columns[column]

        return None

    def _index(self, node: treenode):
        if node is None:
            return QModelIndex()
        if node.parent is None:
            return QModelIndex()
        return self.createIndex(node.row(), 0, node)

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
        for k, v in load_jsons(self.fdp).items():
            self.appends(k, v)
        self.save()

    def save(self):
        return save_jsons(self.fdp, self.rootnode.todict())
