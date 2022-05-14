from pathlib import Path
from os import stat
import time
from .typing import Config, List, Union
from .typing import QAbstractItemModel, Optional, Qt, QModelIndex, QFileSystemWatcher, QIcon
from .util import load_jsons, save_jsons, filesize
from typing import Optional

class treenode:
    typelist = {
        '.json': 'json',
        '.csv': 'csv',
        '.excel': 'excel',
        '.xls': 'excel',
        '.xlsx': 'excel'
    }

    def __init__(self, parent, name: str, isfile: bool = False, setting=None) -> None:
        self.parent = parent
        self.isfile = isfile
        self.file = Path(name).resolve() if isfile else name
        self.name = self.file.name if isfile else name
        self.setting = setting if setting is not None else {'open': {}}
        self.datas = [self.file.name, 'file', name] if isfile else [
            name, 'dir']
        self.chi = []
        self.parent: treenode
        self.datas: List[str]
        self.chi: List[treenode]

    def append(self, child, isfile=False, setting=None):
        if not isinstance(child, treenode):
            child = treenode(self, child, isfile, setting)
        self.chi.append(child)
        return child

    def remove(self, row):
        return self.chi.pop(row)

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
        return 3

    def data(self, column):
        if column == 0:
            return self.name
        if column == 1:
            return 'file' if self.isfile else 'dir'
        if column == 2:
            if self.isfile:
                return str(self.file)
            if self.parent is None:
                return ''
            return self.parent.data(2)+'/'+self.name
        return None

    def setdata(self, col, value):
        if col == 0:
            if self.isfile:
                return
            self.file = value
            self.name = value

    def row(self):
        if self.parent:
            return self.parent.chi.index(self)
        return 0

    def todict(self):
        return {
            'name': str(self.file),
            'isfile': self.isfile,
            'setting': self.setting,
            'child': [i.todict() for i in self.chi]
        }

    def fileinfo(self):
        if self.isfile:
            info = stat(self.file.resolve().__str__())

            return f'{self.file.name}      Size:  {filesize(info.st_size)}     创建时间：{time.ctime(info.st_ctime)}'

    @property
    def type(self):
        if self.isfile:
            return self.typelist.get(self.file.suffix)


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
        parent.remove(row)
        self.endRemoveRows()
        self.layoutChanged.emit()

    def remove(self, node: treenode):
        parent = node.parent
        if parent is None:
            return
        i = len(parent.chi)
        self.beginRemoveRows(self._index(parent), i, i)
        parent.remove(node.row())
        self.endRemoveRows()
        self.layoutChanged.emit()

    def appends(self, name, parent=None, isfile=False, setting=None, child=[]):
        node = self.append(name, parent, isfile, setting)
        if node:
            for i in child:
                self.appends(**i, parent=node)

    def append(self, name, parent: Optional[treenode] = None, isfile=False, setting=None):
        if parent is None:
            parent = self.rootnode
        if isfile and not self.fw.addPath(name):
            return
        i = len(parent.chi)
        self.beginInsertRows(self._index(parent), i, i)
        node = parent.append(name, isfile, setting)
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
        if col == 0 and not ind.isfile:
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

        node.setdata(index.column(), value)
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
        for i in load_jsons(self.fdp).get('child', []):
            self.appends(**i)
        self.save()

    def save(self):
        return save_jsons(self.fdp, self.rootnode.todict())
