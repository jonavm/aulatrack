from __future__ import annotations

from services.adjustment_service import AdjustmentService
from services.attendance_service import AttendanceService
from services.category_service import CategoryService
from services.grade_entry_service import GradeEntryService
from services.grade_service import GradeCalculator
from services.gradebook_service import GradebookService
from services.group_service import GroupService
from services.activity_service import ActivityService
from services.student_category_deduction_service import StudentCategoryDeductionService
from services.student_service import StudentService


class StudentProfileService:
    def __init__(self) -> None:
        self.student_service = StudentService()
        self.group_service = GroupService()
        self.category_service = CategoryService()
        self.activity_service = ActivityService()
        self.grade_entry_service = GradeEntryService()
        self.adjustment_service = AdjustmentService()
        self.student_category_deduction_service = StudentCategoryDeductionService()
        self.attendance_service = AttendanceService()

    def build_profile(self, group_id: int, student_id: int) -> dict | None:
        group = next((item for item in self.group_service.list_groups() if item.id == group_id), None)
        student = next((item for item in self.student_service.list_students_by_group(group_id) if item.id == student_id), None)
        if group is None or student is None:
            return None

        categories = self.category_service.list_by_group(group_id)
        activities = self.activity_service.list_by_group(group_id)
        grades = self.grade_entry_service.list_by_group(group_id)
        adjustments = self.adjustment_service.list_by_group(group_id)
        category_deductions = self.student_category_deduction_service.list_by_group(group_id)

        active_categories = [item for item in categories if item.is_active]
        student_grades = {
            item.activity_id: item
            for item in grades
            if item.student_id == student_id
        }
        adjustment = next((item for item in adjustments if item.student_id == student_id), None)
        adjustment_points = adjustment.points if adjustment else 0.0
        student_deductions: dict[int, list] = {}
        for item in category_deductions:
            if item.student_id != student_id:
                continue
            student_deductions.setdefault(item.category_id, []).append(item)

        category_rows: list[dict] = []
        unresolved_count = 0
        missing_count = 0

        for category in active_categories:
            category_activities = [item for item in activities if item.category_id == category.id]
            scores: list[float] = []
            max_scores: list[float] = []
            deduction_total = 0.0

            for activity in category_activities:
                grade = student_grades.get(activity.id)
                if grade and grade.score is not None:
                    scores.append(grade.score)
                    max_scores.append(activity.max_score)
                    continue
                if category.category_mode == "deduction":
                    continue
                unresolved_count += 1
                if grade and grade.status == "missing":
                    missing_count += 1

            if category.category_mode == "deduction":
                deduction_entries = student_deductions.get(category.id, [])
                deduction_total = round(sum(item.points for item in deduction_entries), 2)
                available_points = round(category.weight_percent, 2)
                if available_points <= 0:
                    category_average = 0.0
                    contribution_points = 0.0
                else:
                    remaining = max(0.0, available_points - deduction_total)
                    category_average = round((remaining / available_points) * 100.0, 2)
                    contribution_points = round(remaining, 2)
            else:
                category_average = GradeCalculator.calculate_category_average(scores, max_scores)
                contribution_points = round(category_average * (category.weight_percent / 100.0), 2)

            category_rows.append(
                {
                    "name": category.name,
                    "weight_percent": category.weight_percent,
                    "average": category_average,
                    "points": contribution_points,
                    "activity_count": len(category_activities),
                    "mode": category.category_mode,
                    "deduction_points": deduction_total if category.category_mode == "deduction" else 0.0,
                    "deduction_note": deduction_entries[0].note if category.category_mode == "deduction" and deduction_entries and deduction_entries[0].note else "",
                    "deduction_count": len(deduction_entries) if category.category_mode == "deduction" else 0,
                }
            )

        average = round(sum(row["points"] for row in category_rows), 2) if active_categories else 0.0
        adjusted_average = round(max(0.0, min(100.0, average + adjustment_points)), 2)
        risk = GradebookService.build_risk_result(
            adjusted_average,
            group.passing_grade,
            missing_count,
            unresolved_count,
        )

        attendance_sheet = self.attendance_service.get_attendance_sheet(group_id)
        statuses = [
            attendance_sheet["records"].get((student_id, session.id), "present")
            for session in attendance_sheet["sessions"]
        ]
        total_sessions = len(statuses)
        absent_count = sum(1 for status in statuses if status == "absent")
        late_count = sum(1 for status in statuses if status == "late")
        justified_count = sum(1 for status in statuses if status == "justified")
        present_count = total_sessions - absent_count - late_count - justified_count
        attendance_rate = round((present_count / total_sessions) * 100, 1) if total_sessions else 0.0
        recent_attendance = [
            {
                "date": session.session_date,
                "status": attendance_sheet["records"].get((student_id, session.id), "present"),
            }
            for session in attendance_sheet["sessions"][-8:]
        ]

        return {
            "group": group,
            "student": student,
            "grade_summary": {
                "average": average,
                "adjusted_average": adjusted_average,
                "adjustment_points": adjustment_points,
                "missing_count": missing_count,
                "unresolved_count": unresolved_count,
                "risk": risk,
                "categories": category_rows,
            },
            "attendance_summary": {
                "total_sessions": total_sessions,
                "present_count": present_count,
                "absent_count": absent_count,
                "late_count": late_count,
                "justified_count": justified_count,
                "attendance_rate": attendance_rate,
                "recent": recent_attendance,
            },
        }

    def save_notes(self, student_id: int, notes: str) -> None:
        self.student_service.update_notes(student_id, notes)
