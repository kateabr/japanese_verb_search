from pathlib import Path
from typing import Dict

from PyQt5.QtCore import QThread, pyqtSignal


class LoadFilesThread(QThread):
    statusChanged = pyqtSignal(int)
    loaded = pyqtSignal(dict)

    def __init__(self, working_dir):
        super().__init__()
        self._workingDir = working_dir

    def setWorkingDir(self, workingDir: Path):
        self._workingDir = workingDir

    def run(self):
        progress = 0
        self.statusChanged.emit(progress)

        files = []
        for file in self._workingDir.iterdir():
            if file.is_file() and file.suffix == ".txt":
                files.append(self._workingDir.joinpath(file))

        files_cnt = len(files)
        items: Dict[Path, str] = {}
        for i, file in enumerate(files):
            with file.open(encoding="utf-8") as f:
                file_content = "".join(f.readlines())
                items[file] = file_content

            prev = progress
            progress = round((i / files_cnt) * 100)
            if prev != progress:
                self.statusChanged.emit(progress)

        self.loaded.emit(items)
