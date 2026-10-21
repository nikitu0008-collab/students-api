"""Students API — REST API для списка студентов.

Данные хранятся в SQLite, при первом запуске база создаётся и наполняется
данными из students.json.
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from .database import SELECT_COLUMNS, get_connection, init_db
from .models import CourseStats, Student


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Students API",
    version="2.0.0",
    description=(
        "REST API для списка студентов: фильтрация по курсу, специальности "
        "и году поступления, агрегаты по группам."
    ),
    lifespan=lifespan,
)


@app.get("/students", response_model=list[Student])
def get_students(
    course: Optional[int] = Query(None, ge=1, description="Курс"),
    major: Optional[str] = Query(None, description="Специальность, регистр не важен"),
    enrollment_year: Optional[int] = Query(None, description="Год поступления"),
):
    """Вернуть студентов, отфильтровав по переданным параметрам."""
    clauses = []
    params = []

    if course is not None:
        clauses.append("course = ?")
        params.append(course)

    if major:
        clauses.append("major_lower = ?")
        params.append(major.strip().lower())

    if enrollment_year is not None:
        clauses.append("enrollment_year = ?")
        params.append(enrollment_year)

    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""

    with get_connection() as con:
        rows = con.execute(
            f"SELECT {SELECT_COLUMNS} FROM students{where} ORDER BY student_id", params
        ).fetchall()

    return [dict(row) for row in rows]


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    """Вернуть одного студента по номеру записи."""
    with get_connection() as con:
        row = con.execute(
            f"SELECT {SELECT_COLUMNS} FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Студент не найден")

    return dict(row)


@app.get("/stats/courses", response_model=list[CourseStats])
def get_course_stats():
    """Количество студентов на каждом курсе."""
    with get_connection() as con:
        rows = con.execute(
            """
            SELECT course, COUNT(*) AS students_count
            FROM students
            GROUP BY course
            ORDER BY course
            """
        ).fetchall()

    return [dict(row) for row in rows]


@app.get("/majors")
def get_majors():
    """Список специальностей с количеством студентов на каждой."""
    with get_connection() as con:
        rows = con.execute(
            """
            SELECT major, COUNT(*) AS students_count
            FROM students
            WHERE major IS NOT NULL
            GROUP BY major
            ORDER BY students_count DESC, major
            """
        ).fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
