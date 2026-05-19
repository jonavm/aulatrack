from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from models.entities import School


class SchoolDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, school: School | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Editar escuela" if school else "Nueva escuela")
        self.setModal(True)
        self.resize(420, 180)
        self._build_ui()
        if school:
            self.name_input.setText(school.name)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)
        title = QLabel(self.windowTitle())
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Usa una escuela por campus o institucion donde da clases.")
        subtitle.setObjectName("Caption")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej. Primaria Benito Juarez")
        form.addRow("Nombre", self.name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(form)
        root.addWidget(buttons)

    def _accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Campo requerido", "El nombre de la escuela es obligatorio.")
            return
        self.accept()

    def get_payload(self) -> dict:
        return {"name": self.name_input.text().strip()}
