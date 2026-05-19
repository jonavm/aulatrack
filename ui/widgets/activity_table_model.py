from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.entities import Activity


class ActivityTableModel(QAbstractTableModel):
    NORMAL_HEADERS = ["Actividad", "Criterio", "Max", "Riesgo", "Fecha"]
    DEDUCTION_HEADERS = ["Criterio", "Criterio base", "Max desc.", "Riesgo", "Fecha"]

    def __init__(self) -> None:
        super().__init__()
        self._items: list[Activity] = []
        self._deduction_mode = False

    def set_items(self, items: list[Activity]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def set_deduction_mode(self, enabled: bool) -> None:
        if self._deduction_mode == enabled:
            return
        self._deduction_mode = enabled
        self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount() - 1)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.NORMAL_HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str | None:
        if not index.isValid():
            return None
        item = self._items[index.row()]
        values = [
            item.name,
            item.category_name or "Sin criterio",
            f"{item.max_score:.1f}",
            "Si" if item.applies_to_risk else "No",
            item.due_date or "-",
        ]
        if role == Qt.DisplayRole:
            return values[index.column()]
        if role == Qt.UserRole:
            return item
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        headers = self.DEDUCTION_HEADERS if self._deduction_mode else self.NORMAL_HEADERS
        return headers[section] if orientation == Qt.Horizontal else str(section + 1)

    def get_item(self, row: int) -> Activity | None:
        if row < 0 or row >= len(self._items):
            return None
        return self._items[row]
