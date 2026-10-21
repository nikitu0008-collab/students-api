"""Работа с базой данных SQLite: подключение, схема, начальное наполнение."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .utils import json_to_dict_list

BASE_DIR = Path(__file__).resolve().parent.parent
SEED_FILE = BASE_DIR / "students.json"

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    student_id      INTEGER PRIMARY KEY,
    first_name      TEXT    NOT NULL,
    last_name       TEXT    NOT NULL,
    date_of_birth   TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    phone_number    TEXT    NOT NULL,
    address         TEXT    NOT NULL,
    enrollment_year INTEGER,
    major           TEXT,
    course          INTEGER NOT NULL,
    special_notes   TEXT,
    major_lower     TEXT
);

CREATE INDEX IF NOT EXISTS idx_students_course ON students (course);
CREATE INDEX IF NOT EXISTS idx_students_major  ON students (major);
CREATE INDEX IF NOT EXISTS idx_students_majlow ON students (major_lower);
CREATE INDEX IF NOT EXISTS idx_students_year   ON students (enrollment_year);
"""

COLUMNS = (
    "student_id",
    "first_name",
    "last_name",
    "date_of_birth",
    "email",
    "phone_number",
    "address",
    "enrollment_year",
    "major",
    "course",
    "special_notes",
)

# LOWER() в SQLite приводит к нижнему регистру только ASCII, поэтому кириллицу
# он не трогает. Нормализованная копия специальности хранится отдельно.
SELECT_COLUMNS = ", ".join(COLUMNS)


def db_path() -> str:
    """Путь к файлу базы. Можно переопределить переменной DATABASE_PATH."""
    return os.environ.get("DATABASE_PATH", str(BASE_DIR / "students.db"))


@contextmanager
def get_connection():
    """Подключение к SQLite с автоматическим commit/rollback."""
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def seed_db() -> int:
    """Наполняет таблицу данными из students.json, если она пуста."""
    students = json_to_dict_list(str(SEED_FILE)) or []

    with get_connection() as con:
        count = con.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count:
            return 0

        insert_columns = SELECT_COLUMNS + ", major_lower"
        placeholders = ", ".join("?" * len(COLUMNS))
        con.executemany(
            f"INSERT INTO students ({insert_columns}) VALUES ({placeholders}, ?)",
            [
                tuple(student.get(column) for column in COLUMNS)
                + ((student.get("major") or "").strip().lower(),)
                for student in students
            ],
        )
    return len(students)


def init_db() -> None:
    """Создаёт схему и наполняет базу при первом запуске."""
    with get_connection() as con:
        con.executescript(SCHEMA)
    seed_db()
