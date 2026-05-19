from __future__ import annotations

from database.connection import get_connection


class DashboardService:
    def get_summary(self, group_id: int | None = None) -> dict:
        total_groups_query = "SELECT COUNT(*) FROM groups"
        groups_without_students_query = """
            SELECT COUNT(*)
            FROM (
                SELECT g.id
                FROM groups g
                LEFT JOIN students s ON s.group_id = g.id AND s.is_active = 1
                GROUP BY g.id
                HAVING COUNT(s.id) = 0
            )
        """

        with get_connection() as connection:
            total_groups = connection.execute(total_groups_query).fetchone()[0] or 0
            groups_without_students = connection.execute(groups_without_students_query).fetchone()[0] or 0

            if group_id is None:
                row = connection.execute(
                    """
                    SELECT
                        COUNT(*) AS total_students,
                        COALESCE(AVG(
                            CASE
                                WHEN g.score IS NOT NULL AND a.max_score > 0 THEN (g.score * 100.0 / a.max_score)
                            END
                        ), 0) AS overall_average
                    FROM students s
                    LEFT JOIN grades g ON g.student_id = s.id
                    LEFT JOIN activities a ON a.id = g.activity_id
                    WHERE s.is_active = 1
                    """
                ).fetchone()
            else:
                row = connection.execute(
                    """
                    SELECT
                        COUNT(DISTINCT s.id) AS total_students,
                        COALESCE(AVG(
                            CASE
                                WHEN g.score IS NOT NULL AND a.max_score > 0 THEN (g.score * 100.0 / a.max_score)
                            END
                        ), 0) AS overall_average
                    FROM students s
                    LEFT JOIN evaluation_categories c
                        ON c.group_id = s.group_id AND c.is_active = 1
                    LEFT JOIN activities a
                        ON a.category_id = c.id
                    LEFT JOIN grades g
                        ON g.activity_id = a.id AND g.student_id = s.id
                    WHERE s.group_id = ? AND s.is_active = 1
                    """,
                    (group_id,),
                ).fetchone()

            total_students = row["total_students"] or 0
            overall_average = round(row["overall_average"] or 0.0, 1)

            attendance_rate = self._get_attendance_rate(connection, group_id)
            pending_activities = self._get_pending_activities(connection, group_id)
            at_risk_students = self._get_risk_students(connection, group_id)

        avg_students_per_group = round(total_students / total_groups, 1) if total_groups and group_id is None else overall_average

        return {
            "total_groups": total_groups,
            "total_students": total_students,
            "avg_students_per_group": avg_students_per_group,
            "groups_without_students": groups_without_students,
            "attendance_rate": attendance_rate,
            "pending_activities": pending_activities,
            "at_risk_students": at_risk_students,
        }

    def get_group_average_rows(self) -> list[dict]:
        query = """
            SELECT
                grp.id,
                grp.name,
                sc.name AS school_name,
                grp.grade_level,
                grp.group_section,
                COALESCE(AVG(
                    CASE
                        WHEN g.score IS NOT NULL AND a.max_score > 0 THEN (g.score * 100.0 / a.max_score)
                    END
                ), 0) AS average_score
            FROM groups grp
            LEFT JOIN schools sc
                ON sc.id = grp.school_id
            LEFT JOIN students s
                ON s.group_id = grp.id AND s.is_active = 1
            LEFT JOIN evaluation_categories c
                ON c.group_id = grp.id AND c.is_active = 1
            LEFT JOIN activities a
                ON a.category_id = c.id
            LEFT JOIN grades g
                ON g.activity_id = a.id AND g.student_id = s.id
            GROUP BY grp.id, grp.name, sc.name, grp.grade_level, grp.group_section
            ORDER BY grp.grade_level, grp.group_section, grp.name
        """
        with get_connection() as connection:
            rows = connection.execute(query).fetchall()

        result: list[dict] = []
        for row in rows:
            grade_level = (row["grade_level"] or "").strip()
            group_section = (row["group_section"] or "").strip().upper()
            if grade_level and group_section:
                label = f"{grade_level}-{group_section}"
            else:
                label = row["name"]
            school_name = " ".join((row["school_name"] or "").strip().split())
            if school_name:
                label = f"{label} · {school_name}"
            result.append(
                {
                    "group_id": row["id"],
                    "label": label,
                    "average": round(row["average_score"] or 0.0, 1),
                }
            )
        return result

    def get_grade_distribution(self, group_id: int | None) -> list[dict]:
        if group_id is None:
            return []
        students = self._get_student_risk_rows(group_id)
        buckets = [
            ("Excelente", 90, 101, "#22A45D"),
            ("Bueno", 80, 90, "#4169E1"),
            ("Regular", 60, 80, "#F59E0B"),
            ("Riesgo", -1, 60, "#EF4444"),
        ]
        total = len(students)
        rows: list[dict] = []
        for label, minimum, maximum, color in buckets:
            count = sum(1 for student in students if minimum <= student["average"] < maximum)
            percent = round((count / total) * 100) if total else 0
            rows.append({"label": label, "count": count, "percent": percent, "color": color})
        return rows

    def get_alerts(self, group_id: int | None) -> list[dict]:
        with get_connection() as connection:
            summary = self.get_summary(group_id)
            alerts: list[dict] = []
            if summary["at_risk_students"] > 0:
                alerts.append(
                    {
                        "title": f'{summary["at_risk_students"]} alumnos en riesgo academico',
                        "detail": "Conviene revisar calificaciones y pendientes cuanto antes.",
                        "tone": "danger",
                    }
                )
            if summary["pending_activities"] > 0:
                alerts.append(
                    {
                        "title": f'{summary["pending_activities"]} actividades con captura pendiente',
                        "detail": "Todavia faltan notas por registrar en este grupo.",
                        "tone": "warning",
                    }
                )
            if summary["attendance_rate"] > 0:
                alerts.append(
                    {
                        "title": f'Asistencia reciente: {summary["attendance_rate"]:.0f}%',
                        "detail": "Calculada con las sesiones registradas en los ultimos 7 dias.",
                        "tone": "info",
                    }
                )
            if group_id is None and summary["groups_without_students"] > 0:
                alerts.append(
                    {
                        "title": f'{summary["groups_without_students"]} grupos aun no tienen alumnos',
                        "detail": "Completa esas listas antes de pasar a asistencia o calificaciones.",
                        "tone": "warning",
                    }
                )
            if not alerts:
                alerts.append(
                    {
                        "title": "Todo en orden por ahora",
                        "detail": "No hay alertas urgentes en los datos disponibles.",
                        "tone": "success",
                    }
                )
        return alerts[:4]

    def get_recent_activities(self, group_id: int | None, search_text: str = "") -> list[dict]:
        if group_id is None:
            return []
        query = """
            SELECT
                a.id,
                a.name,
                c.name AS category_name,
                a.due_date,
                COUNT(DISTINCT s.id) AS total_students,
                COUNT(DISTINCT CASE WHEN g.score IS NOT NULL THEN g.student_id END) AS graded_students
            FROM activities a
            JOIN evaluation_categories c ON c.id = a.category_id
            LEFT JOIN students s ON s.group_id = c.group_id AND s.is_active = 1
            LEFT JOIN grades g ON g.activity_id = a.id AND g.student_id = s.id
            WHERE c.group_id = ?
            GROUP BY a.id, a.name, c.name, a.due_date
            ORDER BY
                CASE WHEN a.due_date IS NULL OR a.due_date = '' THEN 1 ELSE 0 END,
                a.due_date ASC,
                a.id DESC
            LIMIT 12
        """
        with get_connection() as connection:
            rows = connection.execute(query, (group_id,)).fetchall()

        search_lower = search_text.strip().lower()
        activities: list[dict] = []
        for row in rows:
            total_students = row["total_students"] or 0
            graded_students = row["graded_students"] or 0
            if graded_students == 0:
                status = "Pendiente"
            elif graded_students >= total_students and total_students > 0:
                status = "Completa"
            else:
                status = "En progreso"
            item = {
                "name": row["name"],
                "category": row["category_name"],
                "due_date": row["due_date"] or "Sin fecha",
                "progress": f"{graded_students}/{total_students}" if total_students else "0/0",
                "status": status,
            }
            haystack = " ".join((item["name"], item["category"], item["due_date"], item["status"])).lower()
            if search_lower and search_lower not in haystack:
                continue
            activities.append(item)
        return activities[:5]

    def get_risk_students_table(self, group_id: int | None, search_text: str = "") -> list[dict]:
        if group_id is None:
            return []
        rows = self._get_student_risk_rows(group_id)
        search_lower = search_text.strip().lower()
        result: list[dict] = []
        for row in rows:
            issues: list[str] = []
            if row["average"] < row["passing_grade"]:
                issues.append("Promedio bajo")
            if row["pending_count"] >= 3:
                issues.append("Varias pendientes")
            if row["attendance_absences"] >= 2:
                issues.append("Faltas recientes")
            if not issues:
                continue
            item = {
                "name": row["name"],
                "average": f'{row["average"]:.1f}',
                "issues": ", ".join(issues),
                "status": "Revisar",
            }
            haystack = " ".join(item.values()).lower()
            if search_lower and search_lower not in haystack:
                continue
            result.append(item)
        result.sort(key=lambda item: float(item["average"]))
        return result[:5]

    def _get_student_risk_rows(self, group_id: int) -> list[dict]:
        query = """
            SELECT
                s.id,
                TRIM(s.last_name || ' ' || s.first_name) AS full_name,
                (
                    COALESCE((
                        SELECT AVG(CASE WHEN g.score IS NOT NULL AND a.max_score > 0 THEN (g.score * 100.0 / a.max_score) END)
                        FROM evaluation_categories c
                        JOIN activities a ON a.category_id = c.id
                        LEFT JOIN grades g ON g.activity_id = a.id AND g.student_id = s.id
                        WHERE c.group_id = s.group_id AND c.is_active = 1
                    ), 0) + COALESCE(sa.points, 0)
                ) AS average_score,
                (
                    SELECT COUNT(*)
                    FROM evaluation_categories c
                    JOIN activities a ON a.category_id = c.id
                    LEFT JOIN grades g ON g.activity_id = a.id AND g.student_id = s.id
                    WHERE c.group_id = s.group_id
                      AND (g.id IS NULL OR g.score IS NULL OR g.status = 'pending')
                ) AS pending_count,
                (
                    SELECT COUNT(*)
                    FROM attendance_records ar
                    JOIN attendance_sessions ass ON ass.id = ar.session_id
                    WHERE ar.student_id = s.id
                      AND ass.group_id = s.group_id
                      AND ass.session_date >= date('now', '-7 days')
                      AND ar.status = 'absent'
                ) AS attendance_absences,
                grp.passing_grade AS passing_grade
            FROM students s
            JOIN groups grp ON grp.id = s.group_id
            LEFT JOIN student_adjustments sa
                ON sa.group_id = s.group_id AND sa.student_id = s.id
            WHERE s.group_id = ? AND s.is_active = 1
            ORDER BY average_score ASC, full_name ASC
        """
        with get_connection() as connection:
            rows = connection.execute(query, (group_id,)).fetchall()
        return [
            {
                "student_id": row["id"],
                "name": row["full_name"],
                "average": round(row["average_score"] or 0.0, 1),
                "pending_count": row["pending_count"] or 0,
                "attendance_absences": row["attendance_absences"] or 0,
                "passing_grade": row["passing_grade"] or 60.0,
            }
            for row in rows
        ]

    @staticmethod
    def _get_attendance_rate(connection, group_id: int | None) -> float:
        if group_id is None:
            query = """
                SELECT
                    COUNT(*) AS total_records,
                    SUM(CASE WHEN ar.status IN ('present', 'late', 'justified') THEN 1 ELSE 0 END) AS attended_records
                FROM attendance_records ar
                JOIN attendance_sessions s ON s.id = ar.session_id
                WHERE s.session_date >= date('now', '-7 days')
            """
            row = connection.execute(query).fetchone()
        else:
            query = """
                SELECT
                    COUNT(*) AS total_records,
                    SUM(CASE WHEN ar.status IN ('present', 'late', 'justified') THEN 1 ELSE 0 END) AS attended_records
                FROM attendance_records ar
                JOIN attendance_sessions s ON s.id = ar.session_id
                WHERE s.group_id = ? AND s.session_date >= date('now', '-7 days')
            """
            row = connection.execute(query, (group_id,)).fetchone()
        total_records = row["total_records"] or 0
        attended_records = row["attended_records"] or 0
        return round((attended_records / total_records) * 100, 1) if total_records else 0.0

    @staticmethod
    def _get_pending_activities(connection, group_id: int | None) -> int:
        if group_id is None:
            query = """
                SELECT COUNT(DISTINCT a.id) AS pending_activities
                FROM activities a
                JOIN evaluation_categories c ON c.id = a.category_id
                JOIN students s ON s.group_id = c.group_id AND s.is_active = 1
                LEFT JOIN grades g ON g.activity_id = a.id AND g.student_id = s.id
                WHERE g.id IS NULL OR g.score IS NULL OR g.status = 'pending'
            """
            row = connection.execute(query).fetchone()
        else:
            query = """
                SELECT COUNT(DISTINCT a.id) AS pending_activities
                FROM activities a
                JOIN evaluation_categories c ON c.id = a.category_id
                JOIN students s ON s.group_id = c.group_id AND s.is_active = 1
                LEFT JOIN grades g ON g.activity_id = a.id AND g.student_id = s.id
                WHERE c.group_id = ? AND (g.id IS NULL OR g.score IS NULL OR g.status = 'pending')
            """
            row = connection.execute(query, (group_id,)).fetchone()
        return row["pending_activities"] or 0

    def _get_risk_students(self, connection, group_id: int | None) -> int:
        if group_id is None:
            return 0
        rows = self._get_student_risk_rows(group_id)
        return sum(
            1
            for row in rows
            if row["average"] < row["passing_grade"] or row["pending_count"] >= 3 or row["attendance_absences"] >= 2
        )
