from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from services.database_service import DatabaseService
from services.school_service import SchoolService
from ui.widgets.school_dialog import SchoolDialog
from ui.widgets.schools_table_model import SchoolsTableModel


class SettingsView(QWidget):
    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.database_service = DatabaseService()
        self.school_service = SchoolService()
        self.school_model = SchoolsTableModel()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        title = QLabel("Escuelas")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Registra escuelas y protege tu informacion local con respaldos.")
        subtitle.setObjectName("Caption")

        school_panel = QFrame()
        school_panel.setObjectName("Panel")
        school_layout = QVBoxLayout(school_panel)
        school_layout.setContentsMargins(14, 14, 14, 14)
        school_layout.setSpacing(12)

        school_header = QHBoxLayout()
        school_title_wrap = QVBoxLayout()
        school_title = QLabel("Catalogo de escuelas")
        school_title.setObjectName("SectionTitle")
        school_subtitle = QLabel("Aqui guardas las escuelas que luego podras asignar a cada grupo.")
        school_subtitle.setObjectName("Caption")
        school_title_wrap.addWidget(school_title)
        school_title_wrap.addWidget(school_subtitle)

        self.new_button = QPushButton("Nueva escuela")
        self.new_button.setObjectName("PrimaryButton")
        self.edit_button = QPushButton("Editar")
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setObjectName("DangerButton")

        school_header.addLayout(school_title_wrap)
        school_header.addStretch(1)
        school_header.addWidget(self.edit_button)
        school_header.addWidget(self.delete_button)
        school_header.addWidget(self.new_button)

        self.summary_label = QLabel("Sin escuelas registradas.")
        self.summary_label.setObjectName("Caption")

        self.table = QTableView()
        self.table.setModel(self.school_model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableView.NoEditTriggers)

        school_layout.addLayout(school_header)
        school_layout.addWidget(self.summary_label)
        school_layout.addWidget(self.table)

        database_panel = QFrame()
        database_panel.setObjectName("Panel")
        database_layout = QVBoxLayout(database_panel)
        database_layout.setContentsMargins(14, 14, 14, 14)
        database_layout.setSpacing(12)

        database_header = QHBoxLayout()
        database_title_wrap = QVBoxLayout()
        database_title = QLabel("Respaldo de datos")
        database_title.setObjectName("SectionTitle")
        database_subtitle = QLabel("Tu informacion vive en una base local SQLite. Desde aqui puedes respaldarla o restaurarla.")
        database_subtitle.setObjectName("Caption")
        database_title_wrap.addWidget(database_title)
        database_title_wrap.addWidget(database_subtitle)

        self.backup_button = QPushButton("Crear respaldo")
        self.backup_button.setObjectName("PrimaryButton")
        self.restore_button = QPushButton("Restaurar respaldo")

        database_header.addLayout(database_title_wrap)
        database_header.addStretch(1)
        database_header.addWidget(self.restore_button)
        database_header.addWidget(self.backup_button)

        self.database_path_label = QLabel(
            f"Base actual: {self.database_service.get_database_path()}"
        )
        self.database_path_label.setObjectName("StatusText")
        self.database_status_label = QLabel(
            "Recomendado: crea un respaldo antes de cambios grandes o importaciones masivas."
        )
        self.database_status_label.setObjectName("Caption")
        self.database_status_label.setWordWrap(True)

        database_layout.addLayout(database_header)
        database_layout.addWidget(self.database_path_label)
        database_layout.addWidget(self.database_status_label)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(school_panel, 1)
        layout.addWidget(database_panel)

        self.new_button.clicked.connect(self._create_school)
        self.edit_button.clicked.connect(self._edit_school)
        self.delete_button.clicked.connect(self._delete_school)
        self.backup_button.clicked.connect(self._create_backup)
        self.restore_button.clicked.connect(self._restore_backup)
        self.table.doubleClicked.connect(self._edit_school)
        self.table.selectionModel().selectionChanged.connect(self._update_actions)

        self._reload()

    def _reload(self) -> None:
        schools = self.school_service.list_schools()
        self.school_model.set_schools(schools)
        if not schools:
            self.summary_label.setText("Sin escuelas registradas.")
        elif len(schools) == 1:
            self.summary_label.setText("1 escuela registrada. Ya puedes asociarla a tus grupos.")
        else:
            self.summary_label.setText(f"{len(schools)} escuelas registradas.")
        self.table.resizeColumnsToContents()
        if schools and self.table.currentIndex().row() < 0:
            self.table.selectRow(0)
        self._update_actions()

    def _selected_school(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.school_model.get_school(indexes[0].row())

    def _create_school(self) -> None:
        dialog = SchoolDialog(self)
        if dialog.exec() != SchoolDialog.Accepted:
            return
        try:
            self.school_service.create_school(**dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload()
        self.data_changed.emit()

    def _edit_school(self, *_args) -> None:
        school = self._selected_school()
        if not school:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona una escuela para editar.")
            return
        dialog = SchoolDialog(self, school=school)
        if dialog.exec() != SchoolDialog.Accepted:
            return
        try:
            self.school_service.update_school(school.id, **dialog.get_payload())
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        self._reload()
        self.data_changed.emit()

    def _delete_school(self) -> None:
        school = self._selected_school()
        if not school:
            QMessageBox.information(self, "Seleccion requerida", "Selecciona una escuela para eliminar.")
            return
        confirmation = QMessageBox.question(
            self,
            "Eliminar escuela",
            f'Se eliminara la escuela "{school.name}". Los grupos quedaran sin escuela asignada.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmation != QMessageBox.Yes:
            return
        self.school_service.delete_school(school.id)
        self._reload()
        self.data_changed.emit()

    def _update_actions(self, *_args) -> None:
        has_selection = self._selected_school() is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _create_backup(self) -> None:
        default_name = "aulatrack_respaldo.db"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar respaldo",
            default_name,
            "Base de datos SQLite (*.db)",
        )
        if not file_path:
            return
        try:
            backup_path = self.database_service.create_backup(file_path)
        except OSError as error:
            QMessageBox.warning(self, "Respaldo", f"No pude crear el respaldo.\n\n{error}")
            return
        self.database_status_label.setText(f"Respaldo creado correctamente en: {backup_path}")
        QMessageBox.information(
            self,
            "Respaldo creado",
            f"Se guardo una copia de seguridad en:\n\n{backup_path}",
        )

    def _restore_backup(self) -> None:
        confirmation = QMessageBox.question(
            self,
            "Restaurar respaldo",
            (
                "Vas a reemplazar la base actual con un respaldo.\n\n"
                "Si continuas, la informacion actual de la app sera sustituida por la del archivo seleccionado."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmation != QMessageBox.Yes:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar respaldo",
            "",
            "Base de datos SQLite (*.db);;Todos los archivos (*.*)",
        )
        if not file_path:
            return

        try:
            self.database_service.restore_backup(file_path)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Restauracion", str(error))
            return

        self.database_status_label.setText("Respaldo restaurado correctamente. Las vistas se recargaron con la informacion recuperada.")
        self._reload()
        self.data_changed.emit()
        QMessageBox.information(
            self,
            "Restauracion completada",
            "La base de datos fue restaurada correctamente.",
        )
