from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from models.entities import Group, School


class GroupDialog(QDialog):
    def __init__(
        self,
        schools: list[School],
        parent: QWidget | None = None,
        group: Group | None = None,
    ) -> None:
        super().__init__(parent)
        self._group = group
        self._schools = schools
        self._submit_mode = "save"
        self.setWindowTitle("Editar grupo" if group else "Nuevo grupo")
        self.setModal(True)
        self.resize(420, 320)
        self._build_ui()
        if group:
            self._fill_form(group)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel(self.windowTitle())
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Configura el contexto academico del grupo.")
        subtitle.setObjectName("Caption")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Se genera automaticamente. Ej. 2º-B")
        self.name_input.setReadOnly(True)

        self.school_input = QComboBox()
        self.school_input.addItem("Sin escuela", None)
        for school in self._schools:
            self.school_input.addItem(school.name, school.id)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Ej. Matematicas")

        self.grade_level_input = QLineEdit()
        self.grade_level_input.setPlaceholderText("Ej. 2º")

        self.group_section_input = QLineEdit()
        self.group_section_input.setPlaceholderText("Ej. B")

        self.school_year_input = QLineEdit()
        self.school_year_input.setPlaceholderText("Ej. 2026-2027")

        self.passing_grade_input = QDoubleSpinBox()
        self.passing_grade_input.setRange(0, 100)
        self.passing_grade_input.setDecimals(1)
        self.passing_grade_input.setSingleStep(1.0)
        self.passing_grade_input.setValue(60.0)

        form.addRow("Clave del grupo", self.name_input)
        form.addRow("Escuela", self.school_input)
        form.addRow("Materia", self.subject_input)
        form.addRow("Grado", self.grade_level_input)
        form.addRow("Grupo", self.group_section_input)
        form.addRow("Ciclo escolar", self.school_year_input)
        form.addRow("Minimo aprobatorio", self.passing_grade_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Guardar")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancelar")
        if not self._group:
            self.import_button = buttons.addButton("Importar lista", QDialogButtonBox.ActionRole)
            self.import_button.clicked.connect(self._handle_import_submit)
        buttons.accepted.connect(self._handle_accept)
        buttons.rejected.connect(self.reject)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(form)
        root.addStretch(1)
        root.addWidget(buttons)

    def _fill_form(self, group: Group) -> None:
        self.name_input.setText(group.display_name)
        for index in range(self.school_input.count()):
            if self.school_input.itemData(index) == group.school_id:
                self.school_input.setCurrentIndex(index)
                break
        self.subject_input.setText(group.subject_name)
        self.grade_level_input.setText(group.grade_level)
        self.group_section_input.setText(group.formatted_group_section)
        self.school_year_input.setText(group.school_year)
        self.passing_grade_input.setValue(group.passing_grade)

    def _handle_accept(self) -> None:
        self._submit_mode = "save"
        self._validate_and_accept()

    def _handle_import_submit(self) -> None:
        self._submit_mode = "import"
        self._validate_and_accept()

    def _validate_and_accept(self) -> None:
        grade_level_raw = self.grade_level_input.text().strip()
        group_section_raw = self.group_section_input.text().strip()

        if self._submit_mode == "save" and not grade_level_raw:
            QMessageBox.warning(self, "Campo requerido", "El grado es obligatorio.")
            self.grade_level_input.setFocus()
            return
        if self._submit_mode == "save" and not group_section_raw:
            QMessageBox.warning(self, "Campo requerido", "El grupo o seccion es obligatorio.")
            self.group_section_input.setFocus()
            return

        grade_level = Group.normalize_grade_level(grade_level_raw) if grade_level_raw else ""
        group_section = group_section_raw.upper() if group_section_raw else ""
        self.grade_level_input.setText(grade_level)
        self.group_section_input.setText(group_section)
        self.name_input.setText(f"{grade_level}-{group_section}" if grade_level and group_section else "")
        self.accept()

    @property
    def submit_mode(self) -> str:
        return self._submit_mode

    def get_payload(self) -> dict:
        grade_level = Group.normalize_grade_level(self.grade_level_input.text())
        group_section = self.group_section_input.text().strip().upper()
        group_name = f"{grade_level}-{group_section}" if grade_level and group_section else ""
        return {
            "name": group_name,
            "school_id": self.school_input.currentData(),
            "subject_name": self.subject_input.text().strip(),
            "grade_level": grade_level,
            "group_section": group_section,
            "school_year": self.school_year_input.text().strip(),
            "passing_grade": self.passing_grade_input.value(),
        }
