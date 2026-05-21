from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QApplication, QMessageBox, QTableView

from ui.widgets.adjustment_dialog import AdjustmentDialog
from ui.widgets.deduction_entry_dialog import DeductionEntryDialog


class GradebookTableView(QTableView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.clicked.connect(self._handle_clicked)

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)

    def _handle_clicked(self, index: QModelIndex) -> None:
        if not index.isValid():
            return
        model = self.model()
        role_name = getattr(model, "USER_ROLE_DEDUCTION_TARGET", -1)
        target = index.data(role_name)
        if not target:
            adjustment_role = getattr(model, "USER_ROLE_ADJUSTMENT_TARGET", -1)
            adjustment_target = index.data(adjustment_role)
            if not adjustment_target:
                return
            dialog = AdjustmentDialog(
                student_name=adjustment_target["student_name"],
                current_points=adjustment_target["points"],
                entries=adjustment_target["entries"],
                parent=self,
            )
            if dialog.exec() == AdjustmentDialog.Accepted:
                model.setData(index, dialog.get_payload(), Qt.EditRole)
            return
        dialog = DeductionEntryDialog(
            student_name=target["student_name"],
            criterion_name=target["category_name"],
            max_points=target["max_points"],
            entries=target["entries"],
            parent=self,
        )
        if dialog.exec() == DeductionEntryDialog.Accepted:
            model.setData(index, dialog.get_payload(), Qt.EditRole)

    def keyPressEvent(self, event) -> None:
        index = self.currentIndex()
        model = self.model()

        if event.matches(QKeySequence.Paste) and index.isValid():
            self._paste_block(index.row(), index.column())
            return

        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if index.isValid():
                model.setData(index, None, Qt.EditRole)
                return
        if event.key() == Qt.Key_M and index.isValid():
            if hasattr(model, "apply_status"):
                model.apply_status(index, "missing")
                return
        if event.key() == Qt.Key_P and index.isValid():
            if hasattr(model, "apply_status"):
                model.apply_status(index, "pending")
                return
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and index.isValid():
            step = -1 if event.modifiers() & Qt.ShiftModifier else 1
            self._move_vertical(index.row(), index.column(), step)
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
        target_column = max(0, min(self.model().columnCount() - 1, column + step))
        self.setCurrentIndex(self.model().index(row, target_column))
        self.scrollTo(self.currentIndex())

    def _paste_block(self, start_row: int, start_column: int) -> None:
        text = QApplication.clipboard().text()
        if not text.strip():
            return

        rows = [line.split("\t") for line in text.replace("\r\n", "\n").split("\n") if line != ""]
        model = self.model()
        if not hasattr(model, "apply_text_value"):
            return

        max_rows = model.rowCount()
        max_columns = model.columnCount()

        for row_offset, values in enumerate(rows):
            row = start_row + row_offset
            if row >= max_rows:
                break
            for col_offset, value in enumerate(values):
                column = start_column + col_offset
                if column >= max_columns:
                    break
                index = model.index(row, column)
                model.apply_text_value(index, value)

        end_row = min(max_rows - 1, start_row + len(rows) - 1)
        end_col = min(max_columns - 1, start_column + max((len(r) for r in rows), default=1) - 1)
        self.setCurrentIndex(model.index(end_row, end_col))
        self.scrollTo(self.currentIndex())
