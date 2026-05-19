from __future__ import annotations

from collections import defaultdict


class GradeCalculator:
    """Centraliza calculos para mantener la UI simple y la logica testeable."""

    LEGACY_BASE = 10.0
    CURRENT_BASE = 100.0

    @staticmethod
    def validate_weights(category_weights: list[float]) -> bool:
        return round(sum(category_weights), 2) == 100.0

    @staticmethod
    def calculate_final_average(category_results: list[tuple[float, float]]) -> float:
        total = 0.0
        for category_average, weight_percent in category_results:
            total += category_average * (weight_percent / 100.0)
        return round(total, 2)

    @staticmethod
    def calculate_category_average(scores: list[float], max_scores: list[float]) -> float:
        if not scores or not max_scores:
            return 0.0

        normalized_scores = []
        for score, max_score in zip(scores, max_scores):
            if max_score <= 0:
                continue
            normalized_scores.append((score / max_score) * GradeCalculator.CURRENT_BASE)

        if not normalized_scores:
            return 0.0
        return round(sum(normalized_scores) / len(normalized_scores), 2)

    @staticmethod
    def normalize_legacy_threshold(value: float) -> float:
        if value <= GradeCalculator.LEGACY_BASE:
            return round(value * 10.0, 2)
        return round(value, 2)

    @staticmethod
    def group_scores_by_category(rows: list[dict]) -> dict[int, list[dict]]:
        grouped: dict[int, list[dict]] = defaultdict(list)
        for row in rows:
            grouped[row["category_id"]].append(row)
        return grouped
