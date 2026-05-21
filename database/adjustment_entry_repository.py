from __future__ import annotations

from models.entities import StudentAdjustment, StudentAdjustmentEntry

from .connection import get_connection


class AdjustmentEntryRepository:
    def list_by_group(self, group_id: int) -> list[StudentAdjustmentEntry]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, group_id, student_id, points, note, created_at
                FROM student_adjustment_entries
                WHERE group_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (group_id,),
            ).fetchall()
        return [
            StudentAdjustmentEntry(
                id=row["id"],
                group_id=row["group_id"],
                student_id=row["student_id"],
                points=row["points"] or 0.0,
                note=row["note"] or "",
                created_at=row["created_at"] or "",
            )
            for row in rows
        ]

    def add_entry(self, group_id: int, student_id: int, points: float, note: str) -> StudentAdjustment:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO student_adjustment_entries (group_id, student_id, points, note, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (group_id, student_id, points, note),
            )
            total_row = connection.execute(
                """
                SELECT ROUND(COALESCE(SUM(points), 0), 2) AS total
                FROM student_adjustment_entries
                WHERE group_id = ? AND student_id = ?
                """,
                (group_id, student_id),
            ).fetchone()
            total_points = total_row["total"] or 0.0
            connection.execute(
                """
                INSERT INTO student_adjustments (group_id, student_id, points, note, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(group_id, student_id) DO UPDATE SET
                    points = excluded.points,
                    note = excluded.note,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (group_id, student_id, total_points, note),
            )
        return StudentAdjustment(
            id=None,
            group_id=group_id,
            student_id=student_id,
            points=round(total_points, 2),
            note=note,
        )
