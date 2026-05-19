from __future__ import annotations

from models.entities import School

from .connection import get_connection


class SchoolRepository:
    def list_schools(self) -> list[School]:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT id, name FROM schools ORDER BY name COLLATE NOCASE ASC"
            ).fetchall()
        return [School(id=row["id"], name=row["name"]) for row in rows]

    def find_by_name(self, name: str) -> School | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, name
                FROM schools
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
                LIMIT 1
                """,
                (name.strip(),),
            ).fetchone()
        if row is None:
            return None
        return School(id=row["id"], name=row["name"])

    def create_school(self, name: str) -> School:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO schools (name) VALUES (?)",
                (name.strip(),),
            )
            school_id = cursor.lastrowid
        return School(id=school_id, name=name.strip())

    def update_school(self, school_id: int, name: str) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE schools
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name.strip(), school_id),
            )

    def delete_school(self, school_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM schools WHERE id = ?", (school_id,))
