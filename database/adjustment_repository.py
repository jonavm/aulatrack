from __future__ import annotations

from models.entities import StudentAdjustment

from .connection import get_connection


class AdjustmentRepository:
    def list_by_group(self, group_id: int) -> list[StudentAdjustment]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, group_id, student_id, points, note
                FROM student_adjustments
                WHERE group_id = ?
                """,
                (group_id,),
            ).fetchall()
        return [
            StudentAdjustment(
                id=row["id"],
                group_id=row["group_id"],
                student_id=row["student_id"],
                points=row["points"] or 0.0,
                note=row["note"] or "",
            )
            for row in rows
        ]

    def save_adjustment(self, group_id: int, student_id: int, points: float, note: str = "") -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO student_adjustments (group_id, student_id, points, note, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(group_id, student_id) DO UPDATE SET
                    points = excluded.points,
                    note = excluded.note,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (group_id, student_id, points, note),
            )

