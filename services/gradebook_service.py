from __future__ import annotations

from services.activity_service import ActivityService
from services.adjustment_service import AdjustmentService
from services.category_service import CategoryService
from services.grade_entry_service import GradeEntryService
from services.group_service import GroupService
from services.risk_service import RiskAnalyzer
from services.student_category_deduction_service import StudentCategoryDeductionService
from services.student_service import StudentService


class GradebookService:
    def __init__(self) -> None:
        self.group_service = GroupService()
        self.student_service = StudentService()
        self.category_service = CategoryService()
        self.activity_service = ActivityService()
        self.grade_entry_service = GradeEntryService()
        self.adjustment_service = AdjustmentService()
        self.student_category_deduction_service = StudentCategoryDeductionService()

    def build_snapshot(self, group_id: int, period_number: int = 1) -> dict:
        students = self.student_service.list_students_by_group(group_id)
        categories = self.category_service.list_by_group(group_id, period_number)
        activities = self.activity_service.list_by_group(group_id, period_number)
        grades = self.grade_entry_service.list_by_group(group_id, period_number)
        adjustments = self.adjustment_service.list_by_group(group_id)
        category_deductions = self.student_category_deduction_service.list_by_group(group_id, period_number)
        return {
            "students": students,
            "categories": categories,
            "activities": activities,
            "grades": grades,
            "adjustments": adjustments,
            "category_deductions": category_deductions,
        }

    def save_entry(
        self,
        activity_id: int,
        student_id: int,
        score: float | None,
        status: str,
        comment: str = "",
    ) -> None:
        self.grade_entry_service.save_entry(activity_id, student_id, score, status, comment)

    def save_adjustment(self, group_id: int, student_id: int, points: float) -> None:
        self.adjustment_service.save_adjustment(group_id, student_id, points)

    def add_category_deduction(self, category_id: int, student_id: int, points: float, note: str) -> None:
        self.student_category_deduction_service.add_entry(category_id, student_id, points, note)

    @staticmethod
    def build_risk_result(
        average: float,
        passing_grade: float,
        missing_count: int,
        unresolved_count: int,
    ) -> dict:
        return RiskAnalyzer.evaluate_student(
            average=average,
            passing_grade=passing_grade,
            missing_count=missing_count,
            unresolved_count=unresolved_count,
            missing_threshold=3,
            low_performance_threshold=50.0,
        )
