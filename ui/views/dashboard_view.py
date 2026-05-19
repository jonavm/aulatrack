from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.dashboard_service import DashboardService
from services.group_service import GroupService
from themes.theme import get_theme_tokens


class ProgressBar(QWidget):
    def __init__(self, color: str = "#335CFF", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = 0
        self._color = color
        self.setFixedHeight(10)

    def setValue(self, value: int) -> None:
        self._value = max(0, min(100, value))
        self.update()

    def setColor(self, color: str) -> None:
        self._color = color
        self.update()

    def paintEvent(self, _event) -> None:
        tokens = get_theme_tokens()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        background = self.rect().adjusted(0, 0, -1, -1)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(tokens["panel_alt"]))
        painter.drawRoundedRect(background, 5, 5)
        fill_width = int(background.width() * (self._value / 100))
        if fill_width <= 0:
            return
        fill_rect = background.adjusted(0, 0, fill_width - background.width(), 0)
        painter.setBrush(QColor(self._color))
        painter.drawRoundedRect(fill_rect, 5, 5)


class DonutChart(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.rows: list[dict] = []
        self.center_value = "0"
        self.center_label = "Alumnos"
        self.setMinimumSize(210, 210)

    def set_data(self, rows: list[dict], center_value: str, center_label: str) -> None:
        self.rows = rows
        self.center_value = center_value
        self.center_label = center_label
        self.update()

    def paintEvent(self, _event) -> None:
        tokens = get_theme_tokens()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)

        side = min(self.width(), self.height()) - 12
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        rect.adjust(10, 10, -10, -10)

        pen = QPen()
        pen.setWidth(24)
        pen.setCapStyle(Qt.FlatCap)

        start_angle = 90 * 16
        total_percent = sum(row.get("percent", 0) for row in self.rows)
        if total_percent <= 0:
            pen.setColor(QColor(tokens["border"]))
            painter.setPen(pen)
            painter.drawArc(rect, 0, 360 * 16)
        else:
            for row in self.rows:
                percent = row.get("percent", 0)
                span_angle = int(-360 * 16 * (percent / 100))
                pen.setColor(QColor(row.get("color", tokens["accent"])))
                painter.setPen(pen)
                painter.drawArc(rect, start_angle, span_angle)
                start_angle += span_angle

        inner_rect = rect.adjusted(42, 42, -42, -42)
        painter.setPen(QColor(tokens["text"]))
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(inner_rect.adjusted(0, -10, 0, 0), Qt.AlignCenter, self.center_value)
        font.setPointSize(10)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor(tokens["muted"]))
        painter.drawText(inner_rect.adjusted(0, 20, 0, 0), Qt.AlignCenter, self.center_label)


class DashboardView(QWidget):
    open_gradebook_requested = Signal()
    open_groups_requested = Signal()
    open_attendance_requested = Signal()
    open_students_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.dashboard_service = DashboardService()
        self.group_service = GroupService()
        self.selected_group_id: int | None = None
        self.search_text = ""
        self.metric_values: dict[str, QLabel] = {}
        self.metric_helpers: dict[str, QLabel] = {}
        self.group_average_rows: list[dict] = []
        self.distribution_rows: list[dict] = []
        self.alert_rows: list[dict] = []
        self.quick_action_buttons: list[QPushButton] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(18)

        top_row = QHBoxLayout()
        top_row.setSpacing(14)
        greeting_wrap = QVBoxLayout()
        greeting_wrap.setSpacing(4)
        self.title_label = QLabel("Buenas tardes")
        self.title_label.setObjectName("PageTitle")
        self.subtitle_label = QLabel("Aqui tienes un resumen de la actividad de tus grupos.")
        self.subtitle_label.setObjectName("Caption")
        greeting_wrap.addWidget(self.title_label)
        greeting_wrap.addWidget(self.subtitle_label)
        top_row.addLayout(greeting_wrap)
        top_row.addStretch(1)

        self.group_selector = QComboBox()
        self.group_selector.setObjectName("DashboardControl")
        self.group_selector.setMinimumWidth(190)
        self.group_selector.currentIndexChanged.connect(self._on_group_changed)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("DashboardControl")
        self.search_input.setPlaceholderText("Buscar alumnos, actividades...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(250)
        self.search_input.textChanged.connect(self._on_search_changed)

        self.alert_button = QPushButton("Alertas")
        self.alert_button.setObjectName("DashboardIconButton")

        self.primary_action = QPushButton("Nueva actividad")
        self.primary_action.setObjectName("PrimaryButton")
        self.primary_action.clicked.connect(self.open_gradebook_requested.emit)

        top_row.addWidget(self.group_selector)
        top_row.addWidget(self.search_input)
        top_row.addWidget(self.alert_button)
        top_row.addWidget(self.primary_action)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        stat_specs = [
            ("total_students", "Total alumnos", "MetricBlue"),
            ("avg_students_per_group", "Promedio general", "MetricGreen"),
            ("attendance_rate", "Asistencia semanal", "MetricPurple"),
            ("pending_activities", "Actividades pendientes", "MetricAmber"),
            ("at_risk_students", "Alumnos en riesgo", "MetricRed"),
        ]
        for column, (key, title, color_name) in enumerate(stat_specs):
            stats_grid.addWidget(self._build_metric_card(key, title, color_name), 0, column)

        middle_grid = QGridLayout()
        middle_grid.setSpacing(16)
        middle_grid.addWidget(self._build_group_average_panel(), 0, 0)
        middle_grid.addWidget(self._build_distribution_panel(), 0, 1)
        middle_grid.addWidget(self._build_alerts_panel(), 0, 2)

        root.addLayout(top_row)
        root.addLayout(stats_grid)
        root.addLayout(middle_grid)
        root.addWidget(self._build_quick_actions_panel())
        root.addStretch(1)

        self._load_groups()
        self.refresh()

    def _build_metric_card(self, key: str, title: str, icon_style: str) -> QWidget:
        card = QFrame()
        card.setObjectName("DashboardMetricCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        icon = QLabel(" ")
        icon.setObjectName(icon_style)
        icon.setFixedSize(46, 46)

        text_wrap = QVBoxLayout()
        text_wrap.setSpacing(2)
        label = QLabel(title)
        label.setObjectName("StatLabel")
        value = QLabel("--")
        value.setObjectName("StatValue")
        helper = QLabel("")
        helper.setObjectName("Caption")
        helper.setWordWrap(True)
        text_wrap.addWidget(label)
        text_wrap.addWidget(value)
        text_wrap.addWidget(helper)

        self.metric_values[key] = value
        self.metric_helpers[key] = helper

        layout.addWidget(icon, 0, Qt.AlignTop)
        layout.addLayout(text_wrap, 1)
        return card

    def _build_group_average_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("InfoCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Promedio por grupo")
        title.setObjectName("SectionTitle")
        header.addWidget(title)
        header.addStretch(1)
        scope = QLabel("Vista general")
        scope.setObjectName("Caption")
        header.addWidget(scope)
        layout.addLayout(header)

        for _ in range(6):
            row = self._build_group_average_row()
            self.group_average_rows.append(row)
            layout.addWidget(row["container"])
        layout.addStretch(1)
        return panel

    def _build_group_average_row(self) -> dict:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        name = QLabel("--")
        name.setObjectName("StatusValue")
        value = QLabel("--")
        value.setObjectName("Caption")
        top.addWidget(name)
        top.addStretch(1)
        top.addWidget(value)

        bar = ProgressBar()
        layout.addLayout(top)
        layout.addWidget(bar)
        return {"container": container, "name": name, "value": value, "bar": bar}

    def _build_distribution_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("InfoCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.distribution_title = QLabel("Distribucion de calificaciones")
        self.distribution_title.setObjectName("SectionTitle")
        layout.addWidget(self.distribution_title)

        body = QHBoxLayout()
        body.setSpacing(16)

        self.donut = DonutChart()
        body.addWidget(self.donut, 0, Qt.AlignTop)

        legend_wrap = QVBoxLayout()
        legend_wrap.setSpacing(10)
        self.distribution_total = QLabel("Sin datos")
        self.distribution_total.setObjectName("Caption")
        legend_wrap.addWidget(self.distribution_total)
        for _ in range(4):
            row = self._build_distribution_row()
            self.distribution_rows.append(row)
            legend_wrap.addWidget(row["container"])
        legend_wrap.addStretch(1)
        body.addLayout(legend_wrap, 1)

        layout.addLayout(body)
        return panel

    def _build_distribution_row(self) -> dict:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        dot = QLabel(" ")
        dot.setObjectName("DistributionDot")
        dot.setFixedSize(12, 12)
        label = QLabel("--")
        label.setObjectName("StatusValue")
        count = QLabel("--")
        count.setObjectName("Caption")
        percent = QLabel("--")
        percent.setObjectName("Caption")
        top.addWidget(dot, 0, Qt.AlignVCenter)
        top.addWidget(label)
        top.addStretch(1)
        top.addWidget(count)
        top.addWidget(percent)

        bar = ProgressBar()
        bar.setFixedHeight(8)

        layout.addLayout(top)
        layout.addWidget(bar)
        return {
            "container": container,
            "dot": dot,
            "label": label,
            "count": count,
            "percent": percent,
            "bar": bar,
        }

    def _build_alerts_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("InfoCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Alertas importantes")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        for _ in range(4):
            row = self._build_alert_row()
            self.alert_rows.append(row)
            layout.addWidget(row["container"])
        layout.addStretch(1)
        return panel

    def _build_alert_row(self) -> dict:
        container = QFrame()
        container.setObjectName("AlertInfo")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(2)
        title = QLabel("--")
        title.setObjectName("StatusValue")
        detail = QLabel("")
        detail.setObjectName("Caption")
        detail.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(detail)
        return {"container": container, "title": title, "detail": detail}

    def _build_quick_actions_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("InfoCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("Acciones rapidas")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)
        actions = [
            ("Pasar asistencia", self.open_attendance_requested.emit),
            ("Agregar actividad", self.open_gradebook_requested.emit),
            ("Capturar calificaciones", self.open_gradebook_requested.emit),
            ("Abrir grupos", self.open_groups_requested.emit),
            ("Ver alumnos", self.open_students_requested.emit),
        ]
        for label, callback in actions:
            button = QPushButton(label)
            button.setObjectName("QuickActionButton")
            button.clicked.connect(callback)
            self.quick_action_buttons.append(button)
            actions_row.addWidget(button)
        layout.addLayout(actions_row)
        return panel

    def _load_groups(self) -> None:
        groups = self.group_service.list_groups()
        current_group_id = self.selected_group_id
        self.group_selector.blockSignals(True)
        self.group_selector.clear()
        self.group_selector.addItem("Todos los grupos", None)
        for group in groups:
            self.group_selector.addItem(group.qualified_display_name, group.id)
        if current_group_id is not None:
            index = self.group_selector.findData(current_group_id)
            self.group_selector.setCurrentIndex(index if index >= 0 else 0)
        else:
            self.group_selector.setCurrentIndex(1 if groups else 0)
        self.group_selector.blockSignals(False)
        self.selected_group_id = self.group_selector.currentData()
        self.primary_action.setEnabled(self.selected_group_id is not None)

    def _on_group_changed(self) -> None:
        self.selected_group_id = self.group_selector.currentData()
        self.primary_action.setEnabled(self.selected_group_id is not None)
        self.refresh()

    def _on_search_changed(self, text: str) -> None:
        self.search_text = text
        self.refresh()

    def refresh(self) -> None:
        self._load_groups()
        summary = self.dashboard_service.get_summary(self.selected_group_id)
        self.metric_values["total_students"].setText(str(summary["total_students"]))
        self.metric_values["avg_students_per_group"].setText(f'{summary["avg_students_per_group"]:.1f}')
        self.metric_values["attendance_rate"].setText(f'{summary["attendance_rate"]:.0f}%')
        self.metric_values["pending_activities"].setText(str(summary["pending_activities"]))
        self.metric_values["at_risk_students"].setText(str(summary["at_risk_students"]))

        self.metric_helpers["total_students"].setText("Alumnos activos del grupo seleccionado.")
        self.metric_helpers["avg_students_per_group"].setText("Promedio actual en escala de 100.")
        self.metric_helpers["attendance_rate"].setText("Basada en los ultimos 7 dias registrados.")
        self.metric_helpers["pending_activities"].setText("Actividades con captura incompleta.")
        self.metric_helpers["at_risk_students"].setText("Promedio bajo, faltas o varias pendientes.")

        self._refresh_titles()
        self._refresh_group_average_rows()
        self._refresh_distribution_rows()
        self._refresh_alert_rows()

    def _refresh_titles(self) -> None:
        self.title_label.setText("Buenas tardes")
        if self.selected_group_id is None:
            self.subtitle_label.setText("Aqui tienes un resumen de la actividad de tus grupos.")
            self.distribution_title.setText("Distribucion de calificaciones")
            return
        group_name = self.group_selector.currentText()
        self.subtitle_label.setText(f"Resumen del grupo {group_name} y de su actividad reciente.")
        self.distribution_title.setText(f"Distribucion de calificaciones ({group_name})")

    def _refresh_group_average_rows(self) -> None:
        rows = self.dashboard_service.get_group_average_rows()
        active_group = self.selected_group_id
        tokens = get_theme_tokens()
        for index, widgets in enumerate(self.group_average_rows):
            if index < len(rows):
                row = rows[index]
                widgets["container"].show()
                widgets["name"].setText(row["label"])
                widgets["value"].setText(f'{row["average"]:.1f}/100')
                widgets["bar"].setValue(int(row["average"]))
                widgets["bar"].setColor(tokens["accent"] if row["group_id"] == active_group else tokens["border"])
            else:
                widgets["container"].hide()

    def _refresh_distribution_rows(self) -> None:
        rows = self.dashboard_service.get_grade_distribution(self.selected_group_id)
        total_students = int(self.metric_values["total_students"].text() or "0")
        self.distribution_total.setText(f"{total_students} alumnos considerados.")
        self.donut.set_data(rows, str(total_students), "Alumnos")
        for index, widgets in enumerate(self.distribution_rows):
            if index < len(rows):
                row = rows[index]
                widgets["container"].show()
                widgets["label"].setText(row["label"])
                widgets["count"].setText(f'{row["count"]} alumnos')
                widgets["percent"].setText(f'{row["percent"]}%')
                widgets["bar"].setColor(row["color"])
                widgets["bar"].setValue(int(row["percent"]))
                widgets["dot"].setStyleSheet(
                    f"background-color: {row['color']}; border-radius: 6px; border: none;"
                )
            else:
                widgets["container"].hide()

    def _refresh_alert_rows(self) -> None:
        alerts = self.dashboard_service.get_alerts(self.selected_group_id)
        self.alert_button.setText(f"Alertas ({len(alerts)})")
        tones = {
            "danger": "AlertDanger",
            "warning": "AlertWarning",
            "info": "AlertInfo",
            "success": "AlertSuccess",
        }
        for index, widgets in enumerate(self.alert_rows):
            if index < len(alerts):
                alert = alerts[index]
                widgets["container"].show()
                widgets["container"].setObjectName(tones.get(alert["tone"], "AlertInfo"))
                widgets["container"].style().unpolish(widgets["container"])
                widgets["container"].style().polish(widgets["container"])
                widgets["title"].setText(alert["title"])
                widgets["detail"].setText(alert["detail"])
            else:
                widgets["container"].hide()
