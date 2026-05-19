from __future__ import annotations

from itertools import cycle
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.connection import initialize_database, get_connection
from services.activity_service import ActivityService
from services.attendance_service import AttendanceService
from services.category_service import CategoryService
from services.gradebook_service import GradebookService
from services.group_service import GroupService
from services.school_service import SchoolService
from services.student_service import StudentService


GROUP_DEFINITIONS = [
    {
        "label": "2-A",
        "grade_level": "2",
        "group_section": "A",
        "subject_name": "Matematicas",
        "student_count": 12,
    },
    {
        "label": "2-B",
        "grade_level": "2",
        "group_section": "B",
        "subject_name": "Fisica",
        "student_count": 11,
    },
    {
        "label": "2-C",
        "grade_level": "2",
        "group_section": "C",
        "subject_name": "Quimica",
        "student_count": 10,
    },
]

FIRST_NAMES = [
    "Ana",
    "Luis",
    "Sofia",
    "Diego",
    "Valeria",
    "Mateo",
    "Camila",
    "Emilio",
    "Daniela",
    "Hector",
    "Julia",
    "Miguel",
    "Regina",
    "Pablo",
    "Mariana",
    "Nicolas",
]

LAST_NAMES = [
    "Lopez Garcia",
    "Perez Soto",
    "Ramirez Cruz",
    "Torres Silva",
    "Morales Vega",
    "Sanchez Diaz",
    "Ruiz Torres",
    "Castro Luna",
    "Navarro Ortiz",
    "Flores Rios",
    "Hernandez Mata",
    "Vargas Leon",
]

ATTENDANCE_PATTERN = [
    "present",
    "present",
    "late",
    "present",
    "absent",
    "present",
    "justified",
    "present",
]


def reset_database() -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM attendance_records")
        connection.execute("DELETE FROM attendance_sessions")
        connection.execute("DELETE FROM grades")
        connection.execute("DELETE FROM activities")
        connection.execute("DELETE FROM student_category_deduction_entries")
        connection.execute("DELETE FROM student_adjustments")
        connection.execute("DELETE FROM risk_rules")
        connection.execute("DELETE FROM evaluation_categories")
        connection.execute("DELETE FROM students")
        connection.execute("DELETE FROM groups")
        connection.execute("DELETE FROM schools")


def main() -> None:
    initialize_database()
    reset_database()

    school_service = SchoolService()
    group_service = GroupService()
    student_service = StudentService()
    category_service = CategoryService()
    activity_service = ActivityService()
    attendance_service = AttendanceService()
    gradebook_service = GradebookService()

    school = school_service.create_school("ESCUELA SECUNDARIA TECNICA 82")
    date_list = ["2026-05-12", "2026-05-13", "2026-05-14", "2026-05-15", "2026-05-16"]

    total_students = 0
    total_groups = 0

    for group_index, config in enumerate(GROUP_DEFINITIONS):
        group = group_service.create_group(
            name=config["label"],
            school_id=school.id,
            subject_name=config["subject_name"],
            school_year="2025-2026",
            grade_level=config["grade_level"],
            group_section=config["group_section"],
            passing_grade=60.0,
        )
        total_groups += 1

        students = []
        for student_index in range(config["student_count"]):
            first_name = FIRST_NAMES[(group_index * 5 + student_index) % len(FIRST_NAMES)]
            last_name = LAST_NAMES[(group_index * 4 + student_index) % len(LAST_NAMES)]
            student = student_service.create_student(
                group.id,
                first_name=first_name,
                last_name=last_name,
                student_code=f"{config['label']}-{student_index + 1:02d}",
                is_active=True,
                notes="",
            )
            students.append(student)
            total_students += 1

        exam_category = category_service.create(
            group_id=group.id,
            name="Examen",
            weight_percent=40,
            period_number=1,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=1,
        )
        tasks_category = category_service.create(
            group_id=group.id,
            name="Tareas",
            weight_percent=30,
            period_number=1,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=2,
        )
        participation_category = category_service.create(
            group_id=group.id,
            name="Participacion",
            weight_percent=20,
            period_number=1,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=3,
        )
        discipline_category = category_service.create(
            group_id=group.id,
            name="Disciplina",
            weight_percent=10,
            period_number=1,
            category_mode="deduction",
            deduction_base_score=10,
            is_active=True,
            sort_order=4,
        )
        project_category = category_service.create(
            group_id=group.id,
            name="Proyecto",
            weight_percent=100,
            period_number=2,
            category_mode="normal",
            deduction_base_score=100,
            is_active=True,
            sort_order=1,
        )

        activities = [
            activity_service.create(
                category_id=exam_category.id,
                name="Examen parcial",
                max_score=100,
                due_date="2026-05-20",
                applies_to_risk=True,
                sort_order=1,
            ),
            activity_service.create(
                category_id=tasks_category.id,
                name="Tarea 1",
                max_score=100,
                due_date="2026-05-18",
                applies_to_risk=True,
                sort_order=1,
            ),
            activity_service.create(
                category_id=tasks_category.id,
                name="Tarea 2",
                max_score=100,
                due_date="2026-05-22",
                applies_to_risk=True,
                sort_order=2,
            ),
            activity_service.create(
                category_id=participation_category.id,
                name="Participacion semanal",
                max_score=100,
                due_date="2026-05-23",
                applies_to_risk=True,
                sort_order=1,
            ),
            activity_service.create(
                category_id=project_category.id,
                name="Proyecto integrador",
                max_score=100,
                due_date="2026-06-10",
                applies_to_risk=True,
                sort_order=1,
            ),
        ]

        for student_index, student in enumerate(students):
            score_seed = 92 - (student_index * 3) - (group_index * 2)
            score_variants = [
                max(45, min(100, score_seed)),
                max(40, min(100, score_seed - 6)),
                max(35, min(100, score_seed - 10)),
                max(50, min(100, score_seed + 2)),
                max(55, min(100, score_seed - 4)),
            ]
            for activity, score in zip(activities, score_variants, strict=True):
                if student_index % 7 == 0 and activity.name == "Tarea 2":
                    gradebook_service.save_entry(activity.id, student.id, None, "missing", "No entregada")
                elif student_index % 5 == 0 and activity.name == "Proyecto integrador":
                    gradebook_service.save_entry(activity.id, student.id, None, "pending", "Pendiente")
                else:
                    gradebook_service.save_entry(activity.id, student.id, float(score), "graded", "")

            adjustment = 0.0
            if student_index % 6 == 0:
                adjustment = 1.5
            elif student_index % 8 == 0:
                adjustment = -2.0
            if adjustment:
                gradebook_service.save_adjustment(group.id, student.id, adjustment)

            if student_index % 4 == 0:
                gradebook_service.add_category_deduction(
                    discipline_category.id,
                    student.id,
                    1.0,
                    "Falta de material",
                )
            if student_index % 9 == 0:
                gradebook_service.add_category_deduction(
                    discipline_category.id,
                    student.id,
                    1.5,
                    "Retardo acumulado",
                )

        pattern = cycle(ATTENDANCE_PATTERN[group_index:] + ATTENDANCE_PATTERN[:group_index])
        for date_offset, session_date in enumerate(date_list):
            snapshot = attendance_service.get_daily_attendance(group.id, session_date)
            session_id = snapshot["session"].id
            for student_index, student in enumerate(students):
                status = next(pattern)
                if (student_index + date_offset) % 11 == 0:
                    status = "absent"
                elif (student_index + date_offset) % 6 == 0:
                    status = "late"
                elif (student_index + date_offset) % 13 == 0:
                    status = "justified"
                attendance_service.save_status(session_id, student.id, status)

    print(f"Demo cargado correctamente: {total_groups} grupos, {total_students} alumnos.")


if __name__ == "__main__":
    main()
