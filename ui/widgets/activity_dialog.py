from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from models.entities import Activity, EvaluationCategory


class ActivityDialog(QDialog):
    def __init__(
        self,
        categories: list[EvaluationCategory],
        parent: QWidget | None = None,
        activity: Activity | None = None,
        preferred_category_id: int | None = None,
    ) -> None:
        super().__init__(parent)
        self.categories = categories
        self.preferred_category_id = preferred_category_id
        self.setWindowTitle("Editar actividad" if activity else "Nueva actividad")
        self.setModal(True)
        self.resize(430, 340)
        self._build_ui()
        if activity:
            self._fill_form(activity)
        elif preferred_category_id is not None:
            self._select_preferred_category(preferred_category_id)
        self._refresh_copy()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        self.title_label = QLabel(self.windowTitle())
        self.title_label.setObjectName("SectionTitle")
        self.subtitle_label = QLabel("Crea una actividad dentro de un criterio de promedio.")
        self.subtitle_label.setObjectName("Caption")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.category_input = QComboBox()
        for category in self.categories:
            self.category_input.addItem(category.name, category)
        self.category_input.currentIndexChanged.connect(self._refresh_copy)

        self.name_input = QLineEdit()
        self.max_score_input = QDoubleSpinBox()
        self.max_score_input.setRange(0.1, 1000)
        self.max_score_input.setDecimals(1)
        self.max_score_input.setValue(100.0)
        self.order_input = QSpinBox()
        self.order_input.setRange(0, 999)
        self.due_date_input = QLineEdit()
        self.due_date_input.setPlaceholderText("Opcional. Ej. 2026-05-20")
        self.risk_input = QCheckBox("Considerar en deteccion de riesgo")
        self.risk_input.setChecked(True)
        self.name_label = QLabel("Nombre")
        self.max_score_label = QLabel("Puntuacion maxima")
        self.date_label = QLabel("Fecha")

        form.addRow("Criterio", self.category_input)
        form.addRow(self.name_label, self.name_input)
        form.addRow(self.max_score_label, self.max_score_input)
        form.addRow("Orden", self.order_input)
        form.addRow(self.date_label, self.due_date_input)
        form.addRow("", self.risk_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._handle_accept)
        buttons.rejected.connect(self.reject)

        root.addWidget(self.title_label)
        root.addWidget(self.subtitle_label)
        root.addLayout(form)
        root.addStretch(1)
        root.addWidget(buttons)

    def _current_category(self) -> EvaluationCategory | None:
        return self.category_input.currentData()

    def _refresh_copy(self) -> None:
        category = self._current_category()
        deduction_mode = bool(category and category.category_mode == "deduction")
        is_editing = "Editar" in self.windowTitle()
        if deduction_mode:
            self.setWindowTitle("Editar criterio de descuento" if is_editing else "Nuevo criterio de descuento")
            self.title_label.setText(self.windowTitle())
            self.subtitle_label.setText("Define un criterio disponible para descontar puntos manualmente desde el libro de alumnos.")
            self.name_label.setText("Criterio")
            self.max_score_label.setText("Descuento maximo")
            self.date_label.setText("Fecha")
            self.risk_input.setText("Considerar este criterio en deteccion de riesgo")
        else:
            self.setWindowTitle("Editar actividad" if is_editing else "Nueva actividad")
            self.title_label.setText(self.windowTitle())
            self.subtitle_label.setText("Crea una actividad dentro de un criterio de promedio.")
            self.name_label.setText("Nombre")
            self.max_score_label.setText("Puntuacion maxima")
            self.date_label.setText("Fecha")
            self.risk_input.setText("Considerar en deteccion de riesgo")

    def _fill_form(self, activity: Activity) -> None:
        self.name_input.setText(activity.name)
        self.max_score_input.setValue(activity.max_score)
        self.order_input.setValue(activity.sort_order)
        self.due_date_input.setText(activity.due_date or "")
        self.risk_input.setChecked(activity.applies_to_risk)
        for index in range(self.category_input.count()):
            category = self.category_input.itemData(index)
            if category and category.id == activity.category_id:
                self.category_input.setCurrentIndex(index)
                break

    def _select_preferred_category(self, category_id: int) -> None:
        for index in range(self.category_input.count()):
            category = self.category_input.itemData(index)
            if category and category.id == category_id:
                self.category_input.setCurrentIndex(index)
                break

    def _handle_accept(self) -> None:
        if self.category_input.currentIndex() < 0:
            QMessageBox.warning(self, "Criterio requerido", "Primero crea al menos un criterio.")
            return
        if not self.name_input.text().strip():
            category = self._current_category()
            if category and category.category_mode == "deduction":
                QMessageBox.warning(self, "Campo requerido", "El nombre del criterio es obligatorio.")
            else:
                QMessageBox.warning(self, "Campo requerido", "El nombre de la actividad es obligatorio.")
            return
        self.accept()

    def get_payload(self) -> dict:
        category = self.category_input.currentData()
        return {
            "category_id": category.id,
            "category_name": category.name,
            "name": self.name_input.text().strip(),
            "max_score": self.max_score_input.value(),
            "sort_order": self.order_input.value(),
            "due_date": self.due_date_input.text().strip(),
            "applies_to_risk": self.risk_input.isChecked(),
        }
