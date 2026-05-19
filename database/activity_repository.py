from __future__ import annotations

from models.entities import Activity

from .connection import get_connection


class ActivityRepository:
    def list_by_group(self, group_id: int, period_number: int | None = None) -> list[Activity]:
        query = """
            SELECT
                a.id,
                a.category_id,
                a.name,
                a.max_score,
                a.due_date,
                a.applies_to_risk,
                a.sort_order,
                c.name AS category_name
            FROM activities a
            INNER JOIN evaluation_categories c ON c.id = a.category_id
            WHERE c.group_id = ?
            {period_filter}
            ORDER BY c.sort_order ASC, a.sort_order ASC, a.id ASC
        """
        period_filter = ""
        params: list[int] = [group_id]
        if period_number is not None:
            period_filter = "AND c.period_number = ?"
            params.append(period_number)
        with get_connection() as connection:
            rows = connection.execute(query.format(period_filter=period_filter), tuple(params)).fetchall()

        activities = []
        for row in rows:
            item = Activity(
                id=row["id"],
                category_id=row["category_id"],
                name=row["name"],
                max_score=row["max_score"],
                due_date=row["due_date"],
                applies_to_risk=bool(row["applies_to_risk"]),
                sort_order=row["sort_order"],
                category_name=row["category_name"],
            )
            activities.append(item)
        return activities

    def create(self, activity: Activity) -> Activity:
        query = """
            INSERT INTO activities
            (category_id, name, max_score, due_date, applies_to_risk, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with get_connection() as connection:
            cursor = connection.execute(
                query,
                (
                    activity.category_id,
                    activity.name.strip(),
                    activity.max_score,
                    activity.due_date,
                    int(activity.applies_to_risk),
                    activity.sort_order,
                ),
            )
            activity_id = cursor.lastrowid

        return Activity(
            id=activity_id,
            category_id=activity.category_id,
            name=activity.name.strip(),
            max_score=activity.max_score,
            due_date=activity.due_date,
            applies_to_risk=activity.applies_to_risk,
            sort_order=activity.sort_order,
            category_name=activity.category_name,
        )

    def update(self, activity: Activity) -> None:
        query = """
            UPDATE activities
            SET
                name = ?,
                max_score = ?,
                due_date = ?,
                applies_to_risk = ?,
                sort_order = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        with get_connection() as connection:
            connection.execute(
                query,
                (
                    activity.name.strip(),
                    activity.max_score,
                    activity.due_date,
                    int(activity.applies_to_risk),
                    activity.sort_order,
                    activity.id,
                ),
            )

    def delete(self, activity_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
