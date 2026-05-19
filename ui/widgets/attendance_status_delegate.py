from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QWidget


class AttendanceStatusDelegate(QStyledItemDelegate):
    OPTIONS = [
        ("Presente", "present"),
        ("Falta", "absent"),
        ("Retardo", "late"),
        ("Justificada", "justified"),
    ]

    def createEditor(self, parent: QWidget, option, index):
        combo = QComboBox(parent)
        for label, value in self.OPTIONS:
            combo.addItem(label, value)
        return combo

    def setEditorData(self, editor, index) -> None:
        current_value = index.data(role=1002)
        for i in range(editor.count()):
            if editor.itemData(i) == current_value:
                editor.setCurrentIndex(i)
                break

    def setModelData(self, editor, model, index) -> None:
        model.setData(index, editor.currentData())

