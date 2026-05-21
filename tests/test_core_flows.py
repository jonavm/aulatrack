from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import database.connection as db_connection
import services.database_service as db_service_module
from services.activity_service import ActivityService
from services.attendance_service import AttendanceService
from services.category_service import CategoryService
from services.database_service import DatabaseService
from services.gradebook_service import GradebookService
from services.group_service import GroupService
from services.student_profile_service import StudentProfileService
from services.student_import_service import ImportPreview, ParsedStudent
from services.student_service import StudentService


class CoreFlowsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._original_db_dir = db_connection.DB_DIR
        self._original_db_path = db_connection.DB_PATH
        self._original_service_db_path = db_service_module.DB_PATH

        self._temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self._temp_dir.name)
        temp_db_dir = self.temp_path / "data"
        temp_db_path = temp_db_dir / "aulatrack_test.db"

        db_connection.DB_DIR = temp_db_dir
        db_connection.DB_PATH = temp_db_path
        db_service_module.DB_PATH = temp_db_path
        db_connection.initialize_database()

        self.group_service = GroupService()
        self.student_service = StudentService()
        self.attendance_service = AttendanceService()
        self.category_service = CategoryService()
        self.activity_service = ActivityService()
        self.gradebook_service = GradebookService()
        self.student_profile_service = StudentProfileService()
        self.database_service = DatabaseService()

    def tearDown(self) -> None:
        db_connection.DB_DIR = self._original_db_dir
        db_connection.DB_PATH = self._original_db_path
        db_service_module.DB_PATH = self._original_service_db_path
        self._temp_dir.cleanup()

    def test_group_and_student_persistence_flow(self) -> None:
        group = self._create_group()
        student = self.student_service.create_student(
            group.id,
            first_name="Ana",
            last_name="Lopez Garcia",
            student_code="A-01",
            is_active=True,
            notes="Sin observaciones",
        )

        groups = self.group_service.list_groups()
        students = self.student_service.list_students_by_group(group.id)

        self.assertEqual(1, len(groups))
        self.assertEqual("2-C", groups[0].display_name)
        self.assertIsNotNone(student.id)
        self.assertEqual(1, len(students))
        self.assertEqual("Lopez Garcia Ana", students[0].roster_name)

    def test_import_students_skips_duplicates(self) -> None:
        group = self._create_group()
        self.student_service.create_student(
            group.id,
            first_name="Ana",
            last_name="Lopez Garcia",
            student_code="A-01",
            is_active=True,
            notes="",
        )
        preview = ImportPreview(
            source_name="grupo.csv",
            total_rows=3,
            detected_mode="csv",
            students=[
                ParsedStudent(first_name="Ana", last_name="Lopez Garcia", student_code="A-01"),
                ParsedStudent(first_name="Luis", last_name="Perez Soto", student_code="A-02"),
            ],
            warnings=[],
            detected_group="2-C",
        )

        result = self.student_service.import_students(group.id, preview)
        students = self.student_service.list_students_by_group(group.id)

        self.assertEqual(1, result["created"])
        self.assertEqual(1, result["skipped"])
        self.assertEqual(2, len(students))

    def test_attendance_flow_creates_session_and_persists_status(self) -> None:
        group = self._create_group()
        student = self.student_service.create_student(
            group.id,
            first_name="Mario",
            last_name="Sanchez Diaz",
            student_code="A-03",
            is_active=True,
            notes="",
        )

        snapshot = self.attendance_service.get_daily_attendance(group.id, "2026-05-19")
        self.attendance_service.save_status(snapshot["session"].id, student.id, "late")
        refreshed = self.attendance_service.get_attendance_by_session(snapshot["session"].id)
        summary = self.attendance_service.build_summary(refreshed["students"], refreshed["records"])

        self.assertEqual(1, len(refreshed["records"]))
        self.assertEqual("late", refreshed["records"][0].status)
        self.assertEqual(1, summary["late"])
        self.assertEqual(0, summary["absent"])

    def test_gradebook_snapshot_includes_scores_adjustments_and_deductions(self) -> None:
        group = self._create_group()
        student = self.student_service.create_student(
            group.id,
            first_name="Elena",
            last_name="Ruiz Torres",
            student_code="A-04",
            is_active=True,
            notes="",
        )
        normal_category = self.category_service.create(
            group_id=group.id,
            name="Examen",
            weight_percent=70,
            period_number=1,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=1,
        )
        deduction_category = self.category_service.create(
            group_id=group.id,
            name="Disciplina",
            weight_percent=30,
            period_number=1,
            category_mode="deduction",
            deduction_base_score=10,
            is_active=True,
            sort_order=2,
        )
        activity = self.activity_service.create(
            category_id=normal_category.id,
            name="Examen parcial",
            max_score=100,
            due_date="2026-05-20",
            applies_to_risk=True,
            sort_order=1,
        )

        self.gradebook_service.save_entry(activity.id, student.id, 95.0, "graded", "Buen trabajo")
        self.gradebook_service.save_adjustment(group.id, student.id, 1.5)
        self.gradebook_service.add_category_deduction(
            deduction_category.id,
            student.id,
            2.0,
            "Llego sin uniforme completo",
        )

        snapshot = self.gradebook_service.build_snapshot(group.id, 1)

        self.assertEqual(1, len(snapshot["students"]))
        self.assertEqual(2, len(snapshot["categories"]))
        self.assertEqual(1, len(snapshot["activities"]))
        self.assertEqual(1, len(snapshot["grades"]))
        self.assertEqual("graded", snapshot["grades"][0].status)
        self.assertEqual(95.0, snapshot["grades"][0].score)
        self.assertEqual(1, len(snapshot["adjustments"]))
        self.assertEqual(1.5, snapshot["adjustments"][0].points)
        self.assertEqual(1, len(snapshot["adjustment_entries"]))
        self.assertEqual(1.5, snapshot["adjustment_entries"][0].points)
        self.assertEqual(1, len(snapshot["category_deductions"]))
        self.assertEqual(2.0, snapshot["category_deductions"][0].points)

    def test_student_profile_includes_graded_and_pending_activity_lists(self) -> None:
        group = self._create_group()
        student = self.student_service.create_student(
            group.id,
            first_name="Lucia",
            last_name="Herrera Solis",
            student_code="A-06",
            is_active=True,
            notes="",
        )
        category = self.category_service.create(
            group_id=group.id,
            name="Tareas",
            weight_percent=100,
            period_number=1,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=1,
        )
        graded_activity = self.activity_service.create(
            category_id=category.id,
            name="Tarea 1",
            max_score=10,
            due_date="2026-05-21",
            applies_to_risk=True,
            sort_order=1,
        )
        pending_activity = self.activity_service.create(
            category_id=category.id,
            name="Tarea 2",
            max_score=10,
            due_date="2026-05-22",
            applies_to_risk=True,
            sort_order=2,
        )

        self.gradebook_service.save_entry(graded_activity.id, student.id, 9.0, "graded", "")
        self.gradebook_service.save_entry(pending_activity.id, student.id, None, "pending", "")

        profile = self.student_profile_service.build_profile(group.id, student.id)

        self.assertIsNotNone(profile)
        grade_summary = profile["grade_summary"]
        self.assertEqual(1, len(grade_summary["graded_activities"]))
        self.assertEqual("Tarea 1", grade_summary["graded_activities"][0]["activity_name"])
        self.assertEqual(1, len(grade_summary["pending_activities"]))
        self.assertEqual("Tarea 2", grade_summary["pending_activities"][0]["activity_name"])
        self.assertEqual("pending", grade_summary["pending_activities"][0]["status"])

    def test_category_creation_rejects_active_weights_above_100(self) -> None:
        group = self._create_group()
        self.category_service.create(
            group_id=group.id,
            name="Examen",
            weight_percent=70,
            period_number=1,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=1,
        )

        with self.assertRaisesRegex(ValueError, "no puede superar 100"):
            self.category_service.create(
                group_id=group.id,
                name="Proyecto",
                weight_percent=40,
                period_number=1,
                category_mode="normal",
                deduction_base_score=100,
                is_active=True,
                sort_order=2,
            )

    def test_category_update_rejects_active_weights_above_100(self) -> None:
        group = self._create_group()
        category_a = self.category_service.create(
            group_id=group.id,
            name="Examen",
            weight_percent=60,
            period_number=1,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=1,
        )
        category_b = self.category_service.create(
            group_id=group.id,
            name="Proyecto",
            weight_percent=40,
            period_number=1,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=2,
        )

        with self.assertRaisesRegex(ValueError, "no puede superar 100"):
            self.category_service.update(
                category_b.id,
                group.id,
                name="Proyecto",
                weight_percent=50,
                period_number=1,
                category_mode="normal",
                deduction_base_score=100,
                is_active=True,
                sort_order=2,
            )

    def test_backup_and_restore_recovers_deleted_data(self) -> None:
        group = self._create_group()
        self.student_service.create_student(
            group.id,
            first_name="Julia",
            last_name="Morales Vega",
            student_code="A-05",
            is_active=True,
            notes="",
        )
        backup_path = self.temp_path / "respaldos" / "copia_segura.db"

        created_backup = self.database_service.create_backup(str(backup_path))
        self.group_service.delete_group(group.id)
        self.assertEqual([], self.group_service.list_groups())

        self.database_service.restore_backup(str(created_backup))
        restored_groups = self.group_service.list_groups()
        restored_students = self.student_service.list_students_by_group(restored_groups[0].id)

        self.assertEqual(1, len(restored_groups))
        self.assertEqual("2-C", restored_groups[0].display_name)
        self.assertEqual(1, len(restored_students))
        self.assertEqual("Julia", restored_students[0].first_name)

    def _create_group(self):
        return self.group_service.create_group(
            name="2-C",
            school_id=None,
            subject_name="Matematicas",
            school_year="2025-2026",
            grade_level="2",
            group_section="c",
            passing_grade=60.0,
        )


if __name__ == "__main__":
    unittest.main()
