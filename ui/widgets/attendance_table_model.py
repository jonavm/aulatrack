from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from models.entities import AttendanceRecord, Student
from themes.theme import get_theme_tokens


class AttendanceTableModel(QAbstractTableModel):
    USER_ROLE_STATUS = 1002
    STATUS_LABELS = {
        "present": "Presente",
        "absent": "Falta",
        "late": "Retardo",
        "justified": "Justificada",
    }
    STATUS_COLORS = {
        "present": QColor("#1F8A5B"),
        "absent": QColor("#C05666"),
        "late": QColor("#B7791F"),
        "justified": QColor("#2563EB"),
    }

    @staticmethod
    def _status_color(status: str) -> QColor:
        tokens = get_theme_tokens()
        return {
            "present": QColor(tokens["success_text"]),
            "absent": QColor(tokens["danger"]),
            "late": QColor(tokens["warning_text"]),
            "justified": QColor(tokens["info_text"]),
        }.get(status, QColor(tokens["text"]))

    def __init__(self) -> None:
        super().__init__()
        self._students: list[Student] = []
        self._record_lookup: dict[int, AttendanceRecord] = {}
        self._session_id: int | None = None
        self._save_callback = None

    def set_snapshot(
        self,
        *,
        session_id: int | None,
        students: list[Student],
        records: list[AttendanceRecord],
        save_callback,
    ) -> None:
        self.beginResetModel()
        self._session_id = session_id
        self._students = students
        self._record_lookup = {record.student_id: record for record in records}
        self._save_callback = save_callback
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._students)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else 2

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        student = self._students[index.row()]
        record = self._record_lookup.get(student.id)
        status = record.status if record else "present"

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return student.roster_name
            return self.STATUS_LABELS[status]

        if role == self.USER_ROLE_STATUS and index.column() == 1:
            return status

        if role == Qt.ForegroundRole and index.column() == 1:
            return self._status_color(status)

        if role == Qt.TextAlignmentRole and index.column() == 1:
            return Qt.AlignCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ["Alumno", "Asistencia"][section]
        return str(section + 1)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 1:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid() or index.column() != 1:
            return False
        student = self._students[index.row()]
        status = str(value)
        self._save_callback(self._session_id, student.id, status)
        self._record_lookup[student.id] = AttendanceRecord(
            id=None,
            session_id=self._session_id,
            student_id=student.id,
            status=status,
            comment="",
        )
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.ForegroundRole, self.USER_ROLE_STATUS])
        return True
