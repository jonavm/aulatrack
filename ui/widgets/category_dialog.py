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

from models.entities import EvaluationCategory


class CategoryDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        category: EvaluationCategory | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Editar criterio" if category else "Nuevo criterio")
        self.setModal(True)
        self.resize(420, 320)
        self._build_ui()
        if category:
            self._fill_form(category)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel(self.windowTitle())
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Define el nombre, los puntos y el tipo de este criterio de evaluacion.")
        subtitle.setObjectName("Caption")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.name_input = QLineEdit()
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0, 100)
        self.weight_input.setDecimals(1)
        self.weight_input.setSuffix(" pts")
        self.mode_input = QComboBox()
        self.mode_input.addItem("Promedio", "normal")
        self.mode_input.addItem("Deduccion", "deduction")
        self.order_input = QSpinBox()
        self.order_input.setRange(0, 999)
        self.is_active_input = QCheckBox("Criterio activo")
        self.is_active_input.setChecked(True)

        form.addRow("Criterio", self.name_input)
        form.addRow("Puntos", self.weight_input)
        form.addRow("Calculo", self.mode_input)
        form.addRow("Orden", self.order_input)
        form.addRow("", self.is_active_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._handle_accept)
        buttons.rejected.connect(self.reject)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(form)
        root.addStretch(1)
        root.addWidget(buttons)
    def _fill_form(self, category: EvaluationCategory) -> None:
        self.name_input.setText(category.name)
        self.weight_input.setValue(category.weight_percent)
        for index in range(self.mode_input.count()):
            if self.mode_input.itemData(index) == category.category_mode:
                self.mode_input.setCurrentIndex(index)
                break
        self.order_input.setValue(category.sort_order)
        self.is_active_input.setChecked(category.is_active)

    def _handle_accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Campo requerido", "El nombre del criterio es obligatorio.")
            return
        self.accept()

    def get_payload(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "weight_percent": self.weight_input.value(),
            "category_mode": self.mode_input.currentData(),
            "deduction_base_score": self.weight_input.value(),
            "sort_order": self.order_input.value(),
            "is_active": self.is_active_input.isChecked(),
        }
