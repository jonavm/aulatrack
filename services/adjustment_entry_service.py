from __future__ import annotations

from database.adjustment_entry_repository import AdjustmentEntryRepository
from models.entities import StudentAdjustment, StudentAdjustmentEntry


class AdjustmentEntryService:
    def __init__(self, repository: AdjustmentEntryRepository | None = None) -> None:
        self.repository = repository or AdjustmentEntryRepository()

    def list_by_group(self, group_id: int) -> list[StudentAdjustmentEntry]:
        return self.repository.list_by_group(group_id)

    def add_entry(self, group_id: int, student_id: int, points: float, note: str) -> StudentAdjustment:
        if points <= 0:
            raise ValueError("Los puntos extra deben ser mayores que cero.")
        if points > 10:
            raise ValueError("Los puntos extra no pueden superar 10 puntos por registro.")
        if not note.strip():
            raise ValueError("Escribe el motivo de los puntos extra.")
        return self.repository.add_entry(group_id, student_id, round(points, 2), note.strip())
