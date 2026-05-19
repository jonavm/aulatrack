from __future__ import annotations

from database.activity_repository import ActivityRepository
from models.entities import Activity


class ActivityService:
    def __init__(self, repository: ActivityRepository | None = None) -> None:
        self.repository = repository or ActivityRepository()

    def list_by_group(self, group_id: int, period_number: int | None = None) -> list[Activity]:
        return self.repository.list_by_group(group_id, period_number)

    def create(
        self,
        category_id: int,
        name: str,
        max_score: float,
        due_date: str | None,
        applies_to_risk: bool,
        sort_order: int,
        category_name: str = "",
    ) -> Activity:
        self._validate(name, max_score)
        return self.repository.create(
            Activity(
                id=None,
                category_id=category_id,
                name=name,
                max_score=max_score,
                due_date=due_date or None,
                applies_to_risk=applies_to_risk,
                sort_order=sort_order,
                category_name=category_name,
            )
        )

    def update(
        self,
        activity_id: int,
        category_id: int,
        name: str,
        max_score: float,
        due_date: str | None,
        applies_to_risk: bool,
        sort_order: int,
        category_name: str = "",
    ) -> None:
        self._validate(name, max_score)
        self.repository.update(
            Activity(
                id=activity_id,
                category_id=category_id,
                name=name,
                max_score=max_score,
                due_date=due_date or None,
                applies_to_risk=applies_to_risk,
                sort_order=sort_order,
                category_name=category_name,
            )
        )

    def delete(self, activity_id: int) -> None:
        self.repository.delete(activity_id)

    @staticmethod
    def _validate(name: str, max_score: float) -> None:
        if not name.strip():
            raise ValueError("El nombre de la actividad es obligatorio.")
        if max_score <= 0:
            raise ValueError("La puntuacion maxima debe ser mayor que cero.")
