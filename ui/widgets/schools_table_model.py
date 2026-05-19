from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.entities import School


class SchoolsTableModel(QAbstractTableModel):
    HEADERS = ["Escuela"]

    def __init__(self) -> None:
        super().__init__()
        self._schools: list[School] = []

    def set_schools(self, schools: list[School]) -> None:
        self.beginResetModel()
        self._schools = schools
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._schools)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self._schools[index.row()].name
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        return self.HEADERS[section] if orientation == Qt.Horizontal else str(section + 1)

    def get_school(self, row: int) -> School | None:
        if row < 0 or row >= len(self._schools):
            return None
        return self._schools[row]
