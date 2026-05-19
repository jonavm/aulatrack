from __future__ import annotations

from models.entities import Group
from services.grade_service import GradeCalculator

from .connection import get_connection


class GroupRepository:
    def list_groups(self) -> list[Group]:
        query = """
            SELECT
                g.id,
                g.name,
                g.school_id,
                sc.name AS school_name,
                g.subject_name,
                g.school_year,
                g.grade_level,
                g.group_section,
                g.passing_grade,
                COUNT(s.id) AS student_count
            FROM groups g
            LEFT JOIN schools sc ON sc.id = g.school_id
            LEFT JOIN students s ON s.group_id = g.id AND s.is_active = 1
            GROUP BY g.id
            ORDER BY g.created_at DESC, g.id DESC
        """
        with get_connection() as connection:
            rows = connection.execute(query).fetchall()

        groups = []
        for row in rows:
            group = Group(
                id=row["id"],
                name=row["name"],
                school_id=row["school_id"],
                school_name=row["school_name"] or "",
                subject_name=row["subject_name"] or "",
                school_year=row["school_year"] or "",
                grade_level=row["grade_level"] or "",
                group_section=row["group_section"] or "",
                passing_grade=GradeCalculator.normalize_legacy_threshold(row["passing_grade"]),
            )
            group.student_count = row["student_count"]
            groups.append(group)
        return groups

    def create_group(self, group: Group) -> Group:
        query = """
            INSERT INTO groups (school_id, name, school_year, subject_name, grade_level, group_section, passing_grade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with get_connection() as connection:
            cursor = connection.execute(
                query,
                (
                    group.school_id,
                    group.name.strip(),
                    group.school_year.strip(),
                    group.subject_name.strip(),
                    group.grade_level.strip(),
                    group.group_section.strip(),
                    group.passing_grade,
                ),
            )
            group_id = cursor.lastrowid

        return Group(
            id=group_id,
            name=group.name.strip(),
            school_id=group.school_id,
            school_name=group.school_name,
            school_year=group.school_year.strip(),
            subject_name=group.subject_name.strip(),
            grade_level=group.grade_level.strip(),
            group_section=group.group_section.strip(),
            passing_grade=group.passing_grade,
        )

    def find_matching_group(
        self,
        *,
        school_id: int | None,
        grade_level: str,
        group_section: str,
        school_year: str = "",
    ) -> Group | None:
        query = """
            SELECT
                g.id,
                g.name,
                g.school_id,
                sc.name AS school_name,
                g.subject_name,
                g.school_year,
                g.grade_level,
                g.group_section,
                g.passing_grade
            FROM groups g
            LEFT JOIN schools sc ON sc.id = g.school_id
            WHERE LOWER(TRIM(COALESCE(g.grade_level, ''))) = LOWER(TRIM(?))
              AND LOWER(TRIM(COALESCE(g.group_section, ''))) = LOWER(TRIM(?))
              AND (
                    (? IS NULL AND g.school_id IS NULL)
                    OR g.school_id = ?
                  )
              AND (
                    ? = ''
                    OR LOWER(TRIM(COALESCE(g.school_year, ''))) = LOWER(TRIM(?))
                  )
            ORDER BY g.id DESC
            LIMIT 1
        """
        with get_connection() as connection:
            row = connection.execute(
                query,
                (
                    grade_level.strip(),
                    group_section.strip(),
                    school_id,
                    school_id,
                    school_year.strip(),
                    school_year.strip(),
                ),
            ).fetchone()

        if row is None:
            return None

        return Group(
            id=row["id"],
            name=row["name"],
            school_id=row["school_id"],
            school_name=row["school_name"] or "",
            subject_name=row["subject_name"] or "",
            school_year=row["school_year"] or "",
            grade_level=row["grade_level"] or "",
            group_section=row["group_section"] or "",
            passing_grade=GradeCalculator.normalize_legacy_threshold(row["passing_grade"]),
        )

    def update_group(self, group: Group) -> None:
        query = """
            UPDATE groups
            SET
                name = ?,
                school_year = ?,
                subject_name = ?,
                grade_level = ?,
                group_section = ?,
                passing_grade = ?,
                school_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        with get_connection() as connection:
            connection.execute(
                query,
                (
                    group.name.strip(),
                    group.school_year.strip(),
                    group.subject_name.strip(),
                    group.grade_level.strip(),
                    group.group_section.strip(),
                    group.passing_grade,
                    group.school_id,
                    group.id,
                ),
            )

    def delete_group(self, group_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM groups WHERE id = ?", (group_id,))
