from __future__ import annotations

from models.entities import Student

from .connection import get_connection


class StudentRepository:
    def list_students_by_group(self, group_id: int) -> list[Student]:
        query = """
            SELECT
                id,
                group_id,
                first_name,
                last_name,
                student_code,
                is_active,
                notes
            FROM students
            WHERE group_id = ?
            ORDER BY
                TRIM(last_name) COLLATE NOCASE,
                TRIM(first_name) COLLATE NOCASE,
                id ASC
        """
        with get_connection() as connection:
            rows = connection.execute(query, (group_id,)).fetchall()

        return [
            Student(
                id=row["id"],
                group_id=row["group_id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                student_code=row["student_code"] or "",
                is_active=bool(row["is_active"]),
                notes=row["notes"] or "",
            )
            for row in rows
        ]

    def create_student(self, student: Student) -> Student:
        query = """
            INSERT INTO students (group_id, first_name, last_name, student_code, is_active, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with get_connection() as connection:
            cursor = connection.execute(
                query,
                (
                    student.group_id,
                    student.first_name.strip(),
                    student.last_name.strip(),
                    student.student_code.strip(),
                    int(student.is_active),
                    student.notes.strip(),
                ),
            )
            student_id = cursor.lastrowid

        return Student(
            id=student_id,
            group_id=student.group_id,
            first_name=student.first_name.strip(),
            last_name=student.last_name.strip(),
            student_code=student.student_code.strip(),
            is_active=student.is_active,
            notes=student.notes.strip(),
        )

    def update_student(self, student: Student) -> None:
        query = """
            UPDATE students
            SET
                first_name = ?,
                last_name = ?,
                student_code = ?,
                is_active = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        with get_connection() as connection:
            connection.execute(
                query,
                (
                    student.first_name.strip(),
                    student.last_name.strip(),
                    student.student_code.strip(),
                    int(student.is_active),
                    student.notes.strip(),
                    student.id,
                ),
            )

    def update_notes(self, student_id: int, notes: str) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE students
                SET notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (notes.strip(), student_id),
            )

    def delete_student(self, student_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
