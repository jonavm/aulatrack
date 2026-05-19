from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from models.entities import Activity, EvaluationCategory, GradeEntry, Student, StudentAdjustment, StudentCategoryDeductionEntry
from services.grade_service import GradeCalculator
from services.gradebook_service import GradebookService
from themes.theme import get_theme_tokens


class GradebookStudentTableModel(QAbstractTableModel):
    USER_ROLE_MAX_SCORE = 1001
    USER_ROLE_STATUS = 1002
    USER_ROLE_DEDUCTION_TARGET = 1003

    def __init__(self) -> None:
        super().__init__()
        self._students: list[Student] = []
        self._activities: list[Activity] = []
        self._visible_activities: list[Activity] = []
        self._categories: list[EvaluationCategory] = []
        self._active_categories: list[EvaluationCategory] = []
        self._grade_lookup: dict[tuple[int, int], GradeEntry] = {}
        self._adjustment_lookup: dict[int, StudentAdjustment] = {}
        self._category_deduction_lookup: dict[tuple[int, int], list[StudentCategoryDeductionEntry]] = {}
        self._group_id: int | None = None
        self._passing_grade = 60.0
        self._save_callback = None
        self._save_adjustment_callback = None
        self._save_category_deduction_callback = None

    def set_snapshot(
        self,
        *,
        group_id: int | None,
        students: list[Student],
        activities: list[Activity],
        categories: list[EvaluationCategory],
        grades: list[GradeEntry],
        adjustments: list[StudentAdjustment],
        category_deductions: list[StudentCategoryDeductionEntry],
        passing_grade: float,
        save_callback,
        save_adjustment_callback,
        save_category_deduction_callback,
    ) -> None:
        self.beginResetModel()
        self._group_id = group_id
        self._students = students
        self._activities = activities
        self._categories = categories
        self._active_categories = [item for item in categories if item.is_active]
        self._visible_activities = [
            item
            for item in activities
            if (self._activity_category(item) or EvaluationCategory(id=None, group_id=0, name="", weight_percent=0)).category_mode != "deduction"
        ]
        self._grade_lookup = {(item.student_id, item.activity_id): item for item in grades}
        self._adjustment_lookup = {item.student_id: item for item in adjustments}
        deduction_lookup: dict[tuple[int, int], list[StudentCategoryDeductionEntry]] = {}
        for item in category_deductions:
            deduction_lookup.setdefault((item.student_id, item.category_id), []).append(item)
        self._category_deduction_lookup = deduction_lookup
        self._passing_grade = passing_grade
        self._save_callback = save_callback
        self._save_adjustment_callback = save_adjustment_callback
        self._save_category_deduction_callback = save_category_deduction_callback
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._students)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else 5 + len(self._visible_activities) + len(self._active_categories)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        tokens = get_theme_tokens()
        if not index.isValid():
            return None

        student = self._students[index.row()]
        activity_start = 1
        category_avg_start = 1 + len(self._visible_activities)
        average_col = category_avg_start + len(self._active_categories)
        adjustment_col = average_col + 1
        adjusted_average_col = average_col + 2
        missing_col = average_col + 3
        risk_col = average_col + 4

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return student.roster_name
            if activity_start <= index.column() < category_avg_start:
                activity = self._visible_activities[index.column() - activity_start]
                grade = self._grade_lookup.get((student.id, activity.id))
                if grade and grade.status == "missing":
                    return "NE"
                if grade and grade.status == "pending":
                    return "P"
                if grade and grade.score is not None:
                    return f"{grade.score:.1f}"
                return ""
            metrics = self._student_metrics(student)
            average = metrics["average"]
            missing_count = metrics["unresolved_count"]
            risk = metrics["risk"]
            if category_avg_start <= index.column() < average_col:
                category = self._active_categories[index.column() - category_avg_start]
                category_points = metrics["category_points"].get(category.id, 0.0)
                return f"{category_points:.2f}"
            if index.column() == average_col:
                return f"{average:.2f}"
            if index.column() == adjustment_col:
                adjustment = self._adjustment_lookup.get(student.id)
                points = adjustment.points if adjustment else 0.0
                return f"{points:+.2f}" if points else "0.00"
            if index.column() == adjusted_average_col:
                return f"{metrics['adjusted_average']:.2f}"
            if index.column() == missing_col:
                return str(missing_count)
            if index.column() == risk_col:
                return "En riesgo" if risk["is_at_risk"] else "Normal"

        if role == Qt.EditRole and activity_start <= index.column() < category_avg_start:
            activity = self._visible_activities[index.column() - activity_start]
            grade = self._grade_lookup.get((student.id, activity.id))
            if grade and grade.score is not None:
                return grade.score
            return 0.0

        if role == Qt.EditRole and category_avg_start <= index.column() < average_col:
            category = self._active_categories[index.column() - category_avg_start]
            if category.category_mode == "deduction":
                return {
                    "category_id": category.id,
                    "entries": self._category_deduction_entries(student.id, category.id),
                }

        if role == Qt.EditRole and index.column() == adjustment_col:
            adjustment = self._adjustment_lookup.get(student.id)
            return adjustment.points if adjustment else 0.0

        if role == self.USER_ROLE_MAX_SCORE and activity_start <= index.column() < category_avg_start:
            activity = self._visible_activities[index.column() - activity_start]
            return activity.max_score

        if role == self.USER_ROLE_STATUS and activity_start <= index.column() < category_avg_start:
            activity = self._visible_activities[index.column() - activity_start]
            grade = self._grade_lookup.get((student.id, activity.id))
            return grade.status if grade else "pending"

        if role == self.USER_ROLE_DEDUCTION_TARGET and category_avg_start <= index.column() < average_col:
            category = self._active_categories[index.column() - category_avg_start]
            if category.category_mode == "deduction":
                return {
                    "student_id": student.id,
                    "student_name": student.roster_name,
                    "category_id": category.id,
                    "category_name": category.name,
                    "max_points": category.weight_percent,
                    "entries": [
                        {
                            "id": item.id,
                            "points": item.points,
                            "note": item.note,
                            "created_at": item.created_at,
                        }
                        for item in self._category_deduction_entries(student.id, category.id)
                    ],
                }

        if role == Qt.ToolTipRole and index.column() == risk_col:
            metrics = self._student_metrics(student)
            risk = metrics["risk"]
            return "\n".join(risk["reasons"]) if risk["reasons"] else "Sin alertas"

        if role == Qt.ToolTipRole and index.column() == adjustment_col:
            return "Puntos extra o descuento manual aplicados al resultado del periodo."

        if role == Qt.BackgroundRole and index.column() == risk_col:
            metrics = self._student_metrics(student)
            risk = metrics["risk"]
            if risk["is_at_risk"]:
                return QColor(tokens["danger_soft_alt"])
            return QColor(tokens["success_soft"])

        if role == Qt.BackgroundRole and category_avg_start <= index.column() < average_col:
            category = self._active_categories[index.column() - category_avg_start]
            if category.category_mode == "deduction":
                return QColor(tokens["warning_soft"])

        if role == Qt.ToolTipRole and activity_start <= index.column() < category_avg_start:
            activity = self._visible_activities[index.column() - activity_start]
            category = self._activity_category(activity)
            grade = self._grade_lookup.get((student.id, activity.id))
            if category and category.category_mode == "deduction":
                if not grade:
                    return (
                        f"Sin captura. Escribe cuanto descontar a este alumno en este criterio "
                        f"(0 a {activity.max_score:.1f})."
                    )
                if grade.status == "missing":
                    return "Criterio marcado sin captura"
                if grade.status == "pending":
                    return "Criterio pendiente"
                return (
                    f"Descuento aplicado: {grade.score:.1f} / {activity.max_score:.1f}."
                )
            if not grade:
                return "Sin captura. Usa numero, P o M."
            if grade.status == "missing":
                return "No entregada"
            if grade.status == "pending":
                return "Pendiente"
            return f"Calificada: {grade.score:.1f} / {activity.max_score:.1f}"

        if role == Qt.ToolTipRole and category_avg_start <= index.column() < average_col:
            category = self._active_categories[index.column() - category_avg_start]
            if category.category_mode == "deduction":
                entries = self._category_deduction_entries(student.id, category.id)
                total_discount = self._category_deduction_total(student.id, category.id)
                note_text = ""
                if entries:
                    latest_note = entries[0].note.strip()
                    if latest_note:
                        note_text = f" Ultimo motivo: {latest_note}."
                return (
                    f"Puntos actuales de {category.name} para este alumno. "
                    f"Inicia con {category.weight_percent:.1f} puntos y lleva {total_discount:.1f} descontados en {len(entries)} registro(s). "
                    f"Haz clic para ver el historial y agregar un descuento nuevo.{note_text} "
                    f"Este criterio aporta esos puntos directamente al periodo."
                )
            return (
                f"Puntos actuales de {category.name}. "
                f"Se calculan con el promedio de sus actividades y el valor de {category.weight_percent:.1f} puntos de este criterio."
            )

        if role == Qt.BackgroundRole and activity_start <= index.column() < category_avg_start:
            activity = self._visible_activities[index.column() - activity_start]
            category = self._activity_category(activity)
            if category and category.category_mode == "deduction":
                return QColor(tokens["warning_soft"])

        if role == Qt.ForegroundRole and index.column() == risk_col:
            metrics = self._student_metrics(student)
            risk = metrics["risk"]
            if risk["is_at_risk"]:
                return QColor(tokens["danger"])
            return QColor(tokens["success_text"])

        if role == Qt.ForegroundRole and index.column() == average_col:
            metrics = self._student_metrics(student)
            if metrics["average"] < self._passing_grade:
                return QColor(tokens["danger"])
            return QColor(tokens["success_text"])

        if role == Qt.ForegroundRole and index.column() == adjusted_average_col:
            metrics = self._student_metrics(student)
            if metrics["adjusted_average"] < self._passing_grade:
                return QColor(tokens["danger"])
            return QColor(tokens["success_text"])

        if role == Qt.ForegroundRole and activity_start <= index.column() < category_avg_start:
            activity = self._visible_activities[index.column() - activity_start]
            grade = self._grade_lookup.get((student.id, activity.id))
            if grade and grade.status == "missing":
                return QColor(tokens["danger"])
            if not grade or grade.status == "pending" or grade.score is None:
                return QColor(tokens["warning_text"])

        if role == Qt.TextAlignmentRole and index.column() >= 1:
            return Qt.AlignCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.ToolTipRole:
                if section == 0:
                    return "Alumno"
                category_avg_start = 1 + len(self._visible_activities)
                average_col = category_avg_start + len(self._active_categories)
                adjustment_col = average_col + 1
                adjusted_average_col = average_col + 2
                if 1 <= section < category_avg_start:
                    activity = self._visible_activities[section - 1]
                    return f"Actividad calificada sobre {activity.max_score:.1f}."
                if category_avg_start <= section < average_col:
                    category = self._active_categories[section - category_avg_start]
                    if category.category_mode == "deduction":
                        return "Haz clic para registrar o editar el descuento manual de este alumno."
                    return f"Puntos actuales de {category.name} para cada alumno."
                if section == average_col:
                    return "Resultado del periodo antes de ajustes manuales."
                if section == adjustment_col:
                    return "Puntos extra o descuentos manuales sobre el resultado del periodo."
                if section == adjusted_average_col:
                    return "Resultado del periodo despues de ajustes manuales."
                if section == average_col + 3:
                    return "Cantidad de capturas pendientes o sin resolver."
                return "Estado de riesgo academico del alumno."
            if role != Qt.DisplayRole:
                return None
            if section == 0:
                return "Alumno"
            category_avg_start = 1 + len(self._visible_activities)
            average_col = category_avg_start + len(self._active_categories)
            adjustment_col = average_col + 1
            adjusted_average_col = average_col + 2
            if 1 <= section < category_avg_start:
                activity = self._visible_activities[section - 1]
                return activity.name
            if category_avg_start <= section < average_col:
                category = self._active_categories[section - category_avg_start]
                return category.name
            if section == average_col:
                return "Periodo"
            if section == adjustment_col:
                return "Ajuste"
            if section == adjusted_average_col:
                return "Periodo ajust."
            if section == average_col + 3:
                return "Pend."
            return "Riesgo"
        return str(section + 1)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if 1 <= index.column() < 1 + len(self._visible_activities):
            flags |= Qt.ItemIsEditable
        category_avg_start = 1 + len(self._visible_activities)
        average_col = category_avg_start + len(self._active_categories)
        if category_avg_start <= index.column() < average_col:
            category = self._active_categories[index.column() - category_avg_start]
            if category.category_mode == "deduction":
                flags |= Qt.ItemIsEditable
        if index.column() == average_col + 1:
            flags |= Qt.ItemIsEditable
        return flags

    def _activity_category(self, activity: Activity) -> EvaluationCategory | None:
        for category in self._categories:
            if category.id == activity.category_id:
                return category
        return None

    def _category_deduction_entries(self, student_id: int, category_id: int) -> list[StudentCategoryDeductionEntry]:
        return list(self._category_deduction_lookup.get((student_id, category_id), []))

    def _category_deduction_total(self, student_id: int, category_id: int) -> float:
        return round(
            sum(item.points for item in self._category_deduction_entries(student_id, category_id)),
            2,
        )

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid():
            return False
        category_avg_start = 1 + len(self._visible_activities)
        average_col = category_avg_start + len(self._active_categories)
        if category_avg_start <= index.column() < average_col:
            category = self._active_categories[index.column() - category_avg_start]
            if category.category_mode == "deduction":
                return self._set_category_deduction(index, value)
        if index.column() == average_col + 1:
            return self._set_adjustment(index, value)
        if not (1 <= index.column() < 1 + len(self._visible_activities)):
            return False

        student = self._students[index.row()]
        activity = self._visible_activities[index.column() - 1]
        try:
            score = self._normalize_score(value, activity.max_score)
        except ValueError:
            return False

        status = "graded" if score is not None else "pending"
        self._save_callback(activity.id, student.id, score, status)
        self._grade_lookup[(student.id, activity.id)] = GradeEntry(
            id=None,
            activity_id=activity.id,
            student_id=student.id,
            score=score,
            status=status,
            comment="",
        )
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        row = index.row()
        self.dataChanged.emit(
            self.index(row, category_avg_start),
            self.index(row, average_col + 4),
            [Qt.DisplayRole, Qt.ToolTipRole],
        )
        return True

    def apply_text_value(self, index: QModelIndex, raw_value: str) -> bool:
        if not index.isValid():
            return False
        text = raw_value.strip()
        if text == "":
            return self.setData(index, None, Qt.EditRole)

        normalized = text.upper()
        if normalized == "P":
            return self.apply_status(index, "pending")
        if normalized in {"M", "NE"}:
            return self.apply_status(index, "missing")

        return self.setData(index, text, Qt.EditRole)

    @staticmethod
    def _normalize_score(value, max_score: float) -> float | None:
        if value in ("", None):
            return None
        score = float(value)
        if score < 0 or score > max_score:
            raise ValueError("Score fuera de rango")
        return round(score, 1)

    def apply_status(self, index: QModelIndex, status: str) -> bool:
        if not index.isValid():
            return False
        if not (1 <= index.column() < 1 + len(self._visible_activities)):
            return False
        if status not in {"pending", "missing"}:
            return False

        student = self._students[index.row()]
        activity = self._visible_activities[index.column() - 1]
        self._save_callback(activity.id, student.id, None, status)
        self._grade_lookup[(student.id, activity.id)] = GradeEntry(
            id=None,
            activity_id=activity.id,
            student_id=student.id,
            score=None,
            status=status,
            comment="",
        )
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.ToolTipRole, Qt.ForegroundRole])
        row = index.row()
        category_avg_start = 1 + len(self._visible_activities)
        average_col = category_avg_start + len(self._active_categories)
        self.dataChanged.emit(
            self.index(row, category_avg_start),
            self.index(row, average_col + 4),
            [Qt.DisplayRole, Qt.ToolTipRole],
        )
        return True

    def _set_category_deduction(self, index: QModelIndex, value) -> bool:
        payload = value if isinstance(value, dict) else {}
        student = self._students[index.row()]
        category_avg_start = 1 + len(self._visible_activities)
        category = self._active_categories[index.column() - category_avg_start]
        if category.category_mode != "deduction":
            return False
        try:
            points = round(float(payload.get("points", 0) or 0), 2)
        except (TypeError, ValueError):
            return False
        note = str(payload.get("note", "") or "").strip()
        current_total = self._category_deduction_total(student.id, category.id)
        remaining_points = round(max(0.0, category.weight_percent - current_total), 2)
        if points <= 0 or points > remaining_points:
            return False
        self._save_category_deduction_callback(category.id, student.id, points, note)
        self._category_deduction_lookup.setdefault((student.id, category.id), []).insert(
            0,
            StudentCategoryDeductionEntry(
                id=None,
                category_id=category.id,
                student_id=student.id,
                points=points,
                note=note,
                created_at="",
            ),
        )
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole])
        average_col = category_avg_start + len(self._active_categories)
        self.dataChanged.emit(
            self.index(index.row(), category_avg_start),
            self.index(index.row(), average_col + 4),
            [Qt.DisplayRole, Qt.ToolTipRole, Qt.ForegroundRole],
        )
        return True

    def _set_adjustment(self, index: QModelIndex, value) -> bool:
        if self._group_id is None:
            return False
        student = self._students[index.row()]
        try:
            points = round(float(value or 0), 2)
        except (TypeError, ValueError):
            return False
        self._save_adjustment_callback(self._group_id, student.id, points)
        self._adjustment_lookup[student.id] = StudentAdjustment(
            id=None,
            group_id=self._group_id,
            student_id=student.id,
            points=points,
            note="",
        )
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        row = index.row()
        category_avg_start = 1 + len(self._visible_activities)
        average_col = category_avg_start + len(self._active_categories)
        self.dataChanged.emit(
            self.index(row, average_col + 1),
            self.index(row, average_col + 4),
            [Qt.DisplayRole, Qt.ToolTipRole, Qt.ForegroundRole],
        )
        return True

    def _student_metrics(self, student: Student) -> dict:
        category_averages: dict[int, float] = {}
        category_points: dict[int, float] = {}
        unresolved_count = 0
        missing_count = 0

        for category in self._active_categories:
            scores: list[float] = []
            max_scores: list[float] = []
            if category.category_mode == "deduction":
                deduction_total = self._category_deduction_total(student.id, category.id)
                available_points = round(category.weight_percent, 2)
                if available_points <= 0:
                    category_average = 0.0
                    contribution_points = 0.0
                else:
                    remaining = max(0.0, available_points - deduction_total)
                    category_average = round((remaining / available_points) * 100.0, 2)
                    contribution_points = round(remaining, 2)
            else:
                for activity in self._activities:
                    if activity.category_id != category.id:
                        continue
                    grade = self._grade_lookup.get((student.id, activity.id))
                    if grade and grade.score is not None:
                        scores.append(grade.score)
                        max_scores.append(activity.max_score)
                    else:
                        unresolved_count += 1
                        if grade and grade.status == "missing":
                            missing_count += 1
                category_average = GradeCalculator.calculate_category_average(scores, max_scores)
                contribution_points = round(category_average * (category.weight_percent / 100.0), 2)
            category_averages[category.id] = category_average
            category_points[category.id] = contribution_points

        average = round(sum(category_points.values()), 2) if self._active_categories else 0.0
        adjustment = self._adjustment_lookup.get(student.id)
        adjustment_points = adjustment.points if adjustment else 0.0
        adjusted_average = round(max(0.0, min(100.0, average + adjustment_points)), 2)
        risk = GradebookService.build_risk_result(
            adjusted_average,
            self._passing_grade,
            missing_count,
            unresolved_count,
        )
        return {
            "average": average,
            "adjusted_average": adjusted_average,
            "adjustment_points": adjustment_points,
            "unresolved_count": unresolved_count,
            "missing_count": missing_count,
            "risk": risk,
            "category_averages": category_averages,
            "category_points": category_points,
        }
