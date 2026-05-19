from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.entities import Student


class StudentDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, student: Student | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Editar alumno" if student else "Nuevo alumno")
        self.setModal(True)
        self.resize(430, 360)
        self._build_ui()
        if student:
            self._fill_form(student)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel(self.windowTitle())
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Captura datos simples y utiles para trabajar rapido.")
        subtitle.setObjectName("Caption")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Nombre")
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Apellidos")
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notas breves opcionales")
        self.notes_input.setFixedHeight(92)
        self.is_active_input = QCheckBox("Alumno activo")
        self.is_active_input.setChecked(True)

        form.addRow("Nombre", self.first_name_input)
        form.addRow("Apellidos", self.last_name_input)
        form.addRow("Notas", self.notes_input)
        form.addRow("", self.is_active_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._handle_accept)
        buttons.rejected.connect(self.reject)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(form)
        root.addStretch(1)
        root.addWidget(buttons)

    def _fill_form(self, student: Student) -> None:
        self.first_name_input.setText(student.first_name)
        self.last_name_input.setText(student.last_name)
        self.notes_input.setPlainText(student.notes)
        self.is_active_input.setChecked(student.is_active)

    def _handle_accept(self) -> None:
        if not self.first_name_input.text().strip():
            QMessageBox.warning(self, "Campo requerido", "El nombre del alumno es obligatorio.")
            self.first_name_input.setFocus()
            return
        if not self.last_name_input.text().strip():
            QMessageBox.warning(self, "Campo requerido", "Los apellidos del alumno son obligatorios.")
            self.last_name_input.setFocus()
            return
        self.accept()

    def get_payload(self) -> dict:
        return {
            "first_name": self.first_name_input.text().strip(),
            "last_name": self.last_name_input.text().strip(),
            "student_code": "",
            "notes": self.notes_input.toPlainText().strip(),
            "is_active": self.is_active_input.isChecked(),
        }
