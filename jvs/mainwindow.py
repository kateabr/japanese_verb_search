from pathlib import Path

from PyQt5.QtCore import QModelIndex, QRegularExpression, QVariant, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QListView, QGridLayout, QSplitter, QMainWindow, QLineEdit, QLabel, \
    QAbstractItemView, QFileDialog, QProgressBar, QWidget, QAction

from jvs.highlighttextedit import HighlightTextEdit
from jvs.loadfilesthread import LoadFilesThread
from jvs.textfilemodel import TextFile, TextFilesModel, TextFilesProxyModel


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Japanese verb search")
        self.setMinimumSize(800, 600)

        self._createUi()
        self._createMenu()
        self._createSignals()

    def _createUi(self):
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

        self._model = TextFilesModel(self)
        self._proxy_model = TextFilesProxyModel(self)
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

    def _createMenu(self):
        menu = self.menuBar().addMenu("File")
        menu.addAction(QAction("Open", self, triggered=self._openWorkingDir))
        menu.addAction(QAction("Exit", self, triggered=QApplication.exit))

    def _openWorkingDir(self):
        _working_dir: str = QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            str(self._working_dir),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if len(_working_dir) == 0:
            return
        self._working_dir = Path(_working_dir)
        self._loadFiles()

    def _createSignals(self):
        self._files_view.selectionModel().currentChanged.connect(self._displayLyrics)
        self._search.editingFinished.connect(self._filterFiles)

        self._load_thread.started.connect(self._progressbar.show)
        self._load_thread.statusChanged.connect(self._progressbar.setValue)
        self._load_thread.loaded.connect(self._updateFilesModel)
        self._load_thread.finished.connect(self._progressbar.hide)

    def _loadFiles(self):
        self._model.clear()
        self._load_thread.setWorkingDir(self._working_dir)
        self._load_thread.start()

    def _updateFilesModel(self, items: dict):
        files = []
        for file, file_content in items.items():
            files.append(TextFile(file, file_content))
        self._model.setFiles(files)

    def _displayLyrics(self, ind: QModelIndex):
        if not ind.isValid():
            self._lyrics_edit.clear()
            return

        model_idx: QModelIndex = self._proxy_model.mapToSource(ind)
        item: QVariant = self._model.data(model_idx, Qt.UserRole).value()

        lyrics = "".join(item.content)
        self._lyrics_edit.setText(lyrics)
        self._lyrics_edit.highlight(self._searchRegex())

    def _searchRegex(self) -> QRegularExpression:
        return QRegularExpression(self._search.text(), QRegularExpression.CaseInsensitiveOption)

    def _filterFiles(self):
        regex = self._searchRegex()
        self._proxy_model.setFilter(regex)
