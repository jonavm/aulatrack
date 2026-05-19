from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.entities import Student
from services.student_profile_service import StudentProfileService


class StudentProfileDialog(QDialog):
    def __init__(self, group_id: int, student: Student, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.student = student
        self.group_id = group_id
        self.profile_service = StudentProfileService()
        self.setWindowTitle("Ficha del alumno")
        self.setModal(True)
        self.resize(760, 620)
        self._build_ui()
        self._load_profile()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel("Ficha del alumno")
        title.setObjectName("SectionTitle")
        self.subtitle = QLabel("")
        self.subtitle.setObjectName("Caption")

        stats_grid = QGridLayout()
        stats_grid.setSpacing(12)
        self.stat_labels: dict[str, QLabel] = {}
        for index, (key, label_text) in enumerate(
            [
                ("final", "Promedio final"),
                ("attendance", "Asistencia"),
                ("risk", "Riesgo"),
                ("pending", "Pendientes"),
            ]
        ):
            card = QFrame()
            card.setObjectName("Panel")
            card_layout = QVBoxLayout(card)
            label = QLabel(label_text)
            value = QLabel("--")
            value.setObjectName("SectionTitle")
            self.stat_labels[key] = value
            card_layout.addWidget(label)
            card_layout.addWidget(value)
            stats_grid.addWidget(card, 0, index)

        body = QHBoxLayout()
        body.setSpacing(16)

        left_panel = QFrame()
        left_panel.setObjectName("Panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(12)
        left_title = QLabel("Desempeño academico")
        left_title.setObjectName("SectionTitle")
        self.grade_breakdown = QTextEdit()
        self.grade_breakdown.setReadOnly(True)
        self.grade_breakdown.setMinimumHeight(220)
        left_layout.addWidget(left_title)
        left_layout.addWidget(self.grade_breakdown)

        right_panel = QFrame()
        right_panel.setObjectName("Panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(12)
        right_title = QLabel("Asistencia reciente")
        right_title.setObjectName("SectionTitle")
        self.attendance_breakdown = QTextEdit()
        self.attendance_breakdown.setReadOnly(True)
        self.attendance_breakdown.setMinimumHeight(220)
        right_layout.addWidget(right_title)
        right_layout.addWidget(self.attendance_breakdown)

        body.addWidget(left_panel, 1)
        body.addWidget(right_panel, 1)

        notes_panel = QFrame()
        notes_panel.setObjectName("Panel")
        notes_layout = QVBoxLayout(notes_panel)
        notes_layout.setContentsMargins(14, 14, 14, 14)
        notes_layout.setSpacing(12)
        notes_title = QLabel("Observaciones")
        notes_title.setObjectName("SectionTitle")
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Escribe observaciones importantes del alumno.")
        self.notes_input.setMinimumHeight(140)
        notes_layout.addWidget(notes_title)
        notes_layout.addWidget(self.notes_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        buttons.accepted.connect(self._save_notes)
        buttons.rejected.connect(self.reject)

        root.addWidget(title)
        root.addWidget(self.subtitle)
        root.addLayout(stats_grid)
        root.addLayout(body)
        root.addWidget(notes_panel)
        root.addWidget(buttons)

    def _load_profile(self) -> None:
        profile = self.profile_service.build_profile(self.group_id, self.student.id)
        if profile is None:
            QMessageBox.warning(self, "Alumno", "No pude cargar la ficha del alumno.")
            self.reject()
            return

        student = profile["student"]
        group = profile["group"]
        grade_summary = profile["grade_summary"]
        attendance_summary = profile["attendance_summary"]

        school_text = group.school_name or "Sin escuela"
        self.subtitle.setText(f"{student.roster_name} | {group.display_name} | {school_text}")

        self.stat_labels["final"].setText(f'{grade_summary["adjusted_average"]:.2f}')
        self.stat_labels["attendance"].setText(f'{attendance_summary["attendance_rate"]:.1f}%')
        self.stat_labels["risk"].setText("Si" if grade_summary["risk"]["is_at_risk"] else "No")
        self.stat_labels["pending"].setText(str(grade_summary["unresolved_count"]))

        grade_lines = []
        for row in grade_summary["categories"]:
            if row["mode"] == "deduction":
                grade_lines.append(
                    f'{row["name"]}: {row["points"]:.2f} pts vigentes  |  {row["weight_percent"]:.0f} pts del criterio  |  {row["deduction_points"]:.2f} descontados en {row.get("deduction_count", 0)} registro(s)'
                )
                if row["deduction_note"]:
                    grade_lines.append(f'Ultimo motivo: {row["deduction_note"]}')
            else:
                grade_lines.append(
                    f'{row["name"]}: {row["average"]:.2f}/100  |  aporta {row["points"]:.2f} pts  |  {row["activity_count"]} actividades'
                )
        if grade_summary["adjustment_points"]:
            grade_lines.append("")
            grade_lines.append(f'Ajuste final: {grade_summary["adjustment_points"]:+.2f}')
        if grade_summary["risk"]["reasons"]:
            grade_lines.append("")
            grade_lines.append("Alertas:")
            for reason in grade_summary["risk"]["reasons"]:
                grade_lines.append(f"- {reason}")
        self.grade_breakdown.setPlainText("\n".join(grade_lines) or "Sin datos de calificaciones.")

        attendance_lines = [
            f'Total de dias registrados: {attendance_summary["total_sessions"]}',
            f'Asistencias: {attendance_summary["present_count"]}',
            f'Faltas: {attendance_summary["absent_count"]}',
            f'Retardos: {attendance_summary["late_count"]}',
            f'Justificadas: {attendance_summary["justified_count"]}',
            "",
            "Ultimos registros:",
        ]
        status_labels = {
            "present": "Asistencia",
            "absent": "Falta",
            "late": "Retardo",
            "justified": "Justificada",
        }
        for row in attendance_summary["recent"]:
            attendance_lines.append(f'{row["date"]}: {status_labels.get(row["status"], "Asistencia")}')
        self.attendance_breakdown.setPlainText("\n".join(attendance_lines))
        self.notes_input.setPlainText(student.notes)

    def _save_notes(self) -> None:
        try:
            self.profile_service.save_notes(self.student.id, self.notes_input.toPlainText())
        except ValueError as error:
            QMessageBox.warning(self, "Observaciones", str(error))
            return
        self.accept()
