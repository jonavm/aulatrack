from __future__ import annotations

import sqlite3

from app_paths import get_data_dir, get_resource_root

RESOURCE_ROOT = get_resource_root()
DB_DIR = get_data_dir()
DB_PATH = DB_DIR / "aulatrack.db"
SCHEMA_PATH = RESOURCE_ROOT / "database" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("PRAGMA busy_timeout = 5000;")
    connection.execute("PRAGMA synchronous = NORMAL;")
    connection.execute("PRAGMA temp_store = MEMORY;")
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        _prepare_legacy_migrations(connection)
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)
        _run_migrations(connection)


def _prepare_legacy_migrations(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    group_tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'groups'"
    ).fetchall()
    if group_tables:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(groups)").fetchall()
        }
        if "group_section" not in columns:
            connection.execute("ALTER TABLE groups ADD COLUMN group_section TEXT")
        if "school_id" not in columns:
            connection.execute("ALTER TABLE groups ADD COLUMN school_id INTEGER")


def _run_migrations(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(groups)").fetchall()
    }
    if "group_section" not in columns:
        connection.execute("ALTER TABLE groups ADD COLUMN group_section TEXT")
    if "school_id" not in columns:
        connection.execute("ALTER TABLE groups ADD COLUMN school_id INTEGER")

    category_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(evaluation_categories)").fetchall()
    }
    if "category_mode" not in category_columns:
        connection.execute(
            "ALTER TABLE evaluation_categories ADD COLUMN category_mode TEXT NOT NULL DEFAULT 'normal'"
        )
    if "period_number" not in category_columns:
        connection.execute(
            "ALTER TABLE evaluation_categories ADD COLUMN period_number INTEGER NOT NULL DEFAULT 1"
        )
    if "deduction_base_score" not in category_columns:
        connection.execute(
            "ALTER TABLE evaluation_categories ADD COLUMN deduction_base_score REAL NOT NULL DEFAULT 10"
        )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS student_category_deduction_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            points REAL NOT NULL DEFAULT 0,
            note TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES evaluation_categories(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_student_category_deduction_entries_category_student
        ON student_category_deduction_entries(category_id, student_id)
        """
    )
    _migrate_legacy_category_deductions(connection)


def _migrate_legacy_category_deductions(connection: sqlite3.Connection) -> None:
    tables = {
        row["name"]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }
    if "student_category_deductions" not in tables or "student_category_deduction_entries" not in tables:
        return

    existing_rows = connection.execute(
        "SELECT COUNT(*) AS total FROM student_category_deduction_entries"
    ).fetchone()["total"]
    if existing_rows:
        return

    connection.execute(
        """
        INSERT INTO student_category_deduction_entries (category_id, student_id, points, note, created_at)
        SELECT category_id, student_id, points, note, COALESCE(updated_at, CURRENT_TIMESTAMP)
        FROM student_category_deductions
        """
    )
