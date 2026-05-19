from __future__ import annotations

from models.entities import AttendanceRecord, AttendanceSession

from .connection import get_connection


class AttendanceRepository:
    def list_group_records(self, group_id: int) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    r.id,
                    r.session_id,
                    s.session_date,
                    r.student_id,
                    r.status,
                    r.comment
                FROM attendance_records r
                INNER JOIN attendance_sessions s ON s.id = r.session_id
                WHERE s.group_id = ?
                ORDER BY s.session_date ASC, r.student_id ASC
                """,
                (group_id,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "session_id": row["session_id"],
                "session_date": row["session_date"],
                "student_id": row["student_id"],
                "status": row["status"],
                "comment": row["comment"] or "",
            }
            for row in rows
        ]

    def list_session_summaries_by_group(self, group_id: int) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    s.id,
                    s.group_id,
                    s.session_date,
                    s.note,
                    COALESCE(student_totals.total_students, 0) AS total_students,
                    COALESCE(SUM(CASE WHEN r.status = 'absent' THEN 1 ELSE 0 END), 0) AS absent_count,
                    COALESCE(SUM(CASE WHEN r.status = 'late' THEN 1 ELSE 0 END), 0) AS late_count,
                    COALESCE(SUM(CASE WHEN r.status = 'justified' THEN 1 ELSE 0 END), 0) AS justified_count,
                    COALESCE(COUNT(r.id), 0) AS marked_count
                FROM attendance_sessions s
                LEFT JOIN attendance_records r ON r.session_id = s.id
                LEFT JOIN (
                    SELECT group_id, COUNT(*) AS total_students
                    FROM students
                    WHERE is_active = 1
                    GROUP BY group_id
                ) AS student_totals ON student_totals.group_id = s.group_id
                WHERE s.group_id = ?
                GROUP BY s.id, s.group_id, s.session_date, s.note, student_totals.total_students
                ORDER BY s.session_date DESC, s.id DESC
                """,
                (group_id,),
            ).fetchall()

        summaries: list[dict] = []
        for row in rows:
            total = row["total_students"]
            absent = row["absent_count"]
            late = row["late_count"]
            justified = row["justified_count"]
            marked = row["marked_count"]
            present = max(0, total - absent - late - justified)
            summaries.append(
                {
                    "id": row["id"],
                    "group_id": row["group_id"],
                    "session_date": row["session_date"],
                    "note": row["note"] or "",
                    "total": total,
                    "present": present,
                    "absent": absent,
                    "late": late,
                    "justified": justified,
                    "marked": marked,
                }
            )
        return summaries

    def list_sessions_by_group(self, group_id: int) -> list[AttendanceSession]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, group_id, session_date, note
                FROM attendance_sessions
                WHERE group_id = ?
                ORDER BY session_date ASC, id ASC
                """,
                (group_id,),
            ).fetchall()
        return [
            AttendanceSession(
                id=row["id"],
                group_id=row["group_id"],
                session_date=row["session_date"],
                note=row["note"] or "",
            )
            for row in rows
        ]

    def get_session(self, session_id: int) -> AttendanceSession | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, group_id, session_date, note
                FROM attendance_sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return AttendanceSession(
            id=row["id"],
            group_id=row["group_id"],
            session_date=row["session_date"],
            note=row["note"] or "",
        )

    def get_or_create_session(self, group_id: int, session_date: str) -> AttendanceSession:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, group_id, session_date, note
                FROM attendance_sessions
                WHERE group_id = ? AND session_date = ?
                """,
                (group_id, session_date),
            ).fetchone()
            if row:
                return AttendanceSession(
                    id=row["id"],
                    group_id=row["group_id"],
                    session_date=row["session_date"],
                    note=row["note"] or "",
                )

            cursor = connection.execute(
                """
                INSERT INTO attendance_sessions (group_id, session_date)
                VALUES (?, ?)
                """,
                (group_id, session_date),
            )
            return AttendanceSession(
                id=cursor.lastrowid,
                group_id=group_id,
                session_date=session_date,
                note="",
            )

    def list_records(self, session_id: int) -> list[AttendanceRecord]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, session_id, student_id, status, comment
                FROM attendance_records
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchall()
        return [
            AttendanceRecord(
                id=row["id"],
                session_id=row["session_id"],
                student_id=row["student_id"],
                status=row["status"],
                comment=row["comment"] or "",
            )
            for row in rows
        ]

    def save_record(self, session_id: int, student_id: int, status: str, comment: str = "") -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO attendance_records (session_id, student_id, status, comment, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id, student_id) DO UPDATE SET
                    status = excluded.status,
                    comment = excluded.comment,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, student_id, status, comment),
            )
