from PyQt5.QtCore import Qt, QRegularExpression, QRegularExpressionMatchIterator, QRegularExpressionMatch
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat
from PyQt5.QtWidgets import QTextEdit


class HighlightTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()

    def highlight(self, regex: QRegularExpression, color: QColor = QColor(Qt.yellow)):
        if regex.pattern() == "":
            return

        self.moveCursor(QTextCursor.Start)
        matches = []
        it: QRegularExpressionMatchIterator = regex.globalMatch(self.toPlainText())
        while it.hasNext():
            match: QRegularExpressionMatch = it.next()
            if not match.hasMatch():
                continue
            begin = match.capturedStart()
            end = match.capturedEnd()

            matchSelection: QTextEdit.ExtraSelection = QTextEdit.ExtraSelection()
            fmt: QTextCharFormat = matchSelection.format
            fmt.setBackground(color)

            matchSelection.cursor = self.textCursor()
            matchSelection.cursor.setPosition(begin, QTextCursor.MoveAnchor)
            matchSelection.cursor.setPosition(end, QTextCursor.KeepAnchor)
            matches.append(matchSelection)

        self.setExtraSelections(matches)
        self.moveCursor(QTextCursor.Start)
