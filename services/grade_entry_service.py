from __future__ import annotations

from database.grade_repository import GradeRepository
from models.entities import GradeEntry


class GradeEntryService:
    def __init__(self, repository: GradeRepository | None = None) -> None:
        self.repository = repository or GradeRepository()

    def list_by_group(self, group_id: int, period_number: int | None = None) -> list[GradeEntry]:
        return self.repository.list_by_group(group_id, period_number)

    def save_entry(
        self,
        activity_id: int,
        student_id: int,
        score: float | None,
        status: str,
        comment: str = "",
    ) -> None:
        if status not in {"graded", "pending", "missing"}:
            raise ValueError("Estado invalido.")
        if status == "graded" and score is None:
            raise ValueError("Una calificacion guardada necesita puntuacion.")
        if status != "graded":
            score = None
        self.repository.save_entry(activity_id, student_id, score, status, comment)
