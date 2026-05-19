from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QDate, QSettings, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.attendance_service import AttendanceService
from services.export_service import ExportService
from services.group_service import GroupService
from ui.widgets.attendance_sheet_table_model import AttendanceSheetTableModel
from ui.widgets.attendance_sheet_table_view import AttendanceSheetTableView
from ui.widgets.table_preview_dialog import TablePreviewDialog


class AttendanceView(QWidget):
    LAST_GROUP_KEY = "attendance/last_group_id"
    STATUS_LABELS = {
        "all": "Todos los estados",
        "present": "Asistencia",
        "absent": "Falta",
        "late": "Retardo",
        "justified": "Justificada",
    }

    def __init__(self) -> None:
        super().__init__()
        self.group_service = GroupService()
        self.attendance_service = AttendanceService()
        self.export_service = ExportService()
        self.table_model = AttendanceSheetTableModel()
        self.settings = QSettings()
        self._current_snapshot: dict | None = None
        self._active_session_date: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(16)
        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(4)
        title = QLabel("Asistencia")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Control de asistencia diaria")
        subtitle.setObjectName("Caption")
        title_wrap.addWidget(title)
        title_wrap.addWidget(subtitle)

        self.group_selector = QComboBox()
        self.group_selector.setMinimumWidth(180)

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        self.prev_date_button = QPushButton("<")
        self.next_date_button = QPushButton(">")
        self.session_date_button = QPushButton("Sin fecha")
        self.session_date_button.setObjectName("GhostButton")
        nav_layout.addWidget(self.group_selector)
        nav_layout.addSpacing(10)
        nav_layout.addWidget(self.prev_date_button)
        nav_layout.addWidget(self.session_date_button)
        nav_layout.addWidget(self.next_date_button)

        header.addLayout(title_wrap, 1)
        header.addLayout(nav_layout)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        self.group_card = self._build_info_card("Grupo activo", "Sin grupo", "Sin sesion activa")
        self.group_value = self.group_card["value"]
        self.group_caption = self.group_card["caption"]
        cards_layout.addWidget(self.group_card["frame"], 2)

        self.total_card = self._build_metric_card("Total alumnos")
        self.present_card = self._build_metric_card("Asistencias")
        self.absent_card = self._build_metric_card("Faltas")
        self.late_card = self._build_metric_card("Retardos")
        self.justified_card = self._build_metric_card("Justificadas")
        self.metric_cards = {
            "total": self.total_card,
            "present": self.present_card,
            "absent": self.absent_card,
            "late": self.late_card,
            "justified": self.justified_card,
        }
        cards_layout.addWidget(self.total_card["frame"])
        cards_layout.addWidget(self.present_card["frame"])
        cards_layout.addWidget(self.absent_card["frame"])
        cards_layout.addWidget(self.late_card["frame"])
        cards_layout.addWidget(self.justified_card["frame"])

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar alumno...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(240)
        self.status_filter = QComboBox()
        self.status_filter.setMinimumWidth(170)
        self.status_filter.addItem("Todos los estados", "all")
        self.status_filter.addItem("Asistencia", "present")
        self.status_filter.addItem("Falta", "absent")
        self.status_filter.addItem("Retardo", "late")
        self.status_filter.addItem("Justificada", "justified")

        self.fullscreen_button = QPushButton("Pantalla completa")
        self.export_button = QPushButton("Exportar")
        self.export_button.setObjectName("PrimaryButton")

        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.status_filter)
        toolbar.addStretch(1)
        toolbar.addWidget(self.fullscreen_button)
        toolbar.addWidget(self.export_button)

        content = QHBoxLayout()
        content.setSpacing(16)

        table_frame = QFrame()
        table_frame.setObjectName("Panel")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(14, 14, 14, 14)
        table_layout.setSpacing(12)

        table_header = QHBoxLayout()
        table_header.setSpacing(12)
        context_wrap = QVBoxLayout()
        context_wrap.setSpacing(4)
        self.caption = QLabel("Selecciona un grupo para empezar.")
        self.caption.setObjectName("Caption")
        self.table_helper = QLabel("A, F, R y J cambian el estado de la celda seleccionada.")
        self.table_helper.setObjectName("StatusText")
        context_wrap.addWidget(self.caption)
        context_wrap.addWidget(self.table_helper)

        quick_date_wrap = QHBoxLayout()
        quick_date_wrap.setSpacing(8)
        self.inline_today_button = QPushButton("Agregar hoy")
        self.inline_today_button.setObjectName("PrimaryButton")
        self.inline_date_input = QDateEdit()
        self.inline_date_input.setCalendarPopup(True)
        self.inline_date_input.setDisplayFormat("d MMM yyyy")
        self.inline_date_input.setDate(QDate.currentDate())
        self.inline_date_input.setMinimumWidth(140)
        self.create_date_button = QPushButton("Agregar otra fecha")
        self.create_date_button.setObjectName("GhostButton")
        quick_date_wrap.addWidget(self.inline_today_button)
        quick_date_wrap.addWidget(self.inline_date_input)
        quick_date_wrap.addWidget(self.create_date_button)

        table_header.addLayout(context_wrap, 1)
        table_header.addLayout(quick_date_wrap)

        self.table = AttendanceSheetTableView()
        self.table.setModel(self.table_model)
        self.table.setSelectionBehavior(AttendanceSheetTableView.SelectItems)
        self.table.setSelectionMode(AttendanceSheetTableView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)

        table_layout.addLayout(table_header)
        table_layout.addWidget(self.table)

        side_panel = QFrame()
        side_panel.setObjectName("Panel")
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(14, 14, 14, 14)
        side_layout.setSpacing(14)

        legend_title = QLabel("Leyenda")
        legend_title.setObjectName("SectionTitle")
        side_layout.addWidget(legend_title)
        side_layout.addWidget(self._build_legend_chip("A", "Asistencia", "LegendChipPresent"))
        side_layout.addWidget(self._build_legend_chip("F", "Falta", "LegendChipAbsent"))
        side_layout.addWidget(self._build_legend_chip("R", "Retardo", "LegendChipLate"))
        side_layout.addWidget(self._build_legend_chip("J", "Justificada", "LegendChipJustified"))
        side_layout.addStretch(1)

        content.addWidget(table_frame, 1)
        content.addWidget(side_panel, 0)

        layout.addLayout(header)
        layout.addLayout(cards_layout)
        layout.addLayout(toolbar)
        layout.addLayout(content, 1)

        self.group_selector.currentIndexChanged.connect(self._handle_group_changed)
        self.inline_today_button.clicked.connect(self._open_today)
        self.prev_date_button.clicked.connect(lambda: self._step_session(-1))
        self.next_date_button.clicked.connect(lambda: self._step_session(1))
        self.session_date_button.clicked.connect(self._open_active_date)
        self.inline_date_input.dateChanged.connect(self._sync_inline_date)
        self.create_date_button.clicked.connect(self._create_inline_date)
        self.search_input.textChanged.connect(self._apply_filters)
        self.status_filter.currentIndexChanged.connect(self._apply_filters)
        self.fullscreen_button.clicked.connect(self._open_fullscreen_table)
        self.export_button.clicked.connect(self._export_attendance)

        self._load_groups()

    def _build_info_card(self, title_text: str, value_text: str, caption_text: str) -> dict:
        frame = QFrame()
        frame.setObjectName("Panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        title = QLabel(title_text)
        title.setObjectName("StatLabel")
        value = QLabel(value_text)
        value.setObjectName("SectionTitle")
        caption = QLabel(caption_text)
        caption.setObjectName("Caption")
        caption.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(value)
        layout.addWidget(caption)
        return {"frame": frame, "value": value, "caption": caption}

    def _build_metric_card(self, title_text: str) -> dict:
        frame = QFrame()
        frame.setObjectName("StatCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)
        title = QLabel(title_text)
        title.setObjectName("StatLabel")
        value = QLabel("--")
        value.setObjectName("StatValue")
        meta = QLabel("--")
        meta.setObjectName("Caption")
        layout.addWidget(title)
        layout.addWidget(value)
        layout.addWidget(meta)
        return {"frame": frame, "value": value, "meta": meta}

    def _build_legend_chip(self, code: str, label: str, object_name: str) -> QWidget:
        wrap = QWidget()
        layout = QHBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        chip = QLabel(code)
        chip.setObjectName(object_name)
        text = QLabel(label)
        text.setObjectName("Caption")
        layout.addWidget(chip)
        layout.addWidget(text)
        layout.addStretch(1)
        return wrap

    def _load_groups(self) -> None:
        current_group = self._current_group()
        current_group_id = current_group.id if current_group else None
        saved_group_id = self.settings.value(self.LAST_GROUP_KEY, None, int)

        self.group_selector.blockSignals(True)
        self.group_selector.clear()
        for group in self.group_service.list_groups():
            self.group_selector.addItem(group.qualified_display_name, group)

        target_group_id = current_group_id or saved_group_id
        if target_group_id is not None:
            for index in range(self.group_selector.count()):
                group = self.group_selector.itemData(index)
                if group and group.id == target_group_id:
                    self.group_selector.setCurrentIndex(index)
                    break
        self.group_selector.blockSignals(False)
        self._reload_sheet()

    def _current_group(self):
        return self.group_selector.currentData()

    def _handle_group_changed(self) -> None:
        group = self._current_group()
        if group:
            self.settings.setValue(self.LAST_GROUP_KEY, group.id)
        self._reload_sheet()

    def _open_today(self) -> None:
        self.inline_date_input.setDate(QDate.currentDate())
        self._create_or_open_session(QDate.currentDate().toString("yyyy-MM-dd"))

    def _open_active_date(self) -> None:
        if self._active_session_date:
            self._reload_sheet(select_date=self._active_session_date)

    def _sync_inline_date(self) -> None:
        selected = self.inline_date_input.date().toString("yyyy-MM-dd")
        if selected == self._active_session_date:
            return
        if self.table_model.session_column_for_date(selected) is not None:
            self._reload_sheet(select_date=selected)

    def _create_inline_date(self) -> None:
        self._create_or_open_session(self.inline_date_input.date().toString("yyyy-MM-dd"))

    def _create_or_open_session(self, session_date: str) -> None:
        group = self._current_group()
        if not group:
            return
        self.attendance_service.get_daily_attendance(group.id, session_date)
        self._reload_sheet(select_date=session_date)

    def _step_session(self, step: int) -> None:
        if not self._current_snapshot:
            return
        sessions = self._current_snapshot["sessions"]
        if not sessions:
            return
        current = self._active_session_date or sessions[-1].session_date
        dates = [session.session_date for session in sessions]
        try:
            current_index = dates.index(current)
        except ValueError:
            current_index = len(dates) - 1
        next_index = max(0, min(len(dates) - 1, current_index + step))
        self._reload_sheet(select_date=dates[next_index])

    def _reload_sheet(self, select_date: str | None = None) -> None:
        group = self._current_group()
        if not group:
            self._current_snapshot = None
            self._active_session_date = None
            self.table_model.set_sheet(students=[], sessions=[], records={}, save_callback=self._save_status)
            self.table_model.set_active_session_date(None)
            self.group_value.setText("Sin grupo")
            self.group_caption.setText("Selecciona un grupo para tomar asistencia.")
            self.caption.setText("Selecciona un grupo para empezar.")
            self.table_helper.setText("A, F, R y J cambian el estado de la celda seleccionada.")
            self.session_date_button.setText("Sin fecha")
            self.search_input.setEnabled(False)
            self.status_filter.setEnabled(False)
            self.inline_today_button.setEnabled(False)
            self.prev_date_button.setEnabled(False)
            self.next_date_button.setEnabled(False)
            self.session_date_button.setEnabled(False)
            self.create_date_button.setEnabled(False)
            self.fullscreen_button.setEnabled(False)
            self.export_button.setEnabled(False)
            for card in self.metric_cards.values():
                card["value"].setText("--")
                card["meta"].setText("--")
            self._apply_filters()
            return

        snapshot = self.attendance_service.get_attendance_sheet(group.id)
        sessions = snapshot["sessions"]
        if not sessions:
            target_date = select_date or self.inline_date_input.date().toString("yyyy-MM-dd")
            self.attendance_service.get_daily_attendance(group.id, target_date)
            snapshot = self.attendance_service.get_attendance_sheet(group.id)
            sessions = snapshot["sessions"]

        target_date = select_date or self._active_session_date or (sessions[-1].session_date if sessions else None)
        self._active_session_date = target_date
        self._current_snapshot = snapshot

        self.table_model.set_sheet(
            students=snapshot["students"],
            sessions=snapshot["sessions"],
            records=snapshot["records"],
            save_callback=self._save_status,
        )
        self.table_model.set_active_session_date(target_date)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, 340)

        target_qdate = QDate.fromString(target_date or "", "yyyy-MM-dd")
        if target_qdate.isValid():
            self.inline_date_input.blockSignals(True)
            self.inline_date_input.setDate(target_qdate)
            self.inline_date_input.blockSignals(False)

        target_column = self.table_model.session_column_for_date(target_date or "")
        if target_column is not None and snapshot["students"]:
            self.table.setCurrentIndex(self.table_model.index(0, target_column))
            self.table.scrollTo(self.table.currentIndex())

        school_text = group.school_name or "Sin escuela"
        formatted_date = self._format_date(target_date) if target_date else "Sin fecha"
        self.group_value.setText(f"{group.display_name} • {school_text}")
        self.group_caption.setText(f"Sesion activa: {formatted_date}")
        self.caption.setText(f"{group.display_name} | {school_text} | Fecha activa: {formatted_date}")
        self.table_helper.setText("A, F, R y J cambian el estado de la sesion activa y avanzan a la siguiente fila.")
        self.session_date_button.setText(formatted_date)

        self.search_input.setEnabled(True)
        self.status_filter.setEnabled(True)
        self.inline_today_button.setEnabled(True)
        self.prev_date_button.setEnabled(bool(sessions))
        self.next_date_button.setEnabled(bool(sessions))
        self.session_date_button.setEnabled(bool(target_date))
        self.create_date_button.setEnabled(True)
        self.fullscreen_button.setEnabled(bool(snapshot["students"]))
        self.export_button.setEnabled(bool(snapshot["students"]))

        show_today_button = self._should_show_today_button(snapshot["sessions"], target_date)
        self.inline_today_button.setVisible(show_today_button)
        if show_today_button:
            self.inline_today_button.setText("Agregar hoy")
            self.inline_today_button.setObjectName("PrimaryButton")
            self.inline_today_button.style().unpolish(self.inline_today_button)
            self.inline_today_button.style().polish(self.inline_today_button)

        self._update_summary(snapshot["students"], snapshot["records"], target_date or "")
        self._apply_filters()

    def _update_summary(self, students, records: dict[tuple[int, int], str], session_date: str) -> None:
        session_column = self.table_model.session_column_for_date(session_date)
        total = len(students)
        self.total_card["value"].setText(str(total))
        self.total_card["meta"].setText("Grupo cargado")
        if session_column is None:
            for key in ("present", "absent", "late", "justified"):
                self.metric_cards[key]["value"].setText("0")
                self.metric_cards[key]["meta"].setText("--")
            return

        session = self.table_model._sessions[session_column - 1]
        statuses = [records.get((student.id, session.id), "present") for student in students]
        absent = sum(1 for status in statuses if status == "absent")
        late = sum(1 for status in statuses if status == "late")
        justified = sum(1 for status in statuses if status == "justified")
        present = total - absent - late - justified
        values = {
            "present": present,
            "absent": absent,
            "late": late,
            "justified": justified,
        }
        for key, value in values.items():
            percentage = int(round((value / total) * 100)) if total else 0
            self.metric_cards[key]["value"].setText(str(value))
            self.metric_cards[key]["meta"].setText(f"{percentage}%")

    def _apply_filters(self) -> None:
        search = self.search_input.text().strip().lower()
        target_status = self.status_filter.currentData()
        active_column = self.table_model.session_column_for_date(self._active_session_date or "")

        for row in range(self.table_model.rowCount()):
            student = self.table_model._students[row]
            matches_search = search in student.roster_name.lower()
            matches_status = True
            if target_status != "all" and active_column is not None:
                session = self.table_model._sessions[active_column - 1]
                current_status = self.table_model._records.get((student.id, session.id), "present")
                matches_status = current_status == target_status
            self.table.setRowHidden(row, not (matches_search and matches_status))

    def _open_fullscreen_table(self) -> None:
        dialog = TablePreviewDialog(
            title="Lista de asistencia",
            subtitle="Vista ampliada para capturar asistencia con mas espacio.",
            source_table=self.table,
            parent=self,
        )
        dialog.exec()

    def _export_attendance(self) -> None:
        if not self._current_snapshot:
            return
        group = self._current_group()
        default_date = self._active_session_date or "general"
        default_name = f"asistencia_{group.display_name}_{default_date}.pdf".replace(" ", "_")
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar asistencia",
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
            str(self.table_model.headerData(column, Qt.Horizontal, Qt.DisplayRole) or "")
            for column in range(self.table_model.columnCount())
        ]
        rows = []
        for row in range(self.table_model.rowCount()):
            rows.append(
                [
                    str(self.table_model.data(self.table_model.index(row, column), Qt.DisplayRole) or "")
                    for column in range(self.table_model.columnCount())
                ]
            )

        metadata = [
            ("Grupo", group.qualified_display_name),
            ("Fecha activa", self._active_session_date or "Sin fecha"),
        ]
        exported_path = self.export_service.export_table(
            file_path,
            headers,
            rows,
            metadata,
            title="Lista de asistencia",
        )
        self.table_helper.setText(f"Lista exportada en: {exported_path}")
        QMessageBox.information(self, "Exportacion", "La lista de asistencia se exporto correctamente.")

    def _save_status(self, session_id: int, student_id: int, status: str) -> None:
        self.attendance_service.save_status(session_id, student_id, status)
        group = self._current_group()
        if not group:
            return
        session = self.attendance_service.get_attendance_by_session(session_id)
        session_date = session["session"].session_date if session else self.inline_date_input.date().toString("yyyy-MM-dd")
        self._reload_sheet(select_date=session_date)

    def _should_show_today_button(self, sessions, active_date: str | None) -> bool:
        today = QDate.currentDate().toString("yyyy-MM-dd")
        exists = any(session.session_date == today for session in sessions)
        return not exists and active_date != today

    def _format_date(self, raw_date: str | None) -> str:
        if not raw_date:
            return "Sin fecha"
        parsed = QDate.fromString(raw_date, "yyyy-MM-dd")
        if not parsed.isValid():
            return raw_date
        month_names = {
            1: "enero",
            2: "febrero",
            3: "marzo",
            4: "abril",
            5: "mayo",
            6: "junio",
            7: "julio",
            8: "agosto",
            9: "septiembre",
            10: "octubre",
            11: "noviembre",
            12: "diciembre",
        }
        return f"{parsed.day()} {month_names[parsed.month()]} {parsed.year()}"
