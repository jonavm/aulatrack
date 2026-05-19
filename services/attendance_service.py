from __future__ import annotations

from collections import Counter

from database.attendance_repository import AttendanceRepository
from models.entities import AttendanceRecord, AttendanceSession, Student
from services.student_service import StudentService


class AttendanceService:
    VALID_STATUSES = ("present", "absent", "late", "justified")

    def __init__(self, repository: AttendanceRepository | None = None) -> None:
        self.repository = repository or AttendanceRepository()
        self.student_service = StudentService()

    def get_daily_attendance(self, group_id: int, session_date: str) -> dict:
        session = self.repository.get_or_create_session(group_id, session_date)
        students = self.student_service.list_students_by_group(group_id)
        records = self.repository.list_records(session.id)
        return {
            "session": session,
            "students": students,
            "records": records,
        }

    def list_sessions_by_group(self, group_id: int) -> list[AttendanceSession]:
        return self.repository.list_sessions_by_group(group_id)

    def get_attendance_sheet(self, group_id: int) -> dict:
        students = self.student_service.list_students_by_group(group_id)
        sessions = self.repository.list_sessions_by_group(group_id)
        raw_records = self.repository.list_group_records(group_id)
        records = {
            (item["student_id"], item["session_id"]): item["status"]
            for item in raw_records
        }
        return {
            "students": students,
            "sessions": sessions,
            "records": records,
        }

    def list_session_summaries_by_group(self, group_id: int) -> list[dict]:
        return self.repository.list_session_summaries_by_group(group_id)

    def get_attendance_by_session(self, session_id: int) -> dict | None:
        session = self.repository.get_session(session_id)
        if session is None:
            return None
        students = self.student_service.list_students_by_group(session.group_id)
        records = self.repository.list_records(session.id)
        return {
            "session": session,
            "students": students,
            "records": records,
        }

    def save_status(self, session_id: int, student_id: int, status: str) -> None:
        if status not in self.VALID_STATUSES:
            raise ValueError("Estado de asistencia invalido.")
        self.repository.save_record(session_id, student_id, status)

    @staticmethod
    def build_summary(students: list[Student], records: list[AttendanceRecord]) -> dict:
        counts = Counter(record.status for record in records)
        total = len(students)
        counted = sum(counts.values())
        if counted < total:
            counts["present"] += total - counted
        return {
            "total": total,
            "present": counts.get("present", 0),
            "absent": counts.get("absent", 0),
            "late": counts.get("late", 0),
            "justified": counts.get("justified", 0),
        }
