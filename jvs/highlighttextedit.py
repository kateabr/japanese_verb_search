from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat
from PyQt5.QtWidgets import QTextEdit


class HighlightTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()

    def highlight(self, regex: QRegExp, color: QColor = QColor(Qt.yellow)):
        if regex.isEmpty():
            return

        self.moveCursor(QTextCursor.Start)
        matches = []
        while self.find(regex):
            match: QTextEdit.ExtraSelection = QTextEdit.ExtraSelection()
            fmt: QTextCharFormat = match.format
            fmt.setBackground(color)

            match.cursor = self.textCursor()
            matches.append(match)
        self.setExtraSelections(matches)

        self.moveCursor(QTextCursor.Start)
