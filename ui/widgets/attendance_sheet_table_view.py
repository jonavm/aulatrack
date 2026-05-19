from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView


class AttendanceSheetTableView(QTableView):
    def keyPressEvent(self, event) -> None:
        index = self.currentIndex()
        model = self.model()

        if index.isValid() and event.text():
            text = event.text().strip().upper()
            if text in {"A", "P", "F", "R", "J"} and hasattr(model, "apply_text_value"):
                model.apply_text_value(index, text)
                self._move_vertical(index.row(), index.column(), 1)
                return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and index.isValid():
            self._move_vertical(index.row(), index.column(), 1)
            return

        if event.key() == Qt.Key_Tab and index.isValid():
            step = -1 if event.modifiers() & Qt.ShiftModifier else 1
            self._move_horizontal(index.row(), index.column(), step)
            return

        super().keyPressEvent(event)

    def _move_vertical(self, row: int, column: int, step: int) -> None:
        target_row = max(0, min(self.model().rowCount() - 1, row + step))
        self.setCurrentIndex(self.model().index(target_row, column))
        self.scrollTo(self.currentIndex())

    def _move_horizontal(self, row: int, column: int, step: int) -> None:
        target_column = max(1, min(self.model().columnCount() - 1, column + step))
        self.setCurrentIndex(self.model().index(row, target_column))
        self.scrollTo(self.currentIndex())
