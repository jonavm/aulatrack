from __future__ import annotations


class RiskAnalyzer:
    @staticmethod
    def evaluate_student(
        average: float,
        passing_grade: float,
        missing_count: int,
        unresolved_count: int,
        missing_threshold: int,
        low_performance_threshold: float,
    ) -> dict:
        reasons: list[str] = []

        if average < passing_grade:
            reasons.append("Promedio por debajo del minimo aprobatorio")
        if missing_count >= missing_threshold:
            reasons.append("Demasiadas actividades no entregadas")
        elif unresolved_count >= missing_threshold:
            reasons.append("Exceso de actividades pendientes o sin captura")
        if average <= low_performance_threshold:
            reasons.append("Rendimiento general bajo")

        return {
            "is_at_risk": bool(reasons),
            "reasons": reasons,
        }
