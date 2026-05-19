import sys
import logging

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app_paths import get_resource_root
from database.connection import initialize_database
from services.logging_service import configure_logging, install_exception_hook
from themes.theme import build_stylesheet
from ui.main_window import MainWindow


def main() -> int:
    log_path = configure_logging()
    install_exception_hook()
    logging.getLogger("aulatrack").info("Iniciando aplicacion. Log activo en %s", log_path)

    app = QApplication(sys.argv)
    app.setOrganizationName("AulaTrack")
    app.setApplicationName("AulaTrack")
    icon_path = get_resource_root() / "assets" / "app_icon.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    initialize_database()
    app.setStyleSheet(build_stylesheet("light"))

    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.showMaximized()
    logging.getLogger("aulatrack").info("Ventana principal cargada correctamente.")

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
