from pathlib import Path
from typing import List

from PyQt5.QtCore import QRegularExpression, QAbstractListModel, QModelIndex, Qt, QVariant, QSortFilterProxyModel, \
    QRegularExpressionMatch


class TextFile:
    def __init__(self, path: Path, content: str):
        self._path = path
        self._content = content
        self._contentLower = content.lower()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def content(self) -> str:
        return self._content

    def contains(self, regex: QRegularExpression, useRegExp=True) -> bool:
        if useRegExp:
            match: QRegularExpressionMatch = regex.match(self._content)
            return match.hasMatch()
        else:
            return regex.pattern().lower() in self._contentLower


class TextFilesModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._fileList = []
        self._filesCount = 0

    @property
    def filesCount(self):
        return self._filesCount

    def clear(self):
        self.beginResetModel()
        self._fileList = []
        self._filesCount = 0
        self.endResetModel()

    def setFiles(self, files: List[TextFile]):
        self.beginResetModel()
        self._fileList = files
        self._filesCount = len(self._fileList)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._filesCount

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        fileIdx = index.row()
        if not index.isValid() or (fileIdx < 0 or fileIdx >= self._filesCount):
            return QVariant()

        file = self._fileList[fileIdx]
        if role == Qt.DisplayRole:
            return QVariant(file.path.name)
        elif role == Qt.UserRole:
            return QVariant(file)

        return QVariant()


class TextFilesProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter = QRegularExpression()

    def setFilter(self, filesFilter: QRegularExpression):
        if self._filter == filesFilter:
            return

        self._filter = filesFilter
        self.invalidateFilter()

    def setUseRegExp(self, useRegExp: bool):
        self._useRegExp = useRegExp
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        if self._filter.pattern() == "":
            return True

        index: QModelIndex = self.sourceModel().index(sourceRow, 0, sourceParent)
        file: TextFile = self.sourceModel().data(index, Qt.UserRole).value()
        return file.contains(self._filter, self._useRegExp)
