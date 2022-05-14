from pathlib import Path
from .typing import Config, List, Union, Optional
from .typing import Qt, QModelIndex, QAbstractTableModel, QDateTime, QPersistentModelIndex, QValidator
import pandas as pd
import numpy as np
from .util import SupportedDtypes
import re


class datamaster(QAbstractTableModel):
    pread = {
        'json': pd.read_json,
        'csv': pd.read_csv,
        'excel': pd.read_excel,
    }
    _float_precisions = {
        "float16": np.finfo(np.float16).precision - 2,
        "float32": np.finfo(np.float32).precision - 1,
        "float64": np.finfo(np.float64).precision - 1
    }

    """list of int datatypes for easy checking in data() and setData()"""
    _intDtypes = SupportedDtypes.intTypes() + SupportedDtypes.uintTypes()
    """list of float datatypes for easy checking in data() and setData()"""
    _floatDtypes = SupportedDtypes.floatTypes()
    """list of bool datatypes for easy checking in data() and setData()"""
    _boolDtypes = SupportedDtypes.boolTypes()
    """list of datetime datatypes for easy checking in data() and setData()"""
    _dateDtypes = SupportedDtypes.datetimeTypes()

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

    def setDatas(self, func, col, value) -> bool:
        self._data.loc[self.select(func, col), col] = value
        self.layoutChanged.emit()

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
        """
        Renames the dataframe inplace calling appropriate signals.
        Wraps pandas.DataFrame.rename(*args, **kwargs) - overrides
        the inplace kwarg setting it to True.
        Example use:
        renames = {'colname1':'COLNAME_1', 'colname2':'COL2'}
        DataFrameModel.rename(columns=renames)
        :param args:
            see pandas.DataFrame.rename
        :param kwargs:
            see pandas.DataFrame.rename
        :return:
            None
        """
        kwargs['inplace'] = True
        self.layoutAboutToBeChanged.emit()
        self._data.rename(index=index, columns=columns, **kwargs)
        self.layoutChanged.emit()

    def select(self, func, col=None):
        if col is None:
            col = self._data.columns

        def newfunc(data):
            ret = []
            for i in data.index:
                if func(data.loc[i, col]):
                    ret.append(i)
            return ret
        return newfunc

    def mask(self, func, cols):
        return pd.DataFrame({
            col: list(map(func, self._data[col])) for col in cols
        })
    def sub(self, func, col, val):
        col = self._data.columns[col]
        self._data.loc[self.select(func, col), col] = val
        self.layoutChanged.emit()
    def dis(self, data, col):
        default = data.pop()
        data:list.sort(key=lambda x:x[0])
        col = self._data.columns[col]
        def func(x):
            for i in data:
                if (x==i[0] if i[1] else x<i[0]):
                    return i[2]
            return default
        self._data[col] = self.mask(func, [col])
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


class DefaultValueValidator(QValidator):
    def __init__(self, parent=None):
        super(DefaultValueValidator, self).__init__(parent)
        self.dtype = None

        self.intPattern = re.compile('[-+]?\d+')
        self.uintPattern = re.compile('\d+')
        self.floatPattern = re.compile('[+-]? *(?:\d+(?:\.\d*)?|\.\d+)')
        self.boolPattern = re.compile('(1|t|0|f){1}$')

    def validateType(self, dtype):
        self.dtype = dtype

    def fixup(self, string):
        pass

    def validate(self, s, pos):
        if not s:
            # s is emtpy
            return (QValidator.Acceptable, s, pos)

        if self.dtype in SupportedDtypes.strTypes():
            return (QValidator.Acceptable, s, pos)

        elif self.dtype in SupportedDtypes.boolTypes():
            match = re.match(self.boolPattern, s)
            if match:
                return (QValidator.Acceptable, s in '1t', pos)
            else:
                return (QValidator.Invalid, s in '1t', pos)

        elif self.dtype in SupportedDtypes.datetimeTypes():
            try:
                ts = pd.Timestamp(s)
            except ValueError as e:
                return (QValidator.Intermediate, s, pos)
            return (QValidator.Acceptable, ts, pos)

        else:
            dtypeInfo = None
            if self.dtype in SupportedDtypes.intTypes():
                match = re.search(self.intPattern, s)
                if match:
                    try:
                        value = int(match.string)
                    except ValueError as e:
                        return (QValidator.Invalid, s, pos)

                    dtypeInfo = np.iinfo(self.dtype)

            elif self.dtype in SupportedDtypes.uintTypes():
                match = re.search(self.uintPattern, s)
                if match:
                    try:
                        value = int(match.string)
                    except ValueError as e:
                        return (QValidator.Invalid, s, pos)

                    dtypeInfo = np.iinfo(self.dtype)

            elif self.dtype in SupportedDtypes.floatTypes():
                match = re.search(self.floatPattern, s)
                print(match)
                if match:
                    try:
                        value = float(match.string)
                    except ValueError as e:
                        return (QValidator.Invalid, s, pos)

                    dtypeInfo = np.finfo(self.dtype)

            if dtypeInfo is not None:
                if value >= dtypeInfo.min and value <= dtypeInfo.max:
                    return (QValidator.Acceptable, value, pos)
                else:
                    return (QValidator.Invalid, s, pos)
            else:
                return (QValidator.Invalid, s, pos)

        return (QtGui.QValidator.Invalid, s, pos)
