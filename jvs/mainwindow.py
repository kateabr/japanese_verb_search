from pathlib import Path
from typing import Dict

from PyQt5.QtCore import QModelIndex, QRegularExpression, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QShortcut

from jvs import TextFile, TextFilesModel, TextFilesProxyModel
from jvs.uic import Ui_MainWindow
from jvs import LoadFilesThread


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.workingDir = Path().cwd()
        self.loadThread = LoadFilesThread(self.workingDir)

        self.model = TextFilesModel(self)
        self.proxyModel = TextFilesProxyModel(self)
        self.proxyModel.setSourceModel(self.model)
        self.filesView.setModel(self.proxyModel)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        self.progressBar.hide()

        self.createShortcuts()
        self.createSignals()

    def createShortcuts(self):
        self.hkFocusOnSearch = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self, lambda: self.searchBox.setFocus())

    def createSignals(self):
        self.actionOpenDir.triggered.connect(self.openWorkingDir)
        self.actionExit.triggered.connect(QApplication.exit)

        self.filesView.selectionModel().currentChanged.connect(self.displayTextFile)
        self.searchBox.editingFinished.connect(self.filterFiles)

        self.loadThread.started.connect(self.progressBar.show)
        self.loadThread.statusChanged.connect(self.progressBar.setValue)
        self.loadThread.loaded.connect(self.updateModel)
        self.loadThread.finished.connect(self.progressBar.hide)

    def openWorkingDir(self):
        workingDir: str = QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            str(self.workingDir),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if len(workingDir) == 0:
            return
        self.workingDir = Path(workingDir)
        self.startLoadingThread()

    def startLoadingThread(self):
        self.model.clear()
        self.loadThread.setWorkingDir(self.workingDir)
        self.loadThread.start()

    def updateModel(self, items: Dict[Path, str]):
        files = []
        for file, file_content in items.items():
            files.append(TextFile(file, file_content))
        self.model.setFiles(files)

    def displayTextFile(self, ind: QModelIndex):
        if not ind.isValid():
            self.textView.clear()
            return

        model_idx: QModelIndex = self.proxyModel.mapToSource(ind)
        file: TextFile = self.model.data(model_idx, Qt.UserRole).value()

        self.textView.setPlainText(file.content)
        self.textView.highlight(self.searchBoxRegex())

    def searchBoxRegex(self) -> QRegularExpression:
        return QRegularExpression(self.searchBox.text(), QRegularExpression.CaseInsensitiveOption)

    def filterFiles(self):
        regex = self.searchBoxRegex()
        self.proxyModel.setFilter(regex)
        self.textView.highlight(self.searchBoxRegex())
