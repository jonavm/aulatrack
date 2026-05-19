from __future__ import annotations

from PySide6.QtWidgets import QDoubleSpinBox, QStyledItemDelegate, QWidget


class GradeSpinDelegate(QStyledItemDelegate):
    def createEditor(self, parent: QWidget, option, index):
        max_score = index.data(1001)
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(1)
        editor.setRange(0.0, float(max_score or 100.0))
        editor.setSingleStep(1.0)
        editor.setFrame(False)
        return editor
