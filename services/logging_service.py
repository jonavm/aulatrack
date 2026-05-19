from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler

from PySide6.QtWidgets import QMessageBox

from app_paths import get_data_dir

LOG_DIR = get_data_dir() / "logs"
LOG_PATH = LOG_DIR / "aulatrack.log"


def configure_logging() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not any(isinstance(handler, RotatingFileHandler) for handler in root_logger.handlers):
        file_handler = RotatingFileHandler(
            LOG_PATH,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return LOG_PATH


def install_exception_hook() -> None:
    def _handle_exception(exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.getLogger("aulatrack.crash").exception(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

        QMessageBox.critical(
            None,
            "Error inesperado",
            (
                "Ocurrio un error inesperado en AulaTrack.\n\n"
                f"Se guardo un registro en:\n{LOG_PATH}"
            ),
        )

    sys.excepthook = _handle_exception
