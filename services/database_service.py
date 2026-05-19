from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

from database.connection import DB_PATH, initialize_database


class DatabaseService:
    def get_database_path(self) -> Path:
        return DB_PATH

    def create_backup(self, destination: str) -> Path:
        target = Path(destination).expanduser()
        if target.suffix.lower() != ".db":
            target = target.with_suffix(".db")
        target.parent.mkdir(parents=True, exist_ok=True)

        source_connection = sqlite3.connect(DB_PATH)
        try:
            backup_connection = sqlite3.connect(target)
            try:
                source_connection.backup(backup_connection)
            finally:
                backup_connection.close()
        finally:
            source_connection.close()
        return target

    def restore_backup(self, source: str) -> Path:
        source_path = Path(source).expanduser()
        if not source_path.exists():
            raise ValueError("El archivo de respaldo no existe.")
        self._validate_sqlite_file(source_path)

        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        temp_restore_path = DB_PATH.with_suffix(".restore_tmp")
        shutil.copy2(source_path, temp_restore_path)
        self._validate_sqlite_file(temp_restore_path)
        temp_restore_path.replace(DB_PATH)
        initialize_database()
        return DB_PATH

    @staticmethod
    def _validate_sqlite_file(path: Path) -> None:
        try:
            with sqlite3.connect(path) as connection:
                connection.execute("PRAGMA foreign_keys = ON;")
                connection.execute("SELECT name FROM sqlite_master LIMIT 1").fetchall()
        except sqlite3.Error as error:
            raise ValueError("El archivo seleccionado no es un respaldo SQLite valido.") from error
