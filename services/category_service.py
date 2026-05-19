from __future__ import annotations

from database.category_repository import CategoryRepository
from models.entities import EvaluationCategory


class CategoryService:
    def __init__(self, repository: CategoryRepository | None = None) -> None:
        self.repository = repository or CategoryRepository()

    def list_by_group(self, group_id: int, period_number: int | None = None) -> list[EvaluationCategory]:
        return self.repository.list_by_group(group_id, period_number)

    def create(
        self,
        group_id: int,
        name: str,
        weight_percent: float,
        period_number: int,
        category_mode: str,
        deduction_base_score: float,
        is_active: bool,
        sort_order: int,
        is_custom: bool = True,
    ) -> EvaluationCategory:
        self._validate(name, weight_percent, period_number, category_mode, deduction_base_score)
        return self.repository.create(
            EvaluationCategory(
                id=None,
                group_id=group_id,
                name=name,
                weight_percent=weight_percent,
                period_number=period_number,
                category_mode=category_mode,
                deduction_base_score=deduction_base_score,
                is_active=is_active,
                sort_order=sort_order,
                is_custom=is_custom,
            )
        )

    def update(
        self,
        category_id: int,
        group_id: int,
        name: str,
        weight_percent: float,
        period_number: int,
        category_mode: str,
        deduction_base_score: float,
        is_active: bool,
        sort_order: int,
        is_custom: bool = True,
    ) -> None:
        self._validate(name, weight_percent, period_number, category_mode, deduction_base_score)
        self.repository.update(
            EvaluationCategory(
                id=category_id,
                group_id=group_id,
                name=name,
                weight_percent=weight_percent,
                period_number=period_number,
                category_mode=category_mode,
                deduction_base_score=deduction_base_score,
                is_active=is_active,
                sort_order=sort_order,
                is_custom=is_custom,
            )
        )

    def delete(self, category_id: int) -> None:
        self.repository.delete(category_id)

    @staticmethod
    def _validate(
        name: str,
        weight_percent: float,
        period_number: int,
        category_mode: str,
        deduction_base_score: float,
    ) -> None:
        if not name.strip():
            raise ValueError("El nombre del criterio es obligatorio.")
        if weight_percent < 0 or weight_percent > 100:
            raise ValueError("Los puntos del criterio deben estar entre 0 y 100.")
        if period_number not in {1, 2, 3}:
            raise ValueError("El periodo del criterio es invalido.")
        if category_mode not in {"normal", "deduction"}:
            raise ValueError("El tipo de criterio es invalido.")
        if category_mode == "deduction" and deduction_base_score <= 0:
            raise ValueError("Un criterio por deduccion debe tener puntos mayores que cero.")
