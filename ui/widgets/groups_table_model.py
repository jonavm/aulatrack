from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.entities import Group


class GroupsTableModel(QAbstractTableModel):
    HEADERS = [
        "Grupo",
        "Escuela",
        "Grado",
        "Seccion",
        "Materia",
        "Ciclo",
        "Min. aprob.",
        "Alumnos",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._groups: list[Group] = []

    def set_groups(self, groups: list[Group]) -> None:
        self.beginResetModel()
        self._groups = groups
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._groups)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str | None:
        if not index.isValid():
            return None

        group = self._groups[index.row()]
        columns = [
            group.display_name,
            group.school_name or "Sin escuela",
            group.grade_level or "-",
            group.group_section or "-",
            group.subject_name or "Sin materia",
            group.school_year or "Sin ciclo",
            f"{group.passing_grade:.1f}",
            str(group.student_count),
        ]

        if role == Qt.DisplayRole:
            return columns[index.column()]

        if role == Qt.TextAlignmentRole and index.column() in (6, 7):
            return Qt.AlignCenter

        if role == Qt.UserRole:
            return group

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

    def get_group(self, row: int) -> Group | None:
        if row < 0 or row >= len(self._groups):
            return None
        return self._groups[row]
