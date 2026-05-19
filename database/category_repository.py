from __future__ import annotations

from models.entities import EvaluationCategory
from services.grade_service import GradeCalculator

from .connection import get_connection


class CategoryRepository:
    def list_by_group(self, group_id: int, period_number: int | None = None) -> list[EvaluationCategory]:
        query = """
            SELECT
                c.id,
                c.group_id,
                c.name,
                c.weight_percent,
                c.period_number,
                c.category_mode,
                c.deduction_base_score,
                c.is_active,
                c.sort_order,
                c.is_custom,
                COUNT(a.id) AS activity_count
            FROM evaluation_categories c
            LEFT JOIN activities a ON a.category_id = c.id
            WHERE c.group_id = ?
            {period_filter}
            GROUP BY c.id
            ORDER BY c.sort_order ASC, c.id ASC
        """
        period_filter = ""
        params: list[int] = [group_id]
        if period_number is not None:
            period_filter = "AND c.period_number = ?"
            params.append(period_number)
        with get_connection() as connection:
            rows = connection.execute(query.format(period_filter=period_filter), tuple(params)).fetchall()

        categories = []
        for row in rows:
            item = EvaluationCategory(
                id=row["id"],
                group_id=row["group_id"],
                name=row["name"],
                weight_percent=row["weight_percent"],
                period_number=row["period_number"] or 1,
                category_mode=row["category_mode"] or "normal",
                deduction_base_score=GradeCalculator.normalize_legacy_threshold(
                    row["deduction_base_score"] or 100.0
                ),
                is_active=bool(row["is_active"]),
                sort_order=row["sort_order"],
                is_custom=bool(row["is_custom"]),
                activity_count=row["activity_count"],
            )
            categories.append(item)
        return categories

    def create(self, category: EvaluationCategory) -> EvaluationCategory:
        query = """
            INSERT INTO evaluation_categories
            (group_id, name, weight_percent, period_number, category_mode, deduction_base_score, is_active, sort_order, is_custom)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with get_connection() as connection:
            cursor = connection.execute(
                query,
                (
                    category.group_id,
                    category.name.strip(),
                    category.weight_percent,
                    category.period_number,
                    category.category_mode,
                    category.deduction_base_score,
                    int(category.is_active),
                    category.sort_order,
                    int(category.is_custom),
                ),
            )
            category_id = cursor.lastrowid

        return EvaluationCategory(
            id=category_id,
            group_id=category.group_id,
            name=category.name.strip(),
            weight_percent=category.weight_percent,
            period_number=category.period_number,
            category_mode=category.category_mode,
            deduction_base_score=category.deduction_base_score,
            is_active=category.is_active,
            sort_order=category.sort_order,
            is_custom=category.is_custom,
        )

    def update(self, category: EvaluationCategory) -> None:
        query = """
            UPDATE evaluation_categories
            SET
                name = ?,
                weight_percent = ?,
                period_number = ?,
                category_mode = ?,
                deduction_base_score = ?,
                is_active = ?,
                sort_order = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        with get_connection() as connection:
            connection.execute(
                query,
                (
                    category.name.strip(),
                    category.weight_percent,
                    category.period_number,
                    category.category_mode,
                    category.deduction_base_score,
                    int(category.is_active),
                    category.sort_order,
                    category.id,
                ),
            )

    def delete(self, category_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM evaluation_categories WHERE id = ?", (category_id,))
