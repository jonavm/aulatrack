from __future__ import annotations

from database.student_category_deduction_repository import StudentCategoryDeductionRepository
from models.entities import StudentCategoryDeductionEntry


class StudentCategoryDeductionService:
    def __init__(self, repository: StudentCategoryDeductionRepository | None = None) -> None:
        self.repository = repository or StudentCategoryDeductionRepository()

    def list_by_group(self, group_id: int, period_number: int | None = None) -> list[StudentCategoryDeductionEntry]:
        return self.repository.list_by_group(group_id, period_number)

    def add_entry(self, category_id: int, student_id: int, points: float, note: str) -> None:
        if points < 0:
            raise ValueError("El descuento no puede ser negativo.")
        if not note.strip():
            raise ValueError("Escribe el motivo del descuento.")
        self.repository.add_entry(category_id, student_id, round(points, 2), note.strip())
