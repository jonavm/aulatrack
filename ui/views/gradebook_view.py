from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from services.activity_service import ActivityService
from services.category_service import CategoryService
from services.export_service import ExportService
from services.grade_service import GradeCalculator
from services.gradebook_service import GradebookService
from ui.widgets.activity_dialog import ActivityDialog
from ui.widgets.activity_table_model import ActivityTableModel
from ui.widgets.category_dialog import CategoryDialog
from ui.widgets.category_table_model import CategoryTableModel
from ui.widgets.grade_spin_delegate import GradeSpinDelegate
from ui.widgets.gradebook_student_table_model import GradebookStudentTableModel
from ui.widgets.gradebook_table_view import GradebookTableView
from ui.widgets.table_preview_dialog import TablePreviewDialog


class GradebookView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.gradebook_service = GradebookService()
        self.category_service = CategoryService()
        self.activity_service = ActivityService()
        self.export_service = ExportService()
        self.category_model = CategoryTableModel()
        self.activity_model = ActivityTableModel()
        self.student_model = GradebookStudentTableModel()
        self.grade_delegate = GradeSpinDelegate(self)
        self._all_categories = []
        self._all_activities = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        hero_panel = QFrame()
        hero_panel.setObjectName("HeroPanel")
        hero_layout = QVBoxLayout(hero_panel)
        hero_layout.setContentsMargins(18, 18, 18, 18)
        hero_layout.setSpacing(18)

        header = QVBoxLayout()
        header.setSpacing(14)
        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(6)
        heading_row = QHBoxLayout()
        heading_row.setSpacing(10)
        self.page_title = QLabel("Calificaciones")
        self.page_title.setObjectName("PageTitle")
        self.group_status_badge = QLabel("Sin configurar")
        self.group_status_badge.setObjectName("BadgeWarning")
        heading_row.addWidget(self.page_title)
        heading_row.addWidget(self.group_status_badge, 0, Qt.AlignVCenter)
        heading_row.addStretch(1)

        self.header_context = QLabel("Selecciona un grupo y un periodo para empezar.")
        self.header_context.setObjectName("StatusValue")
        self.header_context.setWordWrap(True)
        self.header_summary = QLabel("Primero define los criterios. Luego pasa al libro para capturar por alumno.")
        self.header_summary.setObjectName("Caption")
        self.header_summary.setWordWrap(True)

        title_wrap.addLayout(heading_row)
        title_wrap.addWidget(self.header_context)
        title_wrap.addWidget(self.header_summary)

        self.group_selector = QComboBox()
        self.group_selector.setObjectName("DashboardControl")
        self.group_selector.setMinimumWidth(280)
        self.period_selector = QComboBox()
        self.period_selector.setObjectName("DashboardControl")
        self.period_selector.setMinimumWidth(170)
        self.period_selector.addItem("Periodo 1", 1)
        self.period_selector.addItem("Periodo 2", 2)
        self.period_selector.addItem("Periodo 3", 3)
        self.new_category_button = QPushButton("Nuevo criterio")
        self.add_activity_button = QPushButton("Nueva actividad")
        self.export_book_button = QPushButton("Exportar lista")
        self.expand_book_button = QPushButton("Pantalla completa")
        self.new_category_button.setObjectName("PrimaryButton")
        self.add_activity_button.setObjectName("GhostButton")
        self.export_book_button.setObjectName("GhostButton")
        self.expand_book_button.setObjectName("GhostButton")
        self.new_category_button.setMinimumWidth(150)
        self.add_activity_button.setMinimumWidth(156)
        self.export_book_button.setMinimumWidth(156)
        self.expand_book_button.setMinimumWidth(156)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(16)
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(12)
        filters_layout.addWidget(self.group_selector)
        filters_layout.addWidget(self.period_selector)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        actions_layout.addWidget(self.new_category_button)
        actions_layout.addWidget(self.add_activity_button)
        actions_layout.addWidget(self.export_book_button)
        actions_layout.addWidget(self.expand_book_button)

        controls_row.addLayout(filters_layout)
        controls_row.addStretch(1)
        controls_row.addLayout(actions_layout)

        header.addLayout(title_wrap)
        header.addLayout(controls_row)
        hero_layout.addLayout(header)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)

        config_page = QWidget()
        config_layout = QVBoxLayout(config_page)
        config_layout.setContentsMargins(0, 0, 0, 0)
        config_layout.setSpacing(16)

        management_splitter = QSplitter(Qt.Horizontal)
        management_splitter.setChildrenCollapsible(False)

        categories_panel = QFrame()
        categories_panel.setObjectName("Panel")
        categories_layout = QVBoxLayout(categories_panel)
        categories_layout.setContentsMargins(12, 12, 12, 12)
        categories_layout.setSpacing(10)
        category_header = QHBoxLayout()
        category_title = QLabel("Criterios de evaluacion")
        category_title.setObjectName("SectionTitle")
        self.edit_category_button = QPushButton("Editar")
        self.delete_category_button = QPushButton("Eliminar")
        self.delete_category_button.setObjectName("DangerButton")
        category_header.addWidget(category_title)
        category_header.addStretch(1)
        category_header.addWidget(self.edit_category_button)
        category_header.addWidget(self.delete_category_button)
        self.category_summary = QLabel("Sin criterios.")
        self.category_summary.setObjectName("Caption")
        self.category_helper = QLabel("Aqui defines si el criterio promedia normal o si trabaja por deduccion. La deduccion real se captura por alumno en el libro.")
        self.category_helper.setObjectName("StatusText")
        self.categories_table = QTableView()
        self.categories_table.setModel(self.category_model)
        self.categories_table.setSelectionBehavior(QTableView.SelectRows)
        self.categories_table.setSelectionMode(QTableView.SingleSelection)
        self.categories_table.verticalHeader().setVisible(False)
        self.categories_table.horizontalHeader().setStretchLastSection(True)
        self.categories_table.setShowGrid(False)
        self.categories_table.setEditTriggers(QTableView.NoEditTriggers)
        categories_layout.addLayout(category_header)
        categories_layout.addWidget(self.category_summary)
        categories_layout.addWidget(self.category_helper)
        categories_layout.addWidget(self.categories_table)

        activities_panel = QFrame()
        activities_panel.setObjectName("Panel")
        activities_layout = QVBoxLayout(activities_panel)
        activities_layout.setContentsMargins(12, 12, 12, 12)
        activities_layout.setSpacing(10)
        activity_header = QHBoxLayout()
        self.activity_panel_title = QLabel("Actividades")
        self.activity_panel_title.setObjectName("SectionTitle")
        self.edit_activity_button = QPushButton("Editar")
        self.delete_activity_button = QPushButton("Eliminar")
        self.delete_activity_button.setObjectName("DangerButton")
        activity_header.addWidget(self.activity_panel_title)
        activity_header.addStretch(1)
        activity_header.addWidget(self.edit_activity_button)
        activity_header.addWidget(self.delete_activity_button)
        self.selected_category_label = QLabel("Selecciona un criterio")
        self.selected_category_label.setObjectName("BadgeWarning")
        self.activity_summary = QLabel("Sin actividades.")
        self.activity_summary.setObjectName("Caption")
        self.activity_helper = QLabel("Aqui solo defines la estructura. La captura real siempre se hace por alumno en el libro.")
        self.activity_helper.setObjectName("StatusText")
        self.activities_table = QTableView()
        self.activities_table.setModel(self.activity_model)
        self.activities_table.setSelectionBehavior(QTableView.SelectRows)
        self.activities_table.setSelectionMode(QTableView.SingleSelection)
        self.activities_table.verticalHeader().setVisible(False)
        self.activities_table.horizontalHeader().setStretchLastSection(True)
        self.activities_table.setShowGrid(False)
        self.activities_table.setEditTriggers(QTableView.NoEditTriggers)
        activities_layout.addLayout(activity_header)
        activities_layout.addWidget(self.selected_category_label, 0, Qt.AlignLeft)
        activities_layout.addWidget(self.activity_summary)
        activities_layout.addWidget(self.activity_helper)
        activities_layout.addWidget(self.activities_table)

        management_splitter.addWidget(categories_panel)
        management_splitter.addWidget(activities_panel)
        management_splitter.setSizes([540, 640])

        config_layout.addWidget(management_splitter, 1)

        book_page = QWidget()
        book_layout = QVBoxLayout(book_page)
        book_layout.setContentsMargins(0, 0, 0, 0)
        book_layout.setSpacing(16)

        table_panel = QFrame()
        table_panel.setObjectName("Panel")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(12, 12, 12, 12)
        table_layout.setSpacing(10)
        table_title = QLabel("Libro del periodo actual")
        table_title.setObjectName("SectionTitle")
        self.table_caption = QLabel("Selecciona un grupo para preparar la captura.")
        self.table_caption.setObjectName("Caption")
        self.save_status_label = QLabel("Sin cambios recientes.")
        self.save_status_label.setObjectName("Caption")
        self.student_table = GradebookTableView()
        self.student_table.setModel(self.student_model)
        self.student_table.setItemDelegate(self.grade_delegate)
        self.student_table.setAlternatingRowColors(True)
        self.student_table.verticalHeader().setVisible(False)
        self.student_table.horizontalHeader().setStretchLastSection(False)
        self.student_table.setShowGrid(True)
        table_layout.addWidget(table_title)
        table_layout.addWidget(self.table_caption)
        table_layout.addWidget(self.save_status_label)
        table_layout.addWidget(self.student_table)

        book_layout.addWidget(table_panel, 1)

        layout.addWidget(hero_panel)
        self.tabs.addTab(config_page, "1. Estructura")
        self.tabs.addTab(book_page, "2. Libro")
        layout.addWidget(self.tabs, 1)

        self.group_selector.currentIndexChanged.connect(self._reload_snapshot)
        self.period_selector.currentIndexChanged.connect(self._reload_snapshot)
        self.new_category_button.clicked.connect(self._create_category)
        self.edit_category_button.clicked.connect(self._edit_category)
        self.delete_category_button.clicked.connect(self._delete_category)
        self.add_activity_button.clicked.connect(self._create_activity)
        self.export_book_button.clicked.connect(self._export_gradebook)
        self.expand_book_button.clicked.connect(self._open_book_fullscreen)
        self.edit_activity_button.clicked.connect(self._edit_activity)
        self.delete_activity_button.clicked.connect(self._delete_activity)
        self.categories_table.selectionModel().selectionChanged.connect(self._update_actions)
        self.categories_table.selectionModel().selectionChanged.connect(self._refresh_activity_panel)
        self.activities_table.selectionModel().selectionChanged.connect(self._update_actions)
        self.student_table.selectionModel().selectionChanged.connect(self._update_actions)
        self._load_groups()

    def _current_category_is_deduction(self) -> bool:
        category = self._current_category()
        return bool(category and category.category_mode == "deduction")

    def _load_groups(self) -> None:
        self.group_selector.blockSignals(True)
        self.group_selector.clear()
        groups = self.gradebook_service.group_service.list_groups()
        for group in groups:
            self.group_selector.addItem(group.qualified_display_name, group)
        self.group_selector.blockSignals(False)
        self._reload_snapshot()

    def _current_group(self):
        return self.group_selector.currentData()

    def _current_period_number(self) -> int:
        return int(self.period_selector.currentData() or 1)

    def _current_category(self):
        indexes = self.categories_table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.category_model.get_item(indexes[0].row())

    def _current_activity(self):
        indexes = self.activities_table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.activity_model.get_item(indexes[0].row())

    def _reload_snapshot(self) -> None:
        group = self._current_group()
        if not group:
            self._all_categories = []
            self._all_activities = []
            self.category_model.set_items([])
            self.activity_model.set_items([])
            self.student_model.set_snapshot(
                group_id=None,
                students=[],
                activities=[],
                categories=[],
                grades=[],
                adjustments=[],
                adjustment_entries=[],
                category_deductions=[],
                passing_grade=60.0,
                save_callback=self._save_score,
                save_adjustment_callback=self._save_adjustment,
                save_category_deduction_callback=self._add_category_deduction,
            )
            self.category_summary.setText("Crea primero un grupo para empezar.")
            self.activity_summary.setText("Sin estructura definida.")
            self.table_caption.setText("Selecciona un grupo para preparar la captura.")
            self.save_status_label.setText("Sin grupo seleccionado.")
            self.activity_panel_title.setText("Actividades o descuentos")
            self.selected_category_label.clear()
            self.selected_category_label.hide()
            self.activity_helper.setText("Aqui solo defines la estructura. La captura real siempre se hace por alumno en el libro.")
            self.page_title.setText("Calificaciones")
            self.header_context.setText("Selecciona un grupo y un periodo para empezar.")
            self.group_status_badge.setText("Sin configurar")
            self.group_status_badge.setObjectName("BadgeWarning")
            self.group_status_badge.style().unpolish(self.group_status_badge)
            self.group_status_badge.style().polish(self.group_status_badge)
            self.header_summary.setText("Primero define los criterios. Luego pasa al libro para capturar por alumno.")
            self._update_actions()
            return

        period_number = self._current_period_number()
        snapshot = self.gradebook_service.build_snapshot(group.id, period_number)
        categories = snapshot["categories"]
        activities = snapshot["activities"]
        students = snapshot["students"]
        grades = snapshot["grades"]
        adjustments = snapshot["adjustments"]
        adjustment_entries = snapshot["adjustment_entries"]
        category_deductions = snapshot["category_deductions"]
        self._all_categories = categories
        self._all_activities = activities
        self.category_model.set_items(categories)
        self.student_model.set_snapshot(
            group_id=group.id,
            students=students,
            activities=activities,
            categories=categories,
            grades=grades,
            adjustments=adjustments,
            adjustment_entries=adjustment_entries,
            category_deductions=category_deductions,
            passing_grade=group.passing_grade,
            save_callback=self._save_score,
            save_adjustment_callback=self._save_adjustment,
            save_category_deduction_callback=self._add_category_deduction,
        )
        self.categories_table.resizeColumnsToContents()
        self.student_table.resizeColumnsToContents()
        self._select_first_category_if_needed()
        self._refresh_activity_panel()

        active_categories = [item for item in categories if item.is_active]
        has_capture_structure = bool(activities)
        weights_valid = GradeCalculator.validate_weights([item.weight_percent for item in active_categories])
        self.page_title.setText("Calificaciones")
        self.header_context.setText(f"{group.qualified_display_name} · Periodo {period_number}")
        self.header_summary.setText(f"Configura los criterios del Periodo {period_number} y luego usa el libro para capturar rapido por alumno.")
        self.group_status_badge.setText("Activo" if weights_valid and active_categories else "En progreso")
        self.group_status_badge.setObjectName("BadgeSuccess" if weights_valid and active_categories else "BadgeWarning")
        self.group_status_badge.style().unpolish(self.group_status_badge)
        self.group_status_badge.style().polish(self.group_status_badge)

        self.category_summary.setText("Configuracion valida." if weights_valid else "La suma activa debe llegar a 100 puntos.")
        self.table_caption.setText(
            f"Captura por alumno en el libro del Periodo {period_number}. Tambien puedes asignar puntos extra aparte de los criterios usando el boton o la columna Extra."
            if students and has_capture_structure
            else "Faltan alumnos o estructura para comenzar la captura."
        )
        self.save_status_label.setText("Autoguardado listo.")
        self._update_actions()

    def _select_first_category_if_needed(self) -> None:
        if self.category_model.rowCount() > 0 and self.categories_table.currentIndex().row() < 0:
            self.categories_table.selectRow(0)

    def _refresh_activity_panel(self, *_args) -> None:
        category = self._current_category()
        if not category:
            self.activity_panel_title.setText("Actividades")
            self.activity_model.set_items([])
            self.activity_model.set_deduction_mode(False)
            self.activity_summary.setText("Selecciona un criterio para ver su estructura.")
            self.selected_category_label.clear()
            self.selected_category_label.hide()
            self.activity_helper.setText("Aqui solo defines la estructura. La captura real siempre se hace por alumno en el libro.")
            self.activities_table.resizeColumnsToContents()
            self._update_actions()
            return

        filtered = [item for item in self._all_activities if item.category_id == category.id]
        visible_items = filtered
        self.activity_model.set_items(visible_items)
        self.activity_model.set_deduction_mode(category.category_mode == "deduction")
        self.activities_table.resizeColumnsToContents()
        if category.category_mode == "deduction":
            self.activity_panel_title.setText("Captura de deduccion")
            self.selected_category_label.setText(f"Criterio activo: {category.name} | Deduccion por alumno")
            self.selected_category_label.setObjectName("BadgeWarning")
            self.activity_helper.setText(
                f'Este criterio no usa actividades. En el libro, haz clic sobre la celda de "{category.name}" del alumno y registra el descuento manualmente.'
            )
        else:
            self.activity_panel_title.setText("Actividades del criterio")
            self.selected_category_label.setText(f"Criterio activo: {category.name}")
            self.selected_category_label.setObjectName("BadgeSuccess")
            self.activity_helper.setText("Las actividades de este criterio se promedian de forma normal.")
        self.selected_category_label.show()
        self.selected_category_label.style().unpolish(self.selected_category_label)
        self.selected_category_label.style().polish(self.selected_category_label)
        if not filtered:
            if category.category_mode == "deduction":
                self.activity_summary.setText(f'La deduccion de "{category.name}" se captura directamente en el libro por alumno.')
            else:
                self.activity_summary.setText(f'El criterio "{category.name}" aun no tiene actividades.')
        elif len(filtered) == 1:
            if category.category_mode == "deduction":
                self.activity_summary.setText(f'La deduccion de "{category.name}" se captura directamente en el libro por alumno.')
            else:
                self.activity_summary.setText(f'1 actividad dentro de "{category.name}".')
        else:
            if category.category_mode == "deduction":
                self.activity_summary.setText(f'La deduccion de "{category.name}" se captura directamente en el libro por alumno.')
            else:
                self.activity_summary.setText(f'{len(filtered)} actividades dentro de "{category.name}".')
        if visible_items and self.activities_table.currentIndex().row() < 0:
            self.activities_table.selectRow(0)
        self._update_actions()

    def _create_category(self) -> None:
        group = self._current_group()
        if not group:
            QMessageBox.information(self, "Grupo requerido", "Primero selecciona o crea un grupo.")
            return
        dialog = CategoryDialog(self)
        if dialog.exec() != CategoryDialog.Accepted:
            return
        try:
            self.category_service.create(group.id, period_number=self._current_period_number(), **dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload_snapshot()

    def _edit_category(self) -> None:
        group = self._current_group()
        category = self._current_category()
        if not group or not category:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un criterio para editar.")
            return
        dialog = CategoryDialog(self, category=category)
        if dialog.exec() != CategoryDialog.Accepted:
            return
        try:
            self.category_service.update(category.id, group.id, period_number=self._current_period_number(), **dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload_snapshot()

    def _delete_category(self) -> None:
        category = self._current_category()
        if not category:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona un criterio para eliminar.")
            return
        confirmation = QMessageBox.question(
            self,
            "Eliminar criterio",
            f'Se eliminara el criterio "{category.name}" y sus elementos.\n\nEsta accion no se puede deshacer.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmation != QMessageBox.Yes:
            return
        self.category_service.delete(category.id)
        self._reload_snapshot()

    def _create_activity(self) -> None:
        group = self._current_group()
        if not group:
            QMessageBox.information(self, "Grupo requerido", "Primero selecciona un grupo.")
            return
        categories = self.category_service.list_by_group(group.id, self._current_period_number())
        if not categories:
            QMessageBox.information(self, "Criterio requerido", "Crea un criterio antes de agregar actividades o descuentos.")
            return
        selected_category = self._current_category()
        dialog = ActivityDialog(
            categories,
            self,
            preferred_category_id=selected_category.id if selected_category else None,
        )
        if dialog.exec() != ActivityDialog.Accepted:
            return
        try:
            self.activity_service.create(**dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload_snapshot()

    def _edit_activity(self) -> None:
        group = self._current_group()
        activity = self._current_activity()
        if not group or not activity:
            if self._current_category_is_deduction():
                QMessageBox.information(self, "Seleccion requerida", "Selecciona un criterio para editar.")
            else:
                QMessageBox.information(self, "Seleccion requerida", "Selecciona una actividad para editar.")
            return
        categories = self.category_service.list_by_group(group.id, self._current_period_number())
        dialog = ActivityDialog(categories, self, activity=activity)
        if dialog.exec() != ActivityDialog.Accepted:
            return
        try:
            self.activity_service.update(activity.id, **dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload_snapshot()

    def _delete_activity(self) -> None:
        activity = self._current_activity()
        if not activity:
            if self._current_category_is_deduction():
                QMessageBox.information(self, "Seleccion requerida", "Selecciona un criterio para eliminar.")
            else:
                QMessageBox.information(self, "Seleccion requerida", "Selecciona una actividad para eliminar.")
            return
        is_deduction = self._current_category_is_deduction()
        confirmation = QMessageBox.question(
            self,
            "Eliminar criterio" if is_deduction else "Eliminar actividad",
            (
                f'Se eliminara el criterio "{activity.name}".\n\nEsta accion no se puede deshacer.'
                if is_deduction
                else f'Se eliminara la actividad "{activity.name}".\n\nEsta accion no se puede deshacer.'
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmation != QMessageBox.Yes:
            return
        self.activity_service.delete(activity.id)
        self._reload_snapshot()

    def _update_actions(self, *_args) -> None:
        has_group = self._current_group() is not None
        has_category = self._current_category() is not None
        has_activity = self._current_activity() is not None
        deduction_category = self._current_category_is_deduction()
        self.new_category_button.setEnabled(has_group)
        self.period_selector.setEnabled(has_group)
        self.add_activity_button.setEnabled(has_category and not deduction_category)
        self.edit_category_button.setEnabled(has_category)
        self.delete_category_button.setEnabled(has_category)
        self.edit_activity_button.setEnabled(has_activity)
        self.delete_activity_button.setEnabled(has_activity)
        self.expand_book_button.setEnabled(has_group)
        self.export_book_button.setEnabled(has_group and self.student_model.rowCount() > 0)
        if not has_group:
            self.new_category_button.setText("Crea grupo primero")
        else:
            self.new_category_button.setText("Nuevo criterio")
        self.add_activity_button.setText("Nueva actividad")
        if deduction_category:
            self.add_activity_button.setText("No usa actividades")

    def _open_book_fullscreen(self) -> None:
        dialog = TablePreviewDialog(
            title=f"Libro del Periodo {self._current_period_number()}",
            subtitle="Vista ampliada para capturar y revisar con mas comodidad.",
            source_table=self.student_table,
            delegate=self.grade_delegate,
            parent=self,
        )
        dialog.exec()

    def _export_gradebook(self) -> None:
        group = self._current_group()
        if not group or self.student_model.rowCount() == 0:
            return

        period_number = self._current_period_number()
        default_name = f"calificaciones_{group.display_name}_periodo_{period_number}.pdf".replace(" ", "_")
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar calificaciones",
            str(Path.home() / default_name),
            "PDF (*.pdf);;Excel (*.xlsx);;CSV (*.csv)",
        )
        if not file_path:
            return
        if Path(file_path).suffix == "":
            if "pdf" in selected_filter.lower():
                file_path = f"{file_path}.pdf"
            elif "xlsx" in selected_filter.lower():
                file_path = f"{file_path}.xlsx"
            else:
                file_path = f"{file_path}.csv"

        headers = [
            str(self.student_model.headerData(column, Qt.Horizontal, Qt.DisplayRole) or "")
            for column in range(self.student_model.columnCount())
        ]
        rows = []
        for row in range(self.student_model.rowCount()):
            rows.append(
                [
                    str(self.student_model.data(self.student_model.index(row, column), Qt.DisplayRole) or "")
                    for column in range(self.student_model.columnCount())
                ]
            )

        metadata = [
            ("Grupo", group.qualified_display_name),
            ("Periodo", str(period_number)),
        ]
        exported_path = self.export_service.export_table(
            file_path,
            headers,
            rows,
            metadata,
            title="Lista de calificaciones",
        )
        self.save_status_label.setText(f"Lista exportada en: {exported_path}")
        QMessageBox.information(self, "Exportacion", "La lista de calificaciones se exporto correctamente.")

    def _save_score(
        self,
        activity_id: int,
        student_id: int,
        score: float | None,
        status: str,
        comment: str = "",
    ) -> None:
        self.gradebook_service.save_entry(activity_id, student_id, score, status, comment)
        activity = next((item for item in self._all_activities if item.id == activity_id), None)
        category = next((item for item in self._all_categories if activity and item.id == activity.category_id), None)
        is_deduction = bool(category and category.category_mode == "deduction")
        if status == "missing":
            self.save_status_label.setText(
                "Criterio marcado sin captura para este alumno." if is_deduction else "Actividad marcada como no entregada."
            )
        elif status == "pending":
            self.save_status_label.setText(
                "Criterio marcado como pendiente para este alumno." if is_deduction else "Actividad marcada como pendiente."
            )
        else:
            self.save_status_label.setText(
                f'Descuento guardado en "{activity.name}" para este alumno.'
                if is_deduction
                else f"Calificacion {score:.1f} guardada automaticamente."
            )

    def _save_adjustment(self, group_id: int, student_id: int, points: float, note: str = "") -> None:
        self.gradebook_service.add_adjustment_entry(group_id, student_id, points, note)
        self.save_status_label.setText(f"Puntos extra agregados: +{points:.2f}")

    def _add_category_deduction(self, category_id: int, student_id: int, points: float, note: str) -> None:
        self.gradebook_service.add_category_deduction(category_id, student_id, points, note)
        self.save_status_label.setText(f"Descuento agregado: -{points:.2f}")
