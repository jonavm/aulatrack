from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AdjustmentDialog(QDialog):
    def __init__(
        self,
        *,
        student_name: str,
        current_points: float,
        entries: list[dict],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.entries = entries
        self.setWindowTitle("Puntos extra del alumno")
        self.setModal(True)
        self.resize(560, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel(student_name)
        title.setObjectName("SectionTitle")

        subtitle = QLabel(
            "Registra puntos extra aparte de los criterios para este alumno. "
            f"Total acumulado: +{current_points:.2f} pts."
        )
        subtitle.setObjectName("Caption")
        subtitle.setWordWrap(True)

        summary = QFrame()
        summary.setObjectName("CalloutPanel")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(12, 10, 12, 10)
        summary_layout.setSpacing(18)
        current_label = QLabel(f"Extra acumulado: +{current_points:.2f}")
        current_label.setObjectName("StatusValue")
        range_label = QLabel("Solo puntos positivos por registro | Maximo 10.0")
        range_label.setObjectName("StatusText")
        summary_layout.addWidget(current_label)
        summary_layout.addWidget(range_label)
        summary_layout.addStretch(1)

        history_title = QLabel("Registro de puntos extra")
        history_title.setObjectName("StatusLabel")

        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Fecha", "Puntos", "Motivo"])
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionMode(QTableWidget.NoSelection)
        self.history_table.setFocusPolicy(Qt.NoFocus)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.history_table.setMinimumHeight(180)
        self._populate_history()

        form_title = QLabel("Agregar nuevos puntos extra")
        form_title.setObjectName("StatusLabel")

        self.points_input = QDoubleSpinBox()
        self.points_input.setRange(0.0, 10.0)
        self.points_input.setDecimals(2)
        self.points_input.setSingleStep(0.5)
        self.points_input.setValue(0.0)

        points_row = QHBoxLayout()
        points_label = QLabel("Puntos extra")
        points_label.setObjectName("StatusText")
        points_row.addWidget(points_label)
        points_row.addWidget(self.points_input, 1)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Escribe el motivo de los puntos extra")
        self.note_input.setFixedHeight(110)

        note_helper = QLabel(
            "Cada registro se suma al total del alumno y queda guardado en el historial."
        )
        note_helper.setObjectName("Caption")
        note_helper.setWordWrap(True)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Guardar puntos extra")
        buttons.button(QDialogButtonBox.Cancel).setText("Cerrar")
        buttons.accepted.connect(self._handle_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(summary)
        layout.addWidget(history_title)
        layout.addWidget(self.history_table)
        layout.addWidget(form_title)
        layout.addLayout(points_row)
        layout.addWidget(self.note_input)
        layout.addWidget(note_helper)
        layout.addStretch(1)
        layout.addWidget(buttons)

    def _populate_history(self) -> None:
        self.history_table.setRowCount(len(self.entries))
        if not self.entries:
            self.history_table.setRowCount(1)
            empty = QTableWidgetItem("Sin puntos extra registrados")
            empty.setFlags(Qt.ItemIsEnabled)
            self.history_table.setItem(0, 0, empty)
            self.history_table.setSpan(0, 0, 1, 3)
            return

        for row, entry in enumerate(self.entries):
            date_item = QTableWidgetItem(self._format_timestamp(entry.get("created_at", "")))
            points_item = QTableWidgetItem(f'+{float(entry.get("points", 0) or 0):.2f}')
            note_item = QTableWidgetItem(str(entry.get("note", "") or ""))
            for item in (date_item, points_item, note_item):
                item.setFlags(Qt.ItemIsEnabled)
            self.history_table.setItem(row, 0, date_item)
            self.history_table.setItem(row, 1, points_item)
            self.history_table.setItem(row, 2, note_item)

    @staticmethod
    def _format_timestamp(raw_value: str) -> str:
        if not raw_value:
            return "-"
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(raw_value, fmt).strftime("%d/%m/%Y %H:%M")
            except ValueError:
                continue
        return raw_value

    def _handle_accept(self) -> None:
        if self.points_input.value() <= 0:
            QMessageBox.warning(self, "Puntos requeridos", "Escribe cuantos puntos extra vas a agregar.")
            return
        if not self.note_input.toPlainText().strip():
            QMessageBox.warning(self, "Motivo requerido", "Escribe el motivo de los puntos extra.")
            return
        self.accept()

    def get_payload(self) -> dict:
        return {
            "points": round(self.points_input.value(), 2),
            "note": self.note_input.toPlainText().strip(),
        }
