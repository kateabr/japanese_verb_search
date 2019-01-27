from pathlib import Path
from typing import List

from PyQt5.QtCore import QModelIndex, QRegularExpression, Qt, QObject, QEvent
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QShortcut

from jvs import LoadFilesThread
from jvs import TextFile, TextFilesModel, TextFilesProxyModel
from jvs.uic import Ui_MainWindow


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
        # action signals
        self.actionOpenDir.triggered.connect(self.openWorkingDir)
        self.actionExport.triggered.connect(self.exportSearchResults)
        self.actionExit.triggered.connect(QApplication.exit)

        # update text view
        self.filesView.selectionModel().currentChanged.connect(self.displayTextFile)

        # filter files on these signals
        self.searchBox.textChanged.connect(lambda _: (
            self.filterFiles(),
            self.statusBar.showMessage(f"Number of filtered files: {self.proxyModel.rowCount()}")
        ) if self.actionRealtimeSearch.isChecked() else None)
        self.searchBox.editingFinished.connect(lambda: (
            self.filterFiles(),
            self.statusBar.showMessage(f"Number of filtered files: {self.proxyModel.rowCount()}")
        ))
        self.actionRegExpSearch.changed.connect(lambda: (
            self.filterFiles(),
            self.statusBar.showMessage(f"Number of filtered files: {self.proxyModel.rowCount()}")
        ))

        # update file list
        self.loadThread.loaded.connect(lambda files: (
            self.model.setFiles(files),
            self.statusBar.showMessage(f"Number of files loaded: {self.model.filesCount}")
        ))

        # progressbar related signals
        self.loadThread.started.connect(self.progressBar.show)
        self.loadThread.statusChanged.connect(self.progressBar.setValue)
        self.loadThread.finished.connect(self.progressBar.hide)

    def exportSearchResults(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Export Directory"),
            str(self.workingDir),
            self.tr("Text (*.txt)")
        )

        if len(fileName) == 0:
            return

        filePath: Path = Path(fileName)

        files: List[TextFile] = self.proxyModel.filteredFiles()
        found = [self.searchBoxRegex().pattern()]
        for file in files:
            for idx in file.occurenceLineList(self.searchBoxRegex()):
                match = ""
                if idx - 1 >= 0:
                    match += file[idx - 1]
                match += file[idx]
                if idx + 1 < file.linesCount():
                    match += file[idx + 1]

                found.append(match)

        filePath.touch(exist_ok=True)
        filePath.write_text("\n\n".join(found), "utf-8", )

    def openWorkingDir(self):
        workingDir: str = QFileDialog.getExistingDirectory(
            self,
            self.tr("Open Directory"),
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

    def displayTextFile(self, ind: QModelIndex):
        if not ind.isValid():
            self.textView.clear()
            return

        model_idx: QModelIndex = self.proxyModel.mapToSource(ind)
        file: TextFile = self.model.data(model_idx, Qt.UserRole).value()

        self.textView.setPlainText(file.content)
        self.highlightQuery()

    def highlightQuery(self):
        self.textView.highlight(self.searchBoxRegex())

    def searchBoxRegex(self) -> QRegularExpression:
        return QRegularExpression(self.searchBox.text(), QRegularExpression.CaseInsensitiveOption)

    def filterFiles(self):
        regex = self.searchBoxRegex()
        regexSearch = self.actionRegExpSearch.isChecked()

        self.proxyModel.setFilter(regex)
        self.proxyModel.setUseRegExp(regexSearch)
        self.highlightQuery()
