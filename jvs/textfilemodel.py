from pathlib import Path
from typing import List

from PyQt5.QtCore import QRegularExpression, QAbstractListModel, QModelIndex, Qt, QVariant, QSortFilterProxyModel


class TextFile:
    def __init__(self, path: Path, content: List[str]):
        self._path = path
        self._content = content

    @property
    def path(self) -> Path:
        return self._path

    @property
    def content(self) -> List[str]:
        return self._content

    def contains(self, regex: QRegularExpression) -> bool:
        return any(regex.match(line).hasMatch() for line in self._content)


class TextFilesModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__()

        self._files = []
        self._filesLength = 0

    def clear(self):
        self.beginResetModel()
        self._files = []
        self._filesLength = 0
        self.endResetModel()

    def setFiles(self, files: List[TextFile]):
        self.beginResetModel()
        self._files = files
        self._filesLength = len(self._files)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._filesLength

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        fileIdx = index.row()
        if not index.isValid() or (fileIdx < 0 or fileIdx >= self._filesLength):
            return QVariant()

        file = self._files[fileIdx]
        if role == Qt.DisplayRole:
            return QVariant(file.path.name)
        elif role == Qt.UserRole:
            return QVariant(file)

        return QVariant()

    # def canFetchMore(self, QModelIndex) -> bool:
    #     pass
    #
    # def fetchMore(self, QModelIndex):
    #     pass

    # def headerData(self, p_int, Qt_Orientation, role=None):
    #     pass


class TextFilesProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter = QRegularExpression()

    def setFilter(self, regex_filter: QRegularExpression):
        self._filter = regex_filter
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        if self._filter.pattern() == "":
            return True

        index: QModelIndex = self.sourceModel().index(source_row, 0, source_parent)
        file: TextFile = self.sourceModel().data(index, Qt.UserRole).value()
        return file.contains(self._filter)
