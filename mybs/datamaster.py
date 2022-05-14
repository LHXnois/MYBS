from pathlib import Path
from .typing import Config, List, Union, Optional
from .typing import Qt, QModelIndex, QAbstractTableModel, QPersistentModelIndex, QValidator
import pandas as pd
import numpy as np
from .util import SupportedDtypes, DefaultValueValidator


class datamaster(QAbstractTableModel):
    pread = {
        'json': pd.read_json,
        'csv': pd.read_csv,
        'excel': pd.read_excel,
    }

    def __init__(self, file: Path, type: str, parent=None) -> None:
        super().__init__(parent)
        self.type = type
        self._data = self.pread.get(type)(file)
        self._data: pd.DataFrame
        self.ValueValidator = DefaultValueValidator(parent)

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[col]
            if orientation == Qt.Vertical:
                return col
        return None

    def flags(self, index):
        if not index.isValid():
            return 0
        flags = QAbstractTableModel.flags(self, index)
        col = index.column()
        ind = index.internalPointer()
        flags |= Qt.ItemIsEditable

        return flags

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False

        if value != index.data(role):

            self.layoutAboutToBeChanged.emit()

            row = self._data.index[index.row()]
            col = self._data.columns[index.column()]
            # print 'before change: ', index.data().toUTC(), self._dataFrame.iloc[row][col]
            columnDtype = self._data[col].dtype
            self.ValueValidator.validateType(columnDtype)
            res, value, _ = self.ValueValidator.validate(value, index)
            if res == QValidator.Acceptable:

                self._data.loc[row, col] = value

            # print 'after change: ', value, self._dataFrame.iloc[row][col]
                self.layoutChanged.emit()
                return True
        return False

    def rename(self, index=None, columns=None, **kwargs):
        kwargs['inplace'] = True
        self.layoutAboutToBeChanged.emit()
        self._data.rename(index=index, columns=columns, **kwargs)
        self.layoutChanged.emit()

    def mask(self, func, col=None):
        if col is None:
            col = self._data.columns

        def newfunc(data):
            ret = []
            for i in data.index:
                if func(data.loc[i, col]):
                    ret.append(i)
            return ret
        return newfunc

    def sub(self, func, col, val):
        col = self._data.columns[col]
        self._data.loc[self.mask(func, col), col] = val
        self.layoutChanged.emit()

    def select(self, func, cols):
        return pd.DataFrame({
            col: list(map(func, self._data[col])) for col in cols
        })

    def dis(self, data, col):
        default = data.pop()
        data.sort(key=lambda x: x[0])
        col = self._data.columns[col]

        def func(x):
            for i in data:
                if (x == i[0] if i[1] else x < i[0]):
                    return i[2]
            return default
        self._data[col] = self.select(func, [col])
        self.layoutChanged.emit()

    def addDataFrameColumn(self, columnName, dtype=str, defaultValue=None):

        if dtype not in SupportedDtypes.allTypes():
            return False

        elements = self.rowCount()
        columnPosition = self.columnCount()

        newColumn = pd.Series([defaultValue]*elements,
                              index=self._data.index, dtype=dtype)

        self.beginInsertColumns(
            QModelIndex(), columnPosition - 1, columnPosition - 1)
        try:
            self._data.insert(columnPosition, columnName,
                              newColumn, allow_duplicates=False)

        except ValueError as e:
            # columnName does already exist
            return False

        self.endInsertColumns()
        self.layoutChanged.emit()

        return True

    def removeRow(self, row: int, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> bool:
        self.beginMoveRows(parent, row, row)
        self._data.drop([row], inplace=True)
        self.endMoveRows()
        self.layoutChanged.emit()

    def removeColumn(self, column: int, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> bool:
        self.beginRemoveColumns(parent, column, column)
        self._data.drop(self._data.columns[column], axis=1, inplace=True)
        self.endRemoveColumns()
        self.layoutChanged.emit()

    def save(self):
        pass
