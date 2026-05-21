from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextBrowser,
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
        self._apply_initial_size()
        self._build_ui()
        self._load_profile()

    def _apply_initial_size(self) -> None:
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            self.resize(920, 700)
            self.setMinimumSize(760, 560)
            return

        available = screen.availableGeometry()
        width = min(980, max(760, available.width() - 80))
        height = min(760, max(560, available.height() - 80))
        self.resize(width, height)
        self.setMinimumSize(760, 560)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        content = QVBoxLayout(container)
        content.setContentsMargins(20, 20, 20, 20)
        content.setSpacing(16)

        title = QLabel("Ficha del alumno")
        title.setObjectName("SectionTitle")
        self.subtitle = QLabel("")
        self.subtitle.setObjectName("Caption")
        self.subtitle.setWordWrap(True)

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
            card_layout.setContentsMargins(18, 16, 18, 16)
            card_layout.setSpacing(6)

            label = QLabel(label_text)
            label.setObjectName("Caption")
            value = QLabel("--")
            value.setObjectName("SectionTitle")
            helper = QLabel("")
            helper.setObjectName("StatusText")
            helper.setWordWrap(True)

            self.stat_labels[key] = value
            self.stat_labels[f"{key}_helper"] = helper

            card_layout.addWidget(label)
            card_layout.addWidget(value)
            card_layout.addWidget(helper)
            stats_grid.addWidget(card, 0, index)

        content_splitter = QSplitter(Qt.Vertical)
        content_splitter.setChildrenCollapsible(False)

        left_panel = QFrame()
        left_panel.setObjectName("Panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)
        left_title_row = QHBoxLayout()
        left_title = QLabel("Desempeno academico")
        left_title.setObjectName("SectionTitle")
        self.risk_badge = QLabel("")
        self.risk_badge.setObjectName("BadgeSuccess")
        left_title_row.addWidget(left_title)
        left_title_row.addStretch(1)
        left_title_row.addWidget(self.risk_badge)
        self.grade_breakdown = QTextBrowser()
        self.grade_breakdown.setOpenExternalLinks(False)
        self.grade_breakdown.setMinimumHeight(220)
        self.grade_breakdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addLayout(left_title_row)
        left_layout.addWidget(self.grade_breakdown)

        right_panel = QFrame()
        right_panel.setObjectName("Panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)
        right_title = QLabel("Asistencia reciente")
        right_title.setObjectName("SectionTitle")
        self.attendance_breakdown = QTextBrowser()
        self.attendance_breakdown.setOpenExternalLinks(False)
        self.attendance_breakdown.setMinimumHeight(220)
        self.attendance_breakdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(right_title)
        right_layout.addWidget(self.attendance_breakdown)

        body_widget = QWidget()
        body = QHBoxLayout(body_widget)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(16)
        body.addWidget(left_panel, 1)
        body.addWidget(right_panel, 1)

        notes_panel = QFrame()
        notes_panel.setObjectName("Panel")
        notes_layout = QVBoxLayout(notes_panel)
        notes_layout.setContentsMargins(16, 16, 16, 16)
        notes_layout.setSpacing(10)
        notes_title = QLabel("Observaciones")
        notes_title.setObjectName("SectionTitle")
        notes_helper = QLabel("Espacio para notas importantes, seguimiento o acuerdos con el alumno.")
        notes_helper.setObjectName("StatusText")
        notes_helper.setWordWrap(True)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Escribe observaciones importantes del alumno.")
        self.notes_input.setMinimumHeight(110)
        self.notes_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        notes_layout.addWidget(notes_title)
        notes_layout.addWidget(notes_helper)
        notes_layout.addWidget(self.notes_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        buttons.accepted.connect(self._save_notes)
        buttons.rejected.connect(self.reject)

        content.addWidget(title)
        content.addWidget(self.subtitle)
        content.addLayout(stats_grid)
        content_splitter.addWidget(body_widget)
        content_splitter.addWidget(notes_panel)
        content_splitter.setStretchFactor(0, 4)
        content_splitter.setStretchFactor(1, 2)
        content_splitter.setSizes([430, 210])
        content.addWidget(content_splitter, 1)
        content.addWidget(buttons)

        scroll.setWidget(container)
        root.addWidget(scroll)

    def _set_badge_state(self, text: str, positive: bool) -> None:
        self.risk_badge.setText(text)
        self.risk_badge.setObjectName("BadgeSuccess" if positive else "BadgeWarning")
        self.risk_badge.style().unpolish(self.risk_badge)
        self.risk_badge.style().polish(self.risk_badge)

    @staticmethod
    def _render_section(title: str, rows: list[str]) -> str:
        if not rows:
            return (
                f"<div style='margin-top:12px;'>"
                f"<div style='font-weight:700; font-size:14px; margin-bottom:8px;'>{escape(title)}</div>"
                f"<div style='padding:10px 12px; border:1px dashed #D6DFEA; border-radius:12px; color:#6E7C91;'>Sin datos.</div>"
                f"</div>"
            )

        items = "".join(rows)
        return (
            f"<div style='margin-top:12px;'>"
            f"<div style='font-weight:700; font-size:14px; margin-bottom:8px;'>{escape(title)}</div>"
            f"{items}"
            f"</div>"
        )

    @staticmethod
    def _render_item(title: str, detail: str, tone: str = "#274C77") -> str:
        return (
            "<div style='margin-bottom:8px; padding:10px 12px; border:1px solid #D6DFEA; "
            "border-radius:12px; background:#FFFFFF;'>"
            f"<div style='font-weight:700; color:#142033; margin-bottom:4px;'>{escape(title)}</div>"
            f"<div style='color:{tone};'>{escape(detail)}</div>"
            "</div>"
        )

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
        self.stat_labels["final_helper"].setText("Resultado final del periodo.")
        self.stat_labels["attendance"].setText(f'{attendance_summary["attendance_rate"]:.1f}%')
        self.stat_labels["attendance_helper"].setText(f'{attendance_summary["present_count"]} asistencias registradas.')
        self.stat_labels["risk"].setText("Si" if grade_summary["risk"]["is_at_risk"] else "No")
        self.stat_labels["risk_helper"].setText("Requiere seguimiento." if grade_summary["risk"]["is_at_risk"] else "Sin alertas.")
        self.stat_labels["pending"].setText(str(grade_summary["unresolved_count"]))
        self.stat_labels["pending_helper"].setText("Actividades pendientes o sin captura.")

        self._set_badge_state(
            "En riesgo" if grade_summary["risk"]["is_at_risk"] else "Estable",
            positive=not grade_summary["risk"]["is_at_risk"],
        )

        self.grade_breakdown.setHtml(self._build_grade_html(grade_summary))
        self.attendance_breakdown.setHtml(self._build_attendance_html(attendance_summary))
        self.notes_input.setPlainText(student.notes)

    def _build_grade_html(self, grade_summary: dict) -> str:
        criteria_rows = []
        for row in grade_summary["categories"]:
            if row["mode"] == "deduction":
                title = f'{row["name"]}: {row["points"]:.2f} pts vigentes'
                detail = (
                    f'Base {row["weight_percent"]:.0f} pts | '
                    f'Descontados {row["deduction_points"]:.2f} | '
                    f'{row.get("deduction_count", 0)} registro(s)'
                )
                if row["deduction_note"]:
                    detail += f' | Ultimo motivo: {row["deduction_note"]}'
                tone = "#B7791F"
            else:
                title = f'{row["name"]}: {row["average"]:.2f}/100'
                detail = (
                    f'Aporta {row["points"]:.2f} pts | '
                    f'Peso {row["weight_percent"]:.0f} | '
                    f'{row["activity_count"]} actividad(es)'
                )
                tone = "#274C77"
            criteria_rows.append(self._render_item(title, detail, tone))

        graded_rows = []
        for activity in grade_summary.get("graded_activities", []):
            title = f'{activity["activity_name"]} | {activity["score"]:.1f}/{activity["max_score"]:.1f}'
            detail = activity["category_name"]
            if activity["due_date"]:
                detail += f' | Fecha: {activity["due_date"]}'
            graded_rows.append(self._render_item(title, detail, "#2F855A"))

        pending_rows = []
        for activity in grade_summary.get("pending_activities", []):
            status_text = "No entregada" if activity["status"] == "missing" else "Pendiente"
            title = f'{activity["activity_name"]} | {status_text}'
            detail = activity["category_name"]
            if activity["due_date"]:
                detail += f' | Fecha: {activity["due_date"]}'
            pending_rows.append(self._render_item(title, detail, "#C05666"))

        if grade_summary["adjustment_points"]:
            criteria_rows.append(
                self._render_item(
                    "Ajuste final aplicado",
                    f'{grade_summary["adjustment_points"]:+.2f} pts sobre el resultado del periodo.',
                    "#274C77",
                )
            )

        if grade_summary["risk"]["reasons"]:
            pending_rows.append(
                self._render_item(
                    "Alertas academicas",
                    " | ".join(grade_summary["risk"]["reasons"]),
                    "#C05666",
                )
            )

        return (
            "<div style='font-family: Segoe UI; font-size: 13px;'>"
            f"{self._render_section('Resumen por criterio', criteria_rows)}"
            f"{self._render_section('Calificaciones registradas', graded_rows)}"
            f"{self._render_section('Pendientes del alumno', pending_rows)}"
            "</div>"
        )

    def _build_attendance_html(self, attendance_summary: dict) -> str:
        summary_rows = [
            self._render_item(
                "Asistencia efectiva",
                f'{attendance_summary["attendance_rate"]:.1f}% del periodo registrado.',
                "#2F855A",
            ),
            self._render_item(
                "Dias registrados",
                f'{attendance_summary["total_sessions"]} sesiones capturadas.',
                "#274C77",
            ),
            self._render_item(
                "Incidencias",
                (
                    f'Faltas: {attendance_summary["absent_count"]} | '
                    f'Retardos: {attendance_summary["late_count"]} | '
                    f'Justificadas: {attendance_summary["justified_count"]}'
                ),
                "#274C77",
            ),
        ]

        recent_rows = []
        status_labels = {
            "present": ("Asistencia", "#2F855A"),
            "absent": ("Falta", "#C05666"),
            "late": ("Retardo", "#B7791F"),
            "justified": ("Justificada", "#274C77"),
        }
        for row in attendance_summary["recent"]:
            status_text, tone = status_labels.get(row["status"], ("Asistencia", "#2F855A"))
            recent_rows.append(self._render_item(row["date"], status_text, tone))

        return (
            "<div style='font-family: Segoe UI; font-size: 13px;'>"
            f"{self._render_section('Resumen', summary_rows)}"
            f"{self._render_section('Ultimos registros', recent_rows)}"
            "</div>"
        )

    def _save_notes(self) -> None:
        try:
            self.profile_service.save_notes(self.student.id, self.notes_input.toPlainText())
        except ValueError as error:
            QMessageBox.warning(self, "Observaciones", str(error))
            return
        self.accept()
