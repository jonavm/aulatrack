from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.entities import Student


class StudentsTableModel(QAbstractTableModel):
    HEADERS = ["Alumno", "Estado", "Notas"]

    def __init__(self) -> None:
        super().__init__()
        self._students: list[Student] = []

    def set_students(self, students: list[Student]) -> None:
        self.beginResetModel()
        self._students = students
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._students)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str | None:
        if not index.isValid():
            return None

        student = self._students[index.row()]
        values = [
            student.roster_name,
            "Activo" if student.is_active else "Inactivo",
            student.notes or "Sin notas",
        ]

        if role == Qt.DisplayRole:
            return values[index.column()]

        if role == Qt.UserRole:
            return student

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> str | None:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def get_student(self, row: int) -> Student | None:
        if row < 0 or row >= len(self._students):
            return None
        return self._students[row]
