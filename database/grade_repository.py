from __future__ import annotations

from models.entities import GradeEntry

from .connection import get_connection


class GradeRepository:
    def list_by_group(self, group_id: int, period_number: int | None = None) -> list[GradeEntry]:
        query = """
            SELECT
                g.id,
                g.activity_id,
                g.student_id,
                g.score,
                g.status,
                g.comment
            FROM grades g
            INNER JOIN activities a ON a.id = g.activity_id
            INNER JOIN evaluation_categories c ON c.id = a.category_id
            WHERE c.group_id = ?
            {period_filter}
        """
        period_filter = ""
        params: list[int] = [group_id]
        if period_number is not None:
            period_filter = "AND c.period_number = ?"
            params.append(period_number)
        with get_connection() as connection:
            rows = connection.execute(query.format(period_filter=period_filter), tuple(params)).fetchall()

        return [
            GradeEntry(
                id=row["id"],
                activity_id=row["activity_id"],
                student_id=row["student_id"],
                score=row["score"],
                status=row["status"],
                comment=row["comment"] or "",
            )
            for row in rows
        ]

    def save_entry(
        self,
        activity_id: int,
        student_id: int,
        score: float | None,
        status: str,
        comment: str = "",
    ) -> None:
        query = """
            INSERT INTO grades (activity_id, student_id, score, status, comment, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(activity_id, student_id) DO UPDATE SET
                score = excluded.score,
                status = excluded.status,
                comment = excluded.comment,
                updated_at = CURRENT_TIMESTAMP
        """
        with get_connection() as connection:
            connection.execute(query, (activity_id, student_id, score, status, comment))
