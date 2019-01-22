from pathlib import Path

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class LyricsLoadThread(QThread):
    loadStarted = pyqtSignal()
    loadStatusChanged = pyqtSignal(int, name="loadStatusChanged")
    itemsLoaded = pyqtSignal(dict, name="itemsLoaded")
    loadFinished = pyqtSignal()

    def __init__(self, dir=Path().cwd()):
        super().__init__()
        self._working_dir = dir

    def set_working_dir(self, dir: Path):
        self._working_dir = dir

    def run(self):
        self.loadStarted.emit()
        self.loadStatusChanged.emit(0)

        files = []
        for file in self._working_dir.iterdir():
            if file.is_file() and file.suffix == ".txt":
                files.append(self._working_dir.joinpath(file))

        files_cnt = len(files)
        items = {}
        for i, file in enumerate(files):
            file_content = []
            try:
                with file.open(encoding="utf-8") as f:
                    file_content = f.readlines()
            except IOError as ex:
                print(ex)
            items[file] = file_content

            progress = round((i / files_cnt) * 100)
            self.loadStatusChanged.emit(progress)

        self.itemsLoaded.emit(items)
        self.loadFinished.emit()


class HighlightTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()

        self.setFont(QFont("Yu Gothic"))
        self.setReadOnly(True)
        self.setFontPointSize(11)

    def highlight_word(self, word: str, color: QColor = QColor(Qt.yellow)):
        if word == "":
            return

        self.moveCursor(QTextCursor.Start, QTextCursor.MoveAnchor)
        scan_results = []
        while self.find(word):
            result: QTextEdit.ExtraSelection = QTextEdit.ExtraSelection()
            result.format.setBackground(color)

            result.cursor = self.textCursor()
            scan_results.append(result)

        self.setExtraSelections(scan_results)


class ProxyContentModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        regex: QRegExp = self.filterRegExp()
        if regex.pattern() == "":
            return True

        index: QModelIndex = self.sourceModel().index(sourceRow, 0, sourceParent)
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
        self._load_thread = LyricsLoadThread(self._working_dir)

        self._model = QStandardItemModel()
        self._proxy_model = ProxyContentModel(self)
        self._proxy_model.setSourceModel(self._model)
        self._files_view.setModel(self._proxy_model)

        self._lyrics_edit = HighlightTextEdit()
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
        self._search.editingFinished.connect(self._update_view)

        self._load_thread.loadStarted.connect(self._progressbar.show)
        self._load_thread.loadStatusChanged.connect(self._progressbar.setValue)
        self._load_thread.itemsLoaded.connect(self._load_items)
        self._load_thread.loadFinished.connect(self._progressbar.hide)

    def _load_lyrics(self):
        self._model.clear()
        self._load_thread.set_working_dir(self._working_dir)
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
        self._lyrics_edit.highlight_word(self._search.text())

    def _update_view(self):
        search_text = self._search.text()
        reg_exp: QRegExp = QRegExp(search_text, Qt.CaseInsensitive)
        self._proxy_model.setFilterRegExp(reg_exp)
        self._lyrics_edit.highlight_word(search_text)
