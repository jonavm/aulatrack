from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QMenu,
)

from services.group_service import GroupService
from services.school_service import SchoolService
from services.student_service import StudentService
from ui.widgets.group_dialog import GroupDialog
from ui.widgets.groups_table_model import GroupsTableModel
from ui.widgets.student_dialog import StudentDialog
from ui.widgets.student_profile_dialog import StudentProfileDialog
from ui.widgets.students_table_model import StudentsTableModel
from ui.widgets.table_preview_dialog import TablePreviewDialog


class GroupsView(QWidget):
    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.group_service = GroupService()
        self.school_service = SchoolService()
        self.student_service = StudentService()
        self._navigation_mode = "groups"
        self.table_model = GroupsTableModel()
        self.students_model = StudentsTableModel()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title_wrap = QVBoxLayout()
        self.page_title = QLabel("Grupos")
        self.page_title.setObjectName("PageTitle")
        self.page_subtitle = QLabel("Gestiona grupos y trabaja sobre sus alumnos sin salir de esta vista.")
        self.page_subtitle.setObjectName("Caption")
        title_wrap.addWidget(self.page_title)
        title_wrap.addWidget(self.page_subtitle)

        self.new_button = QPushButton("Nuevo grupo")
        self.new_button.setObjectName("PrimaryButton")
        self.group_actions_button = QToolButton()
        self.group_actions_button.setText("Mas acciones")
        self.group_actions_button.setPopupMode(QToolButton.InstantPopup)
        self.group_actions_menu = QMenu(self.group_actions_button)
        self.edit_group_action = QAction("Editar grupo", self)
        self.delete_group_action = QAction("Eliminar grupo", self)
        self.group_actions_menu.addAction(self.edit_group_action)
        self.group_actions_menu.addAction(self.delete_group_action)
        self.group_actions_button.setMenu(self.group_actions_menu)

        header.addLayout(title_wrap)
        header.addStretch(1)
        header.addWidget(self.new_button)

        self.content_splitter = QSplitter()
        self.content_splitter.setChildrenCollapsible(False)

        self.table_panel = QFrame()
        self.table_panel.setObjectName("Panel")
        table_layout = QVBoxLayout(self.table_panel)
        table_layout.setContentsMargins(12, 12, 12, 12)
        table_layout.setSpacing(12)

        table_header = QHBoxLayout()
        table_title_wrap = QVBoxLayout()
        table_title = QLabel("Tus grupos")
        table_title.setObjectName("SectionTitle")
        self.summary_label = QLabel("Sin grupos registrados.")
        self.summary_label.setObjectName("Caption")
        table_title_wrap.addWidget(table_title)
        table_title_wrap.addWidget(self.summary_label)

        table_header.addLayout(table_title_wrap)
        table_header.addStretch(1)

        self.table = QTableView()
        self.table.setModel(self.table_model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setSortingEnabled(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.setMinimumWidth(420)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)

        table_layout.addLayout(table_header)
        table_layout.addWidget(self.table)

        self.students_panel = QFrame()
        self.students_panel.setObjectName("Panel")
        students_layout = QVBoxLayout(self.students_panel)
        students_layout.setContentsMargins(12, 12, 12, 12)
        students_layout.setSpacing(12)

        students_header = QHBoxLayout()
        students_title_wrap = QVBoxLayout()
        students_title_wrap.setSpacing(4)
        self.students_title = QLabel("Alumnos")
        self.students_title.setObjectName("SectionTitle")
        self.students_subtitle = QLabel("Selecciona un grupo para ver sus alumnos.")
        self.students_subtitle.setObjectName("Caption")
        students_title_wrap.addWidget(self.students_title)
        students_title_wrap.addWidget(self.students_subtitle)

        students_header.addLayout(students_title_wrap)
        students_header.addStretch(1)
        self.student_group_selector = QComboBox()
        self.student_group_selector.setMinimumWidth(180)
        self.new_student_button = QPushButton("Nuevo alumno")
        self.new_student_button.setObjectName("PrimaryButton")
        self.expand_students_button = QPushButton("Pantalla completa")
        self.profile_student_action = QAction("Ficha alumno", self)
        self.edit_student_action = QAction("Editar alumno", self)
        self.delete_student_action = QAction("Eliminar alumno", self)

        students_header.addWidget(self.student_group_selector)
        students_header.addWidget(self.new_student_button)
        students_header.addWidget(self.expand_students_button)

        self.students_meta_label = QLabel("Sin alumnos para mostrar.")
        self.students_meta_label.setObjectName("StatusText")
        self.import_hint_label = QLabel("Importa desde Excel o CSV.")
        self.import_hint_label.setObjectName("Caption")

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        self.student_search_input = QLineEdit()
        self.student_search_input.setPlaceholderText("Buscar alumno...")
        self.student_search_input.setClearButtonEnabled(True)
        self.student_search_input.setMinimumWidth(240)
        self.student_status_filter = QLineEdit()
        self.student_status_filter.hide()
        self.student_state_selector = QPushButton("Solo activos")
        self.student_state_selector.setObjectName("GhostButton")
        filter_row.addWidget(self.student_search_input)
        filter_row.addWidget(self.student_state_selector)
        filter_row.addWidget(self.import_hint_label)
        filter_row.addStretch(1)

        self.students_table = QTableView()
        self.students_table.setModel(self.students_model)
        self.students_table.setSelectionBehavior(QTableView.SelectRows)
        self.students_table.setSelectionMode(QTableView.SingleSelection)
        self.students_table.setAlternatingRowColors(True)
        self.students_table.verticalHeader().setVisible(False)
        self.students_table.horizontalHeader().setStretchLastSection(True)
        self.students_table.setShowGrid(False)
        self.students_table.setEditTriggers(QTableView.NoEditTriggers)
        self.students_table.setContextMenuPolicy(Qt.CustomContextMenu)

        students_layout.addLayout(students_header)
        students_layout.addWidget(self.students_meta_label)
        students_layout.addLayout(filter_row)
        students_layout.addWidget(self.students_table)

        self.content_splitter.addWidget(self.table_panel)
        self.content_splitter.addWidget(self.students_panel)
        self.content_splitter.setSizes([400, 900])

        layout.addLayout(header)
        layout.addWidget(self.content_splitter, 1)

        self.new_button.clicked.connect(self._create_group)
        self.edit_group_action.triggered.connect(self._edit_group)
        self.delete_group_action.triggered.connect(self._delete_group)
        self.table.doubleClicked.connect(self._edit_group)
        self.table.selectionModel().selectionChanged.connect(self._update_action_state)
        self.table.selectionModel().selectionChanged.connect(self._reload_students)
        self.table.customContextMenuRequested.connect(self._open_group_context_menu)

        self.new_student_button.clicked.connect(self._create_student)
        self.profile_student_action.triggered.connect(self._open_student_profile)
        self.edit_student_action.triggered.connect(self._edit_student)
        self.delete_student_action.triggered.connect(self._delete_student)
        self.expand_students_button.clicked.connect(self._open_students_fullscreen)
        self.student_group_selector.currentIndexChanged.connect(self._handle_student_group_changed)
        self.student_search_input.textChanged.connect(self._apply_student_filters)
        self.student_state_selector.clicked.connect(self._toggle_student_state_filter)
        self.students_table.doubleClicked.connect(self._handle_student_double_click)
        self.students_table.selectionModel().selectionChanged.connect(self._update_student_action_state)
        self.students_table.customContextMenuRequested.connect(self._open_student_context_menu)

        self._show_only_active_students = True
        self._reload_groups()
        self.set_navigation_mode("groups")

    def focus_students_section(self) -> None:
        if self.table_model.rowCount() and self._selected_group() is None:
            self.table.selectRow(0)
            self._reload_students()
        if self.students_model.rowCount():
            self.students_table.setFocus(Qt.OtherFocusReason)
        else:
            self.student_search_input.setFocus(Qt.OtherFocusReason)

    def set_navigation_mode(self, mode: str) -> None:
        self._navigation_mode = mode
        if mode == "students":
            self.page_title.setText("Alumnos")
            self.page_subtitle.setText("Consulta alumnos y abre sus fichas desde una sola lista.")
            self.table_panel.hide()
            self.students_panel.show()
            self.new_button.hide()
            self.new_student_button.show()
            self.student_group_selector.show()
            self.content_splitter.setSizes([0, 1])
            self.focus_students_section()
            return
        self.page_title.setText("Grupos")
        self.page_subtitle.setText("Gestiona tus grupos y su configuracion general.")
        self.table_panel.show()
        self.students_panel.hide()
        self.new_button.show()
        self.new_student_button.show()
        self.student_group_selector.hide()
        self.content_splitter.setSizes([1, 0])

    def _handle_student_group_changed(self) -> None:
        if self._navigation_mode != "students":
            return
        group_id = self.student_group_selector.currentData()
        if group_id is None:
            return
        self._select_group_by_id(group_id)
        self._reload_students()

    def _reload_groups(self) -> None:
        groups = self.group_service.list_groups()
        self.table_model.set_groups(groups)
        self.student_group_selector.blockSignals(True)
        self.student_group_selector.clear()
        for group in groups:
            self.student_group_selector.addItem(group.qualified_display_name, group.id)
        self.student_group_selector.blockSignals(False)
        count = len(groups)
        if count == 0:
            self.summary_label.setText("Sin grupos registrados.")
        elif count == 1:
            self.summary_label.setText("1 grupo registrado. Seleccionalo para ver su ficha operativa.")
        else:
            self.summary_label.setText(f"{count} grupos registrados. Selecciona uno para trabajar.")
        self.table.resizeColumnsToContents()
        if count and self.table.currentIndex().row() < 0:
            self.table.selectRow(0)
        selected_group = self._selected_group()
        if selected_group is not None:
            for index in range(self.student_group_selector.count()):
                if self.student_group_selector.itemData(index) == selected_group.id:
                    self.student_group_selector.blockSignals(True)
                    self.student_group_selector.setCurrentIndex(index)
                    self.student_group_selector.blockSignals(False)
                    break
        self._update_action_state()
        self._reload_students()

    def _select_group_by_id(self, group_id: int | None) -> None:
        if group_id is None:
            return
        for row in range(self.table_model.rowCount()):
            group = self.table_model.get_group(row)
            if group and group.id == group_id:
                self.table.selectRow(row)
                for index in range(self.student_group_selector.count()):
                    if self.student_group_selector.itemData(index) == group_id:
                        self.student_group_selector.blockSignals(True)
                        self.student_group_selector.setCurrentIndex(index)
                        self.student_group_selector.blockSignals(False)
                        break
                return

    def _selected_group(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.table_model.get_group(indexes[0].row())

    def _selected_student(self):
        indexes = self.students_table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.students_model.get_student(indexes[0].row())

    def _open_group_context_menu(self, position) -> None:
        index = self.table.indexAt(position)
        if index.isValid():
            self.table.selectRow(index.row())
        group = self._selected_group()
        if not group:
            return
        menu = QMenu(self)
        menu.addAction(self.edit_group_action)
        menu.addSeparator()
        menu.addAction(self.delete_group_action)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _open_student_context_menu(self, position) -> None:
        if self._navigation_mode != "students":
            return
        index = self.students_table.indexAt(position)
        if index.isValid():
            self.students_table.selectRow(index.row())
        student = self._selected_student()
        if not student:
            return
        menu = QMenu(self)
        menu.addAction(self.profile_student_action)
        menu.addAction(self.edit_student_action)
        menu.addSeparator()
        menu.addAction(self.delete_student_action)
        menu.exec(self.students_table.viewport().mapToGlobal(position))

    def _handle_student_double_click(self, *_args) -> None:
        if self._navigation_mode == "students":
            self._open_student_profile()
            return
        self._edit_student()

    def _create_group(self) -> None:
        dialog = GroupDialog(self.school_service.list_schools(), self)
        if dialog.exec() != GroupDialog.Accepted:
            return
        if dialog.submit_mode == "import":
            self._create_group_from_import(dialog.get_payload())
            return
        try:
            group = self.group_service.create_group(**dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload_groups()
        self._select_group_by_id(group.id)
        self.data_changed.emit()

    def _create_group_from_import(self, base_payload: dict) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar lista de alumnos",
            "",
            "Archivos de alumnos (*.xlsx *.xlsm *.csv)",
        )
        if not file_path:
            return

        try:
            preview = self.student_service.preview_import(file_path)
        except ValueError as error:
            QMessageBox.warning(self, "Importacion", str(error))
            return

        detected_grade, detected_section = self.student_service.import_service.split_group_label(
            preview.detected_group
        )
        grade_level = base_payload["grade_level"] or detected_grade
        group_section = base_payload["group_section"] or detected_section
        school_year = base_payload["school_year"] or preview.detected_school_year

        if not grade_level or not group_section:
            QMessageBox.warning(
                self,
                "Importacion",
                "No pude detectar claramente el grado y grupo en el archivo. Completa esos campos manualmente antes de importar.",
            )
            return

        school_id = base_payload["school_id"]
        if school_id is None and preview.detected_school:
            school = self.school_service.get_or_create_school(preview.detected_school)
            school_id = school.id

        payload = {
            **base_payload,
            "name": f"{grade_level}-{group_section}",
            "school_id": school_id,
            "grade_level": grade_level,
            "group_section": group_section,
            "school_year": school_year,
        }

        existing_group = self.group_service.find_matching_group(
            school_id=payload["school_id"],
            grade_level=payload["grade_level"],
            group_section=payload["group_section"],
            school_year=payload["school_year"],
        )
        if existing_group is None:
            try:
                target_group = self.group_service.create_group(**payload)
            except ValueError as error:
                QMessageBox.warning(self, "Validacion", str(error))
                return
        else:
            target_group = existing_group

        result = self.student_service.import_students(target_group.id, preview)
        summary_lines = [
            f'Grupo: {target_group.display_name}',
            f'Creados: {result["created"]}',
            f'Omitidos por duplicado: {result["skipped"]}',
        ]
        if result["warnings"]:
            summary_lines.append("Hubo filas ambiguas o incompletas que no se importaron.")
        self._reload_groups()
        self._select_group_by_id(target_group.id)
        self._reload_students()
        self.data_changed.emit()
        QMessageBox.information(self, "Importacion completada", "\n".join(summary_lines))

    def _import_group_from_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar grupo desde archivo",
            "",
            "Archivos de alumnos (*.xlsx *.xlsm *.csv)",
        )
        if not file_path:
            return

        try:
            preview = self.student_service.preview_import(file_path)
        except ValueError as error:
            QMessageBox.warning(self, "Importacion", str(error))
            return

        grade_level, group_section = self.student_service.import_service.split_group_label(
            preview.detected_group
        )
        if not grade_level or not group_section:
            QMessageBox.warning(
                self,
                "Importacion",
                "No pude detectar claramente el grupo en el archivo. Puedes crearlo manualmente o usar un formato que incluya 'Grado y grupo'.",
            )
            return

        school = None
        if preview.detected_school:
            school = self.school_service.get_or_create_school(preview.detected_school)

        existing_group = self.group_service.find_matching_group(
            school_id=school.id if school else None,
            grade_level=grade_level,
            group_section=group_section,
            school_year=preview.detected_school_year,
        )
        created_group = False
        if existing_group is None:
            target_group = self.group_service.create_group(
                name=f"{grade_level}-{group_section}",
                school_id=school.id if school else None,
                subject_name="",
                school_year=preview.detected_school_year,
                grade_level=grade_level,
                group_section=group_section,
                passing_grade=60.0,
            )
            created_group = True
        else:
            target_group = existing_group

        result = self.student_service.import_students(target_group.id, preview)
        message_lines = [
            f'Archivo: {preview.source_name}',
            f'Escuela: {school.name if school else "No detectada"}',
            f'Grupo: {target_group.display_name}',
            f'Ciclo: {preview.detected_school_year or "Sin detectar"}',
            "",
            "Resultado:",
            f'Grupo {"creado" if created_group else "reutilizado"} automaticamente.',
            f'Alumnos importados: {result["created"]}',
            f'Omitidos por duplicado: {result["skipped"]}',
        ]
        if result["warnings"]:
            message_lines.append("Hubo filas ambiguas o incompletas que no se importaron.")

        self._reload_groups()
        self._select_group_by_id(target_group.id)
        self._reload_students()
        self.data_changed.emit()
        QMessageBox.information(self, "Importacion completada", "\n".join(message_lines))

    def _edit_group(self, *_args) -> None:
        group = self._selected_group()
        if not group:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un grupo para editar.")
            return
        dialog = GroupDialog(self.school_service.list_schools(), self, group=group)
        if dialog.exec() != GroupDialog.Accepted:
            return
        payload = dialog.get_payload()
        try:
            self.group_service.update_group(group.id, **payload)
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload_groups()
        self.data_changed.emit()

    def _delete_group(self) -> None:
        group = self._selected_group()
        if not group:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un grupo para eliminar.")
            return

        message = (
            f'Se eliminara el grupo "{group.display_name}" y sus datos relacionados.\n\n'
            "Esta accion no se puede deshacer."
        )
        confirmation = QMessageBox.question(
            self,
            "Eliminar grupo",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmation != QMessageBox.Yes:
            return

        self.group_service.delete_group(group.id)
        self._reload_groups()
        self.data_changed.emit()

    def _update_action_state(self) -> None:
        has_selection = self._selected_group() is not None
        self.group_actions_button.setEnabled(has_selection)
        self.edit_group_action.setEnabled(has_selection)
        self.delete_group_action.setEnabled(has_selection)
        self.new_student_button.setEnabled(has_selection)
        

    def _reload_students(self, *_args) -> None:
        group = self._selected_group()
        if not group:
            self.students_title.setText("Alumnos")
            self.students_subtitle.setText("Selecciona un grupo para ver sus alumnos.")
            self.students_meta_label.setText("Sin alumnos para mostrar.")
            self.import_hint_label.setText(
                "Selecciona un grupo para habilitar la importacion."
            )
            self.students_model.set_students([])
            self._apply_student_filters()
            self._update_student_action_state()
            return

        students = self.student_service.list_students_by_group(group.id)
        if self._navigation_mode == "students":
            self.students_title.setText("Lista de alumnos")
        else:
            self.students_title.setText(f"Alumnos de {group.display_name}")
        subject_text = group.subject_name or "Sin materia"
        school_text = group.school_name or "Sin escuela"
        self.students_subtitle.setText(
            f"{school_text} | {subject_text} | Minimo {group.passing_grade:.1f} | {group.student_count} alumnos"
        )
        self.import_hint_label.setText(
            "Importa desde Excel o CSV."
        )
        if not students:
            self.students_meta_label.setText("Este grupo aun no tiene alumnos.")
        elif len(students) == 1:
            self.students_meta_label.setText("1 alumno registrado.")
        else:
            self.students_meta_label.setText(f"{len(students)} alumnos registrados.")
        self.students_model.set_students(students)
        self.students_table.resizeColumnsToContents()
        self.students_table.setColumnWidth(0, 360)
        self._apply_student_filters()
        if students and self.students_table.currentIndex().row() < 0:
            self.students_table.selectRow(0)
        self._update_student_action_state()

    def _create_student(self) -> None:
        group = self._selected_group()
        if not group:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un grupo primero.")
            return
        dialog = StudentDialog(self)
        if dialog.exec() != StudentDialog.Accepted:
            return
        try:
            self.student_service.create_student(group.id, **dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload_groups()
        self._reload_students()
        self.data_changed.emit()

    def _edit_student(self, *_args) -> None:
        student = self._selected_student()
        if not student:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un alumno para editar.")
            return
        dialog = StudentDialog(self, student=student)
        if dialog.exec() != StudentDialog.Accepted:
            return
        try:
            self.student_service.update_student(student.id, student.group_id, **dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload_students()
        self.data_changed.emit()

    def _open_student_profile(self) -> None:
        group = self._selected_group()
        student = self._selected_student()
        if not group or not student:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un alumno para ver su ficha.")
            return
        dialog = StudentProfileDialog(group.id, student, self)
        if dialog.exec() == StudentProfileDialog.Accepted:
            self._reload_students()
            self.data_changed.emit()

    def _delete_student(self) -> None:
        student = self._selected_student()
        if not student:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un alumno para eliminar.")
            return
        confirmation = QMessageBox.question(
            self,
            "Eliminar alumno",
            f'Se eliminara a "{student.full_name}".\n\nEsta accion no se puede deshacer.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmation != QMessageBox.Yes:
            return
        self.student_service.delete_student(student.id)
        self._reload_groups()
        self._reload_students()
        self.data_changed.emit()

    def _update_student_action_state(self) -> None:
        has_group = self._selected_group() is not None
        has_student = self._selected_student() is not None
        self.new_student_button.setEnabled(has_group)
        self.expand_students_button.setEnabled(has_group)
        self.profile_student_action.setEnabled(has_student)
        self.edit_student_action.setEnabled(has_student)
        self.delete_student_action.setEnabled(has_student)

    def _handle_import(self) -> None:
        if self._selected_group() is not None:
            self._import_students()
            return
        self._import_group_from_file()

    def _apply_student_filters(self) -> None:
        search_text = self.student_search_input.text().strip().lower()
        for row in range(self.students_model.rowCount()):
            student = self.students_model.get_student(row)
            if student is None:
                self.students_table.setRowHidden(row, True)
                continue
            matches_search = search_text in student.roster_name.lower()
            matches_state = student.is_active or not self._show_only_active_students
            self.students_table.setRowHidden(row, not (matches_search and matches_state))

    def _toggle_student_state_filter(self) -> None:
        self._show_only_active_students = not self._show_only_active_students
        self.student_state_selector.setText("Solo activos" if self._show_only_active_students else "Todos")
        self._apply_student_filters()

    def _open_students_fullscreen(self) -> None:
        dialog = TablePreviewDialog(
            title="Alumnos del grupo",
            subtitle="Vista ampliada para revisar, buscar y gestionar alumnos con mas espacio.",
            source_table=self.students_table,
            parent=self,
        )
        dialog.exec()

    def _import_students(self) -> None:
        group = self._selected_group()
        if not group:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un grupo primero.")
            return
        self._import_students_into_group(group)

    def _import_students_into_group(self, group) -> None:
        if not group:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar alumnos",
            "",
            "Archivos de alumnos (*.xlsx *.xlsm *.csv)",
        )
        if not file_path:
            return

        try:
            preview = self.student_service.preview_import(file_path)
        except ValueError as error:
            QMessageBox.warning(self, "Importacion", str(error))
            return

        message_lines = [
            f'Archivo: {preview.source_name}',
            f'Filas leidas: {preview.total_rows}',
            f'Deteccion automatica: {preview.detected_mode}',
            f'Alumnos listos para importar: {len(preview.students)}',
        ]
        if preview.sheet_name:
            message_lines.append(f'Hoja detectada: {preview.sheet_name}')
        if preview.detected_school:
            message_lines.append(f'Escuela detectada: {preview.detected_school}')
        if preview.detected_school_year:
            message_lines.append(f'Ciclo detectado: {preview.detected_school_year}')
        if preview.detected_group:
            message_lines.append(f'Grupo detectado en archivo: {preview.detected_group}')
        if preview.warnings:
            message_lines.append("Advertencia: se omitieron algunas filas incompletas o ambiguas.")
        if preview.detected_group and preview.detected_group != group.display_name:
            message_lines.append(
                f'Atencion: el archivo parece corresponder a "{preview.detected_group}" y el grupo seleccionado es "{group.display_name}".'
            )
        message_lines.append("")
        message_lines.append(f'Los alumnos se agregaran al grupo "{group.display_name}".')
        confirmation = QMessageBox.question(
            self,
            "Confirmar importacion",
            "\n".join(message_lines),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if confirmation != QMessageBox.Yes:
            return

        result = self.student_service.import_students(group.id, preview)
        summary_lines = [
            f'Creados: {result["created"]}',
            f'Omitidos por duplicado: {result["skipped"]}',
        ]
        if result["warnings"]:
            summary_lines.append("Hubo filas ambiguas o incompletas que no se importaron.")
        QMessageBox.information(self, "Importacion completada", "\n".join(summary_lines))
        self._reload_groups()
        self._select_group_by_id(group.id)
        self._reload_students()
        self.data_changed.emit()
