from __future__ import annotations


LIGHT_TOKENS = {
    "bg": "#EEF3F8",
    "sidebar": "#16243A",
    "sidebar_alt": "#1C2E49",
    "sidebar_text": "#FFFFFF",
    "sidebar_muted": "rgba(255, 255, 255, 0.70)",
    "sidebar_caption": "rgba(255, 255, 255, 0.76)",
    "sidebar_nav_text": "rgba(255, 255, 255, 0.86)",
    "sidebar_nav_hover": "rgba(255, 255, 255, 0.08)",
    "sidebar_nav_disabled": "rgba(255, 255, 255, 0.52)",
    "sidebar_nav_active": "#3F67F6",
    "switch_bg": "rgba(255, 255, 255, 0.18)",
    "switch_border": "rgba(255, 255, 255, 0.14)",
    "switch_checked": "#4C6FFF",
    "panel": "#FFFFFF",
    "panel_alt": "#F7FAFC",
    "panel_soft": "#F3F7FB",
    "border": "#D6DFEA",
    "text": "#142033",
    "muted": "#6E7C91",
    "accent": "#274C77",
    "accent_soft": "#E7EEF7",
    "selection_bg": "#DCE9FA",
    "selection_border": "#7EA2D6",
    "success": "#2F855A",
    "success_soft": "#EAF7F0",
    "success_border": "#B8E2CB",
    "success_text": "#1F8A5B",
    "warning": "#B7791F",
    "warning_soft": "#FFF4DB",
    "warning_border": "#F2D28A",
    "warning_text": "#B7791F",
    "danger": "#C05666",
    "danger_soft": "#FDF0F2",
    "danger_border": "#F2B8C0",
    "danger_soft_alt": "#FCEBED",
    "info_soft": "#E7F0FF",
    "info_border": "#BED2FB",
    "info_text": "#2563EB",
    "alert_danger_bg": "#FFF1F1",
    "alert_danger_border": "#F2C7C7",
    "alert_warning_bg": "#FFF8E8",
    "alert_warning_border": "#F3DEAF",
    "alert_info_bg": "#EFF5FF",
    "alert_info_border": "#D1DFFF",
    "alert_success_bg": "#EFFAF3",
    "alert_success_border": "#CBEBD6",
    "metric_blue_bg": "#E8EEFF",
    "metric_blue_border": "#C8D6FF",
    "metric_green_bg": "#E8F8EF",
    "metric_green_border": "#C6EFD5",
    "metric_purple_bg": "#F0E9FF",
    "metric_purple_border": "#D9C9FF",
    "metric_amber_bg": "#FFF4DE",
    "metric_amber_border": "#F6D59A",
    "metric_red_bg": "#FFE9E9",
    "metric_red_border": "#F4C1C1",
    "shadow": "rgba(16, 24, 40, 0.06)",
}

DARK_TOKENS = {
    "bg": "#111318",
    "sidebar": "#0F1726",
    "sidebar_alt": "#162133",
    "sidebar_text": "#F7FAFF",
    "sidebar_muted": "rgba(231, 238, 247, 0.70)",
    "sidebar_caption": "rgba(231, 238, 247, 0.76)",
    "sidebar_nav_text": "rgba(240, 245, 255, 0.88)",
    "sidebar_nav_hover": "rgba(110, 168, 254, 0.12)",
    "sidebar_nav_disabled": "rgba(240, 245, 255, 0.42)",
    "sidebar_nav_active": "#2F5FB8",
    "switch_bg": "rgba(255, 255, 255, 0.10)",
    "switch_border": "rgba(255, 255, 255, 0.10)",
    "switch_checked": "#6EA8FE",
    "panel": "#171A21",
    "panel_alt": "#20242D",
    "panel_soft": "#1D2230",
    "border": "#2B3240",
    "text": "#EEF2F7",
    "muted": "#98A2B3",
    "accent": "#6EA8FE",
    "accent_soft": "#1B2B46",
    "selection_bg": "#223758",
    "selection_border": "#6EA8FE",
    "success": "#4FB286",
    "success_soft": "#153528",
    "success_border": "#2E6E53",
    "success_text": "#8FE0B5",
    "warning": "#D3A34D",
    "warning_soft": "#3A2D16",
    "warning_border": "#705421",
    "warning_text": "#F0C878",
    "danger": "#E07A8A",
    "danger_soft": "#3A1F28",
    "danger_border": "#7C3C49",
    "danger_soft_alt": "#3C222A",
    "info_soft": "#1B2B46",
    "info_border": "#34527E",
    "info_text": "#8FC0FF",
    "alert_danger_bg": "#2E1B21",
    "alert_danger_border": "#6B3641",
    "alert_warning_bg": "#342916",
    "alert_warning_border": "#6F5726",
    "alert_info_bg": "#182537",
    "alert_info_border": "#355277",
    "alert_success_bg": "#152920",
    "alert_success_border": "#2F5E49",
    "metric_blue_bg": "#1A2940",
    "metric_blue_border": "#36557F",
    "metric_green_bg": "#172A21",
    "metric_green_border": "#2F5E49",
    "metric_purple_bg": "#261E38",
    "metric_purple_border": "#5A4C83",
    "metric_amber_bg": "#342916",
    "metric_amber_border": "#705421",
    "metric_red_bg": "#311E25",
    "metric_red_border": "#74404D",
}

CURRENT_THEME_MODE = "light"


def get_theme_tokens() -> dict:
    return DARK_TOKENS if CURRENT_THEME_MODE == "dark" else LIGHT_TOKENS


def build_stylesheet(mode: str = "dark") -> str:
    global CURRENT_THEME_MODE
    CURRENT_THEME_MODE = mode
    tokens = DARK_TOKENS if mode == "dark" else LIGHT_TOKENS
    return f"""
    QWidget {{
        background-color: {tokens["bg"]};
        color: {tokens["text"]};
        font-family: 'Segoe UI';
        font-size: 13px;
    }}
    QLabel {{
        background-color: transparent;
    }}
    QMainWindow {{
        background-color: {tokens["bg"]};
    }}
    QFrame#Sidebar {{
        background-color: {tokens.get("sidebar", tokens["panel"])};
        border: none;
        border-radius: 24px;
    }}
    QFrame#Panel, QFrame#StatCard, QFrame#InfoCard {{
        background-color: {tokens["panel"]};
        border: 1px solid {tokens["border"]};
        border-radius: 18px;
    }}
    QFrame#DashboardMetricCard {{
        background-color: {tokens["panel"]};
        border: 1px solid {tokens["border"]};
        border-radius: 18px;
    }}
    QFrame#SidebarCard {{
        background-color: {tokens.get("sidebar_alt", tokens["panel_alt"])};
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
    }}
    QFrame#SidebarBottom {{
        background-color: transparent;
        border: none;
    }}
    QFrame#SidebarInfoCard {{
        background-color: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
    }}
    QLabel#SectionTitle {{
        font-size: 17px;
        font-weight: 700;
    }}
    QLabel#PageTitle {{
        font-size: 27px;
        font-weight: 700;
        color: {tokens["text"]};
    }}
    QLabel#SidebarTitle {{
        color: {tokens["sidebar_text"]};
        font-size: 18px;
        font-weight: 700;
    }}
    QLabel#SidebarSubtle {{
        color: {tokens["sidebar_muted"]};
        font-size: 12px;
    }}
    QLabel#SidebarGroupValue {{
        color: {tokens["sidebar_text"]};
        font-size: 16px;
        font-weight: 700;
    }}
    QLabel#Caption {{
        color: {tokens["muted"]};
    }}
    QLabel#Eyebrow {{
        color: {tokens["accent"]};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    QLabel#StatusText {{
        color: {tokens["muted"]};
        font-size: 12px;
    }}
    QLabel#StatusValue {{
        color: {tokens["text"]};
        font-size: 15px;
        font-weight: 700;
    }}
    QLabel#DashboardEmptyState {{
        color: {tokens["muted"]};
        background-color: {tokens["panel_alt"]};
        border: 1px dashed {tokens["border"]};
        border-radius: 16px;
        padding: 30px 18px;
        font-size: 14px;
    }}
    QLabel#BadgeSuccess {{
        background-color: {tokens["success_soft"]};
        border: 1px solid {tokens["success_border"]};
        border-radius: 999px;
        padding: 4px 10px;
        color: {tokens["success_text"]};
        font-size: 12px;
        font-weight: 700;
    }}
    QLabel#BadgeWarning {{
        background-color: {tokens["warning_soft"]};
        border: 1px solid {tokens["warning_border"]};
        border-radius: 999px;
        padding: 4px 10px;
        color: {tokens["warning_text"]};
        font-size: 12px;
        font-weight: 700;
    }}
    QLabel#LegendChip {{
        background-color: {tokens["panel_alt"]};
        border: 1px solid {tokens["border"]};
        border-radius: 10px;
        padding: 6px 10px;
        color: {tokens["text"]};
        font-size: 12px;
        font-weight: 600;
    }}
    QLabel#LegendChipPresent {{
        background-color: {tokens["success_soft"]};
        border: 1px solid {tokens["success_border"]};
        border-radius: 10px;
        padding: 6px 10px;
        color: {tokens["success_text"]};
        font-size: 12px;
        font-weight: 700;
    }}
    QLabel#LegendChipAbsent {{
        background-color: {tokens["danger_soft_alt"]};
        border: 1px solid {tokens["danger_border"]};
        border-radius: 10px;
        padding: 6px 10px;
        color: {tokens["danger"]};
        font-size: 12px;
        font-weight: 700;
    }}
    QLabel#LegendChipLate {{
        background-color: {tokens["warning_soft"]};
        border: 1px solid {tokens["warning_border"]};
        border-radius: 10px;
        padding: 6px 10px;
        color: {tokens["warning_text"]};
        font-size: 12px;
        font-weight: 700;
    }}
    QLabel#LegendChipJustified {{
        background-color: {tokens["info_soft"]};
        border: 1px solid {tokens["info_border"]};
        border-radius: 10px;
        padding: 6px 10px;
        color: {tokens["info_text"]};
        font-size: 12px;
        font-weight: 700;
    }}
    QLabel#SidebarCaption {{
        color: {tokens["sidebar_caption"]};
    }}
    QLabel#MetricBlue, QLabel#MetricGreen, QLabel#MetricPurple, QLabel#MetricAmber, QLabel#MetricRed {{
        border-radius: 23px;
    }}
    QLabel#MetricBlue {{
        background-color: {tokens["metric_blue_bg"]};
        border: 1px solid {tokens["metric_blue_border"]};
    }}
    QLabel#MetricGreen {{
        background-color: {tokens["metric_green_bg"]};
        border: 1px solid {tokens["metric_green_border"]};
    }}
    QLabel#MetricPurple {{
        background-color: {tokens["metric_purple_bg"]};
        border: 1px solid {tokens["metric_purple_border"]};
    }}
    QLabel#MetricAmber {{
        background-color: {tokens["metric_amber_bg"]};
        border: 1px solid {tokens["metric_amber_border"]};
    }}
    QLabel#MetricRed {{
        background-color: {tokens["metric_red_bg"]};
        border: 1px solid {tokens["metric_red_border"]};
    }}
    QLabel#DistributionDot {{
        border-radius: 6px;
    }}
    QLabel#StatValue {{
        font-size: 30px;
        font-weight: 700;
        color: {tokens["text"]};
    }}
    QLabel#StatLabel {{
        color: {tokens["muted"]};
        font-size: 12px;
    }}
    QPushButton {{
        background-color: {tokens["panel_alt"]};
        border: 1px solid {tokens["border"]};
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 600;
    }}
    QPushButton:focus {{
        border-color: {tokens["accent"]};
    }}
    QPushButton:hover {{
        border-color: {tokens["accent"]};
    }}
    QPushButton:pressed {{
        background-color: {tokens["accent_soft"]};
    }}
    QPushButton:disabled {{
        color: {tokens["muted"]};
        background-color: {tokens["panel_soft"]};
        border-color: {tokens["border"]};
    }}
    QPushButton#PrimaryButton {{
        background-color: {tokens["accent"]};
        color: white;
        border: none;
    }}
    QPushButton#GhostButton {{
        background-color: transparent;
        color: {tokens["muted"]};
        border: 1px solid {tokens["border"]};
    }}
    QPushButton#DangerButton {{
        background-color: {tokens["danger_soft"]};
        color: {tokens["danger"]};
        border: 1px solid {tokens["danger"]};
    }}
    QPushButton#DashboardControl {{
        background-color: {tokens["panel"]};
    }}
    QPushButton#DashboardIconButton {{
        background-color: {tokens["panel"]};
        min-width: 92px;
    }}
    QPushButton#QuickActionButton {{
        background-color: {tokens["panel"]};
        border: 1px solid {tokens["border"]};
        border-radius: 14px;
        padding: 14px 18px;
        text-align: left;
    }}
    QToolButton {{
        background-color: {tokens["panel_alt"]};
        border: 1px solid {tokens["border"]};
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 600;
    }}
    QToolButton:hover {{
        border-color: {tokens["accent"]};
    }}
    QToolButton:pressed {{
        background-color: {tokens["accent_soft"]};
    }}
    QToolButton:disabled {{
        color: {tokens["muted"]};
        background-color: {tokens["panel_soft"]};
        border-color: {tokens["border"]};
    }}
    QToolButton::menu-indicator {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        right: 10px;
    }}
    QListWidget#SidebarNav {{
        background-color: transparent;
        border: none;
        outline: none;
        color: white;
        padding: 4px 0;
    }}
    QListWidget#SidebarNav::item {{
        background-color: transparent;
        border: none;
        border-radius: 14px;
        padding: 11px 14px;
        margin: 2px 0;
        color: {tokens["sidebar_nav_text"]};
        font-weight: 600;
    }}
    QListWidget#SidebarNav::item:selected {{
        background-color: {tokens["sidebar_nav_active"]};
        color: {tokens["sidebar_text"]};
    }}
    QListWidget#SidebarNav::item:hover {{
        background-color: {tokens["sidebar_nav_hover"]};
    }}
    QListWidget#SidebarNav::item:disabled {{
        color: {tokens["sidebar_nav_disabled"]};
    }}
    QTableView {{
        background-color: {tokens["panel"]};
        alternate-background-color: {tokens["panel_alt"]};
        border: 1px solid {tokens["border"]};
        border-radius: 16px;
        gridline-color: {tokens["border"]};
        selection-background-color: {tokens["accent_soft"]};
        selection-color: {tokens["text"]};
    }}
    QTableView::item:selected {{
        background-color: {tokens["selection_bg"]};
        color: {tokens["text"]};
        border-top: 1px solid {tokens["selection_border"]};
        border-bottom: 1px solid {tokens["selection_border"]};
    }}
    QTableView::item:selected:active {{
        background-color: {tokens["selection_bg"]};
        color: {tokens["text"]};
    }}
    QTableView::item:selected:!active {{
        background-color: {tokens["selection_bg"]};
        color: {tokens["text"]};
    }}
    QTableView:focus {{
        border-color: {tokens["accent"]};
    }}
    QHeaderView::section {{
        background-color: {tokens["panel_alt"]};
        color: {tokens["muted"]};
        border: none;
        border-bottom: 1px solid {tokens["border"]};
        padding: 11px;
        font-weight: 600;
    }}
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit, QListWidget {{
        background-color: {tokens["panel"]};
        border: 1px solid {tokens["border"]};
        border-radius: 12px;
        padding: 8px 10px;
    }}
    QComboBox#DashboardControl, QLineEdit#DashboardControl {{
        border-radius: 14px;
        padding: 10px 12px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus, QListWidget:focus {{
        border-color: {tokens["accent"]};
    }}
    QProgressBar {{
        background-color: {tokens["panel_alt"]};
        border: 1px solid {tokens["border"]};
        border-radius: 999px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: {tokens["accent"]};
        border-radius: 999px;
    }}
    QTextEdit {{
        padding: 10px 12px;
    }}
    QFrame#HeroPanel, QFrame#CalloutPanel {{
        background-color: {tokens["panel_soft"]};
        border: 1px solid {tokens["border"]};
        border-radius: 18px;
    }}
    QFrame#AlertDanger {{
        background-color: {tokens["alert_danger_bg"]};
        border: 1px solid {tokens["alert_danger_border"]};
        border-radius: 16px;
    }}
    QFrame#AlertWarning {{
        background-color: {tokens["alert_warning_bg"]};
        border: 1px solid {tokens["alert_warning_border"]};
        border-radius: 16px;
    }}
    QFrame#AlertInfo {{
        background-color: {tokens["alert_info_bg"]};
        border: 1px solid {tokens["alert_info_border"]};
        border-radius: 16px;
    }}
    QFrame#AlertSuccess {{
        background-color: {tokens["alert_success_bg"]};
        border: 1px solid {tokens["alert_success_border"]};
        border-radius: 16px;
    }}
    QTableWidget {{
        background-color: {tokens["panel"]};
        alternate-background-color: {tokens["panel_alt"]};
        border: 1px solid {tokens["border"]};
        border-radius: 16px;
        gridline-color: {tokens["border"]};
        selection-background-color: {tokens["panel"]};
        selection-color: {tokens["text"]};
    }}
    QTabWidget::pane {{
        border: none;
        background: transparent;
    }}
    QTabBar::tab {{
        background-color: {tokens["panel_alt"]};
        border: 1px solid {tokens["border"]};
        border-radius: 12px;
        padding: 10px 16px;
        margin-right: 8px;
        color: {tokens["muted"]};
        font-weight: 600;
    }}
    QTabBar::tab:selected {{
        background-color: {tokens["panel"]};
        color: {tokens["text"]};
        border-color: {tokens["accent"]};
    }}
    QDialog {{
        background-color: {tokens["bg"]};
    }}
    """
