from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class AttendanceSessionsTableModel(QAbstractTableModel):
    HEADERS = ["Fecha", "Total", "Presentes", "Faltas", "Ret.", "Just."]

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[dict] = []

    def set_rows(self, rows: list[dict]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = self._rows[index.row()]
        values = [
            row["session_date"],
            str(row["total"]),
            str(row["present"]),
            str(row["absent"]),
            str(row["late"]),
            str(row["justified"]),
        ]

        if role == Qt.DisplayRole:
            return values[index.column()]

        if role == Qt.TextAlignmentRole and index.column() >= 1:
            return Qt.AlignCenter

        if role == Qt.UserRole:
            return row

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def get_row(self, row: int) -> dict | None:
        if row < 0 or row >= len(self._rows):
            return None
        return self._rows[row]
