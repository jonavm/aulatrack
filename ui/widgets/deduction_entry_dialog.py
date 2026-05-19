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


class DeductionEntryDialog(QDialog):
    def __init__(
        self,
        *,
        student_name: str,
        criterion_name: str,
        max_points: float,
        entries: list[dict],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.max_points = round(max_points, 2)
        self.entries = entries
        self.setWindowTitle("Descuentos del alumno")
        self.setModal(True)
        self.resize(560, 520)

        total_discount = round(sum(float(item.get("points", 0) or 0) for item in entries), 2)
        remaining_points = max(0.0, round(self.max_points - total_discount, 2))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel(student_name)
        title.setObjectName("SectionTitle")

        subtitle = QLabel(
            f"{criterion_name}: registra descuentos individuales para este alumno. "
            f"Llevas {total_discount:.1f} pts descontados de {self.max_points:.1f}."
        )
        subtitle.setObjectName("Caption")
        subtitle.setWordWrap(True)

        summary = QFrame()
        summary.setObjectName("CalloutPanel")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(12, 10, 12, 10)
        summary_layout.setSpacing(18)
        self.total_label = QLabel(f"Descontado: {total_discount:.1f}")
        self.total_label.setObjectName("StatusValue")
        self.remaining_label = QLabel(f"Disponible: {remaining_points:.1f}")
        self.remaining_label.setObjectName("StatusText")
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.remaining_label)
        summary_layout.addStretch(1)

        history_title = QLabel("Registro de descuentos")
        history_title.setObjectName("StatusLabel")

        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Fecha", "Descuento", "Motivo"])
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionMode(QTableWidget.NoSelection)
        self.history_table.setFocusPolicy(Qt.NoFocus)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.history_table.setMinimumHeight(180)
        self._populate_history()

        add_title = QLabel("Agregar nuevo descuento")
        add_title.setObjectName("StatusLabel")

        self.points_input = QDoubleSpinBox()
        self.points_input.setRange(0.0, remaining_points)
        self.points_input.setDecimals(1)
        self.points_input.setSingleStep(1.0)
        self.points_input.setValue(0.0)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Escribe el motivo del descuento")
        self.note_input.setFixedHeight(110)

        add_form = QVBoxLayout()
        add_form.setSpacing(10)

        discount_row = QHBoxLayout()
        discount_label = QLabel("Descuento")
        discount_label.setObjectName("StatusText")
        discount_row.addWidget(discount_label)
        discount_row.addWidget(self.points_input, 1)

        self.limit_label = QLabel(f"Puedes agregar hasta {remaining_points:.1f} puntos en este momento.")
        self.limit_label.setObjectName("Caption")
        self.limit_label.setWordWrap(True)

        add_form.addLayout(discount_row)
        add_form.addWidget(self.note_input)
        add_form.addWidget(self.limit_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Agregar descuento")
        buttons.button(QDialogButtonBox.Cancel).setText("Cerrar")
        buttons.accepted.connect(self._handle_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(summary)
        layout.addWidget(history_title)
        layout.addWidget(self.history_table)
        layout.addWidget(add_title)
        layout.addLayout(add_form)
        layout.addWidget(buttons)

    def _populate_history(self) -> None:
        self.history_table.setRowCount(len(self.entries))
        if not self.entries:
            self.history_table.setRowCount(1)
            empty = QTableWidgetItem("Sin descuentos registrados")
            empty.setFlags(Qt.ItemIsEnabled)
            self.history_table.setItem(0, 0, empty)
            self.history_table.setSpan(0, 0, 1, 3)
            return

        for row, entry in enumerate(self.entries):
            date_item = QTableWidgetItem(self._format_timestamp(entry.get("created_at", "")))
            points_item = QTableWidgetItem(f'-{float(entry.get("points", 0) or 0):.1f}')
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
            QMessageBox.warning(self, "Descuento requerido", "Escribe cuántos puntos vas a descontar.")
            return
        if not self.note_input.toPlainText().strip():
            QMessageBox.warning(self, "Motivo requerido", "Escribe el motivo del descuento.")
            return
        self.accept()

    def get_payload(self) -> dict:
        return {
            "points": round(self.points_input.value(), 2),
            "note": self.note_input.toPlainText().strip(),
        }
