from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from services.group_service import GroupService
from themes.theme import build_stylesheet
from ui.views.attendance_view import AttendanceView
from ui.views.dashboard_view import DashboardView
from ui.views.gradebook_view import GradebookView
from ui.views.groups_view import GroupsView
from ui.views.settings_view import SettingsView
from ui.widgets.toggle_switch import ToggleSwitch


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_mode = "light"
        self.group_service = GroupService()
        self._active_group_id: int | None = None
        self.setWindowTitle("AulaTrack")
        self.setMinimumSize(1280, 820)
        self.resize(1360, 860)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(256)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 14, 14, 14)
        sidebar_layout.setSpacing(14)

        brand_card = QFrame()
        brand_card.setObjectName("SidebarCard")
        brand_layout = QVBoxLayout(brand_card)
        brand_layout.setContentsMargins(14, 14, 14, 14)
        brand_layout.setSpacing(2)
        title = QLabel("AulaTrack")
        title.setObjectName("SidebarTitle")
        subtitle = QLabel("Gestion escolar local para docentes")
        subtitle.setObjectName("SidebarCaption")
        brand_layout.addWidget(title)
        brand_layout.addWidget(subtitle)

        self.nav = QListWidget()
        self.nav.setObjectName("SidebarNav")
        self.nav.setSpacing(4)
        self.nav.setAlternatingRowColors(False)
        self.nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_items = [
            ("Dashboard", "Resumen general", 0, True),
            ("Grupos", "Grupos y alumnos", 1, True),
            ("Alumnos", "Ver fichas de alumnos", 1, True),
            ("Asistencia", "Libro de asistencia", 2, True),
            ("Calificaciones", "Libro de calificaciones", 3, True),
            ("Escuelas", "Catalogo de escuelas", 4, True),
        ]
        for label, hint, stack_index, enabled in nav_items:
            item = QListWidgetItem(label, self.nav)
            item.setToolTip(hint)
            item.setData(Qt.UserRole, stack_index)
            item.setSizeHint(QSize(0, 42))
            if not enabled:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled & ~Qt.ItemIsSelectable)

        bottom_panel = QFrame()
        bottom_panel.setObjectName("SidebarBottom")
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        active_group_card = QFrame()
        active_group_card.setObjectName("SidebarInfoCard")
        active_group_layout = QVBoxLayout(active_group_card)
        active_group_layout.setContentsMargins(12, 10, 12, 10)
        active_group_layout.setSpacing(2)
        active_group_label = QLabel("Grupo activo")
        active_group_label.setObjectName("SidebarSubtle")
        self.active_group_value = QLabel("Sin grupo")
        self.active_group_value.setObjectName("SidebarGroupValue")
        self.active_group_value.setWordWrap(True)
        active_group_layout.addWidget(active_group_label)
        active_group_layout.addWidget(self.active_group_value)

        mode_row = QHBoxLayout()
        mode_row.setContentsMargins(6, 0, 6, 0)
        mode_row.setSpacing(8)
        mode_label = QLabel("Modo claro")
        mode_label.setObjectName("SidebarSubtle")
        self.mode_toggle = ToggleSwitch()
        self.mode_toggle.setChecked(True)
        mode_row.addWidget(mode_label)
        mode_row.addStretch(1)
        mode_row.addWidget(self.mode_toggle)

        bottom_layout.addWidget(active_group_card)
        bottom_layout.addLayout(mode_row)

        sidebar_layout.addWidget(brand_card)
        sidebar_layout.addWidget(self.nav, 1)
        sidebar_layout.addWidget(bottom_panel)

        self.stack = QStackedWidget()
        self.dashboard_view = DashboardView()
        self.groups_view = GroupsView()
        self.attendance_view = AttendanceView()
        self.gradebook_view = GradebookView()
        self.settings_view = SettingsView()
        self.groups_view.data_changed.connect(self.dashboard_view.refresh)
        self.groups_view.data_changed.connect(self.dashboard_view._load_groups)
        self.groups_view.data_changed.connect(self.attendance_view._load_groups)
        self.groups_view.data_changed.connect(self.gradebook_view._load_groups)
        self.settings_view.data_changed.connect(self.groups_view._reload_groups)
        self.settings_view.data_changed.connect(self.dashboard_view._load_groups)
        self.dashboard_view.open_gradebook_requested.connect(lambda: self._select_nav_item("Calificaciones"))
        self.dashboard_view.open_groups_requested.connect(lambda: self._select_nav_item("Grupos"))
        self.dashboard_view.open_attendance_requested.connect(lambda: self._select_nav_item("Asistencia"))
        self.dashboard_view.open_students_requested.connect(lambda: self._select_nav_item("Alumnos"))
        self.settings_view.data_changed.connect(self.attendance_view._load_groups)
        self.settings_view.data_changed.connect(self.gradebook_view._load_groups)
        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.groups_view)
        self.stack.addWidget(self.attendance_view)
        self.stack.addWidget(self.gradebook_view)
        self.stack.addWidget(self.settings_view)

        layout.addWidget(sidebar, 0)
        layout.addWidget(self.stack, 1)

        self.nav.currentItemChanged.connect(self._handle_nav_change)
        self.mode_toggle.toggled.connect(self._toggle_mode)
        self.groups_view.data_changed.connect(self._refresh_active_group)
        self.dashboard_view.group_selector.currentIndexChanged.connect(self._refresh_active_group)
        self.attendance_view.group_selector.currentIndexChanged.connect(self._refresh_active_group)
        self.gradebook_view.group_selector.currentIndexChanged.connect(self._refresh_active_group)
        self.groups_view.table.selectionModel().selectionChanged.connect(self._refresh_active_group)
        self.nav.setCurrentRow(0)
        self._refresh_active_group()

        self.setCentralWidget(root)

    def _handle_nav_change(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            return
        stack_index = current.data(Qt.UserRole)
        if stack_index is None:
            return
        self.stack.setCurrentIndex(int(stack_index))
        if current.text() == "Alumnos":
            self.groups_view.set_navigation_mode("students")
            self.groups_view.focus_students_section()
            self._refresh_active_group()
            return
        if current.text() == "Grupos":
            self.groups_view.set_navigation_mode("groups")
        self._refresh_active_group()

    def _refresh_active_group(self, *_args) -> None:
        active_label = self._get_contextual_active_group_label()
        if active_label:
            self.active_group_value.setText(active_label)
            return
        groups = self.group_service.list_groups()
        if groups:
            fallback_group = self._find_group_by_id(self._active_group_id) or groups[0]
            self._active_group_id = fallback_group.id
            self.active_group_value.setText(fallback_group.qualified_display_name)
        else:
            self._active_group_id = None
            self.active_group_value.setText("Sin grupo")

    def _get_contextual_active_group_label(self) -> str | None:
        current_view = self.stack.currentWidget()
        if current_view is self.dashboard_view:
            if self.dashboard_view.selected_group_id is None:
                self._active_group_id = None
                return self.dashboard_view.group_selector.currentText() or "Todos los grupos"
            group = self._find_group_by_id(self.dashboard_view.selected_group_id)
            if group is not None:
                self._active_group_id = group.id
                return group.qualified_display_name
            return None

        if current_view is self.groups_view:
            group = self.groups_view._selected_group()
            if group is not None:
                self._active_group_id = group.id
                return group.qualified_display_name
            return None

        if current_view is self.attendance_view:
            group = self.attendance_view._current_group()
            if group is not None:
                self._active_group_id = group.id
                return group.qualified_display_name
            return None

        if current_view is self.gradebook_view:
            group = self.gradebook_view._current_group()
            if group is not None:
                self._active_group_id = group.id
                return group.qualified_display_name
            return None

        return None

    def _find_group_by_id(self, group_id: int | None):
        if group_id is None:
            return None
        return next((group for group in self.group_service.list_groups() if group.id == group_id), None)

    def _toggle_mode(self, checked: bool) -> None:
        self.current_mode = "light" if checked else "dark"
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(build_stylesheet(self.current_mode))

    def _select_nav_item(self, label: str) -> None:
        for index in range(self.nav.count()):
            item = self.nav.item(index)
            if item and item.text() == label:
                self.nav.setCurrentRow(index)
                return
