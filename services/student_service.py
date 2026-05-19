from __future__ import annotations

from database.student_repository import StudentRepository
from models.entities import Student
from services.student_import_service import ImportPreview, StudentImportService


class StudentService:
    def __init__(self, repository: StudentRepository | None = None) -> None:
        self.repository = repository or StudentRepository()
        self.import_service = StudentImportService()

    def list_students_by_group(self, group_id: int) -> list[Student]:
        return self.repository.list_students_by_group(group_id)

    def create_student(
        self,
        group_id: int,
        first_name: str,
        last_name: str,
        student_code: str,
        is_active: bool,
        notes: str,
    ) -> Student:
        self._validate_name_fields(first_name, last_name)
        return self.repository.create_student(
            Student(
                id=None,
                group_id=group_id,
                first_name=first_name,
                last_name=last_name,
                student_code=student_code,
                is_active=is_active,
                notes=notes,
            )
        )

    def update_student(
        self,
        student_id: int,
        group_id: int,
        first_name: str,
        last_name: str,
        student_code: str,
        is_active: bool,
        notes: str,
    ) -> None:
        self._validate_name_fields(first_name, last_name)
        self.repository.update_student(
            Student(
                id=student_id,
                group_id=group_id,
                first_name=first_name,
                last_name=last_name,
                student_code=student_code,
                is_active=is_active,
                notes=notes,
            )
        )

    def delete_student(self, student_id: int) -> None:
        self.repository.delete_student(student_id)

    def update_notes(self, student_id: int, notes: str) -> None:
        self.repository.update_notes(student_id, notes)

    def preview_import(self, file_path: str) -> ImportPreview:
        return self.import_service.parse_file(file_path)

    def import_students(self, group_id: int, preview: ImportPreview) -> dict:
        existing = self.list_students_by_group(group_id)
        existing_keys = {
            (student.first_name.strip().lower(), student.last_name.strip().lower())
            for student in existing
        }

        created = 0
        skipped = 0
        for item in preview.students:
            key = (item.first_name.strip().lower(), item.last_name.strip().lower())
            if key in existing_keys:
                skipped += 1
                continue
            self.repository.create_student(
                Student(
                    id=None,
                    group_id=group_id,
                    first_name=item.first_name,
                    last_name=item.last_name,
                    student_code=item.student_code,
                    is_active=True,
                    notes="",
                )
            )
            existing_keys.add(key)
            created += 1

        return {
            "created": created,
            "skipped": skipped,
            "warnings": preview.warnings,
            "detected_mode": preview.detected_mode,
            "source_name": preview.source_name,
        }

    @staticmethod
    def _validate_name_fields(first_name: str, last_name: str) -> None:
        if not first_name.strip():
            raise ValueError("El nombre del alumno es obligatorio.")
        if not last_name.strip():
            raise ValueError("Los apellidos del alumno son obligatorios.")
