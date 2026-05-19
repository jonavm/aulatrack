from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.entities import EvaluationCategory


class CategoryTableModel(QAbstractTableModel):
    HEADERS = ["Criterio", "Puntos", "Calculo", "Estado", "Items"]

    def __init__(self) -> None:
        super().__init__()
        self._items: list[EvaluationCategory] = []

    def set_items(self, items: list[EvaluationCategory]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str | None:
        if not index.isValid():
            return None
        item = self._items[index.row()]
        values = [
            item.name,
            f"{item.weight_percent:.1f}",
            "Deduccion" if item.category_mode == "deduction" else "Promedio",
            "Activa" if item.is_active else "Inactiva",
            str(item.activity_count),
        ]
        if role == Qt.DisplayRole:
            return values[index.column()]
        if role == Qt.UserRole:
            return item
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        return self.HEADERS[section] if orientation == Qt.Horizontal else str(section + 1)

    def get_item(self, row: int) -> EvaluationCategory | None:
        if row < 0 or row >= len(self._items):
            return None
        return self._items[row]
