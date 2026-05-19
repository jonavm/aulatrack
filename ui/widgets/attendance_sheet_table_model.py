from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from models.entities import AttendanceSession, Student
from themes.theme import get_theme_tokens


class AttendanceSheetTableModel(QAbstractTableModel):
    STATUS_TO_LABEL = {
        "present": "A",
        "absent": "F",
        "late": "R",
        "justified": "J",
    }
    INPUT_TO_STATUS = {
        "A": "present",
        "P": "present",
        "F": "absent",
        "R": "late",
        "J": "justified",
    }
    STATUS_COLORS = {
        "present": QColor("#1F8A5B"),
        "absent": QColor("#C05666"),
        "late": QColor("#B7791F"),
        "justified": QColor("#2563EB"),
    }
    STATUS_BACKGROUNDS = {
        "present": QColor("#EAF7F0"),
        "absent": QColor("#FCEBED"),
        "late": QColor("#FFF4DB"),
        "justified": QColor("#E7F0FF"),
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

    @staticmethod
    def _status_background(status: str) -> QColor:
        tokens = get_theme_tokens()
        return {
            "present": QColor(tokens["success_soft"]),
            "absent": QColor(tokens["danger_soft_alt"]),
            "late": QColor(tokens["warning_soft"]),
            "justified": QColor(tokens["info_soft"]),
        }.get(status, QColor(tokens["panel_alt"]))

    def __init__(self) -> None:
        super().__init__()
        self._students: list[Student] = []
        self._sessions: list[AttendanceSession] = []
        self._records: dict[tuple[int, int], str] = {}
        self._save_callback = None
        self._active_session_date: str | None = None

    def set_sheet(
        self,
        *,
        students: list[Student],
        sessions: list[AttendanceSession],
        records: dict[tuple[int, int], str],
        save_callback,
    ) -> None:
        self.beginResetModel()
        self._students = students
        self._sessions = sessions
        self._records = records
        self._save_callback = save_callback
        self.endResetModel()

    def set_active_session_date(self, session_date: str | None) -> None:
        self._active_session_date = session_date
        if self.columnCount() > 1 and self.rowCount() > 0:
            top_left = self.index(0, 1)
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole])

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._students)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else 1 + len(self._sessions)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        student = self._students[index.row()]
        if index.column() == 0:
            if role == Qt.DisplayRole:
                return student.roster_name
            return None

        session = self._sessions[index.column() - 1]
        status = self._records.get((student.id, session.id), "present")

        if role == Qt.DisplayRole:
            return self.STATUS_TO_LABEL.get(status, "A")

        if role == Qt.EditRole:
            return self.STATUS_TO_LABEL.get(status, "A")

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role == Qt.ForegroundRole:
            return self._status_color(status)

        if role == Qt.BackgroundRole:
            background = self._status_background(status)
            if self._active_session_date and session.session_date == self._active_session_date:
                return background.darker(104) if background else QColor(get_theme_tokens()["selection_bg"])
            return background

        if role == Qt.ToolTipRole:
            return {
                "present": "Asistencia",
                "absent": "Falta",
                "late": "Retardo",
                "justified": "Justificada",
            }.get(status, "Asistencia")

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if section == 0:
                if role == Qt.DisplayRole:
                    return "Alumno"
                return None
            session_date = self._sessions[section - 1].session_date
            if role == Qt.DisplayRole:
                return session_date
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            if role == Qt.BackgroundRole and session_date == self._active_session_date:
                return QColor(get_theme_tokens()["accent"])
            if role == Qt.ForegroundRole and session_date == self._active_session_date:
                return QColor(get_theme_tokens()["sidebar_text"])
            return None
        if role == Qt.DisplayRole:
            return str(section + 1)
        return None

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() >= 1:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid() or index.column() == 0:
            return False

        text = str(value).strip().upper()
        if text not in self.INPUT_TO_STATUS:
            return False

        student = self._students[index.row()]
        session = self._sessions[index.column() - 1]
        status = self.INPUT_TO_STATUS[text]
        self._save_callback(session.id, student.id, status)
        self._records[(student.id, session.id)] = status
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.ForegroundRole, Qt.BackgroundRole])
        return True

    def apply_text_value(self, index: QModelIndex, raw_value: str) -> bool:
        return self.setData(index, raw_value, Qt.EditRole)

    def session_column_for_date(self, session_date: str) -> int | None:
        for offset, session in enumerate(self._sessions, start=1):
            if session.session_date == session_date:
                return offset
        return None
