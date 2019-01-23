from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal


class LoadFilesThread(QThread):
    statusChanged = pyqtSignal(int)
    loaded = pyqtSignal(dict)

    def __init__(self, working_dir=Path().cwd()):
        super().__init__()
        self._workingDir = working_dir

    def setWorkingDir(self, workingDir: Path):
        self._workingDir = workingDir

    def run(self):
        self.started.emit()
        self.statusChanged.emit(0)

        files = []
        for file in self._workingDir.iterdir():
            if file.is_file() and file.suffix == ".txt":
                files.append(self._workingDir.joinpath(file))

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
            self.statusChanged.emit(progress)

        self.loaded.emit(items)
        self.finished.emit()
