from __future__ import annotations

from database.adjustment_repository import AdjustmentRepository
from models.entities import StudentAdjustment


class AdjustmentService:
    def __init__(self, repository: AdjustmentRepository | None = None) -> None:
        self.repository = repository or AdjustmentRepository()

    def list_by_group(self, group_id: int) -> list[StudentAdjustment]:
        return self.repository.list_by_group(group_id)

    def save_adjustment(self, group_id: int, student_id: int, points: float) -> None:
        if points < -10 or points > 10:
            raise ValueError("El ajuste debe estar entre -10 y 10 puntos.")
        self.repository.save_adjustment(group_id, student_id, round(points, 2))
