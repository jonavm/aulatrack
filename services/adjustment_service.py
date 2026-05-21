from __future__ import annotations

from database.adjustment_repository import AdjustmentRepository
from models.entities import StudentAdjustment


class AdjustmentService:
    def __init__(self, repository: AdjustmentRepository | None = None) -> None:
        self.repository = repository or AdjustmentRepository()

    def list_by_group(self, group_id: int) -> list[StudentAdjustment]:
        return self.repository.list_by_group(group_id)

    def save_adjustment(self, group_id: int, student_id: int, points: float, note: str = "") -> None:
        if points < 0 or points > 100:
            raise ValueError("El total de puntos extra no puede ser negativo.")
        self.repository.save_adjustment(group_id, student_id, round(points, 2), note.strip())
