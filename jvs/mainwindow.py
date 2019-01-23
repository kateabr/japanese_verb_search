from pathlib import Path

from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QRegExp
from PyQt5.QtWidgets import QApplication, QListView, QGridLayout, QSplitter, QMainWindow, QLineEdit, QLabel, \
    QAbstractItemView, QFileDialog, QProgressBar, QWidget, QAction
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QFont

from jvs.highlighttextedit import HighlightTextEdit
from jvs.loadfilesthread import LoadFilesThread


class ProxyContentModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        regex: QRegExp = self.filterRegExp()
        if regex.pattern() == "":
            return True

        index: QModelIndex = self.sourceModel().index(source_row, 0, source_parent)
        item: QStandardItem = self.sourceModel().itemFromIndex(index)
        content_join: str = "".join(item.data())

        return regex.indexIn(content_join, 0) != -1


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Japanese verb search")
        self.setMinimumSize(800, 600)

        self._create_ui()
        self._create_menu()
        self._create_signals()

    def _create_ui(self):
        layout: QGridLayout = QGridLayout()
        layout.addWidget(QLabel("Search"), 0, 0)

        self._search = QLineEdit()
        layout.addWidget(self._search, 0, 1)

        splitter = QSplitter()
        layout.addWidget(splitter, 1, 0, 1, 2)

        self._files_view = QListView()
        splitter.addWidget(self._files_view)
        self._files_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._files_view.setAlternatingRowColors(True)

        self._working_dir = Path().cwd()
        self._load_thread = LoadFilesThread(self._working_dir)

        self._model = QStandardItemModel()
        self._proxy_model = ProxyContentModel(self)
        self._proxy_model.setSourceModel(self._model)
        self._files_view.setModel(self._proxy_model)

        self._lyrics_edit = HighlightTextEdit()
        self._lyrics_edit.setFont(QFont("Yu Gothic"))
        self._lyrics_edit.setReadOnly(True)
        self._lyrics_edit.setFontPointSize(11)
        splitter.addWidget(self._lyrics_edit)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        self._progressbar = QProgressBar()
        layout.addWidget(self._progressbar, 2, 0, 1, 2)
        self._progressbar.setRange(0, 100)
        self._progressbar.hide()

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _create_menu(self):
        menu = self.menuBar().addMenu("File")
        menu.addAction(QAction("Open", self, triggered=self._open_dir))
        menu.addAction(QAction("Exit", self, triggered=QApplication.exit))

    def _open_dir(self):
        _working_dir: str = QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            str(self._working_dir),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if len(_working_dir) == 0:
            return
        self._working_dir = Path(_working_dir)
        self._load_lyrics()

    def _create_signals(self):
        self._files_view.selectionModel().currentChanged.connect(self._display_lyrics)
        self._search.editingFinished.connect(self._filter_files)

        self._load_thread.started.connect(self._progressbar.show)
        self._load_thread.statusChanged.connect(self._progressbar.setValue)
        self._load_thread.loaded.connect(self._load_items)
        self._load_thread.finished.connect(self._progressbar.hide)

    def _load_lyrics(self):
        self._model.clear()
        self._load_thread.setWorkingDir(self._working_dir)
        self._load_thread.start()

    def _load_items(self, items: dict):
        for file, file_content in items.items():
            item: QStandardItem = QStandardItem()
            item.setData(file_content)
            item.setText(file.name)
            self._model.appendRow(item)

    def _display_lyrics(self, ind: QModelIndex):
        if not ind.isValid():
            self._lyrics_edit.clear()
            return

        model_idx: QModelIndex = self._proxy_model.mapToSource(ind)
        item: QStandardItem = self._model.itemFromIndex(model_idx)

        lyrics = "".join(item.data())
        self._lyrics_edit.setText(lyrics)
        self._lyrics_edit.highlight(self._get_search_regex())

    def _get_search_regex(self):
        regex: QRegExp = QRegExp(self._search.text(), Qt.CaseInsensitive)
        return regex

    def _filter_files(self):
        regex = self._get_search_regex()
        self._proxy_model.setFilterRegExp(regex)
