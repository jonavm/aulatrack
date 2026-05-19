from __future__ import annotations

from models.entities import StudentCategoryDeductionEntry

from .connection import get_connection


class StudentCategoryDeductionRepository:
    def list_by_group(self, group_id: int, period_number: int | None = None) -> list[StudentCategoryDeductionEntry]:
        query = """
            SELECT
                d.id,
                d.category_id,
                d.student_id,
                d.points,
                d.note,
                d.created_at
            FROM student_category_deduction_entries d
            INNER JOIN evaluation_categories c ON c.id = d.category_id
            WHERE c.group_id = ?
            {period_filter}
            ORDER BY d.created_at DESC, d.id DESC
        """
        period_filter = ""
        params: list[int] = [group_id]
        if period_number is not None:
            period_filter = "AND c.period_number = ?"
            params.append(period_number)
        with get_connection() as connection:
            rows = connection.execute(query.format(period_filter=period_filter), tuple(params)).fetchall()
        return [
            StudentCategoryDeductionEntry(
                id=row["id"],
                category_id=row["category_id"],
                student_id=row["student_id"],
                points=row["points"] or 0.0,
                note=row["note"] or "",
                created_at=row["created_at"] or "",
            )
            for row in rows
        ]

    def add_entry(self, category_id: int, student_id: int, points: float, note: str = "") -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO student_category_deduction_entries (category_id, student_id, points, note, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (category_id, student_id, points, note),
            )
