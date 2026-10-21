"""Тесты API: фильтры, поиск по id, агрегаты."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Клиент с отдельной временной базой, чтобы не трогать рабочую."""
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def test_health_and_list(client):
    response = client.get("/students")
    assert response.status_code == 200
    students = response.json()
    assert len(students) == 10
    assert students[0]["student_id"] == 1


def test_filter_by_course(client):
    students = client.get("/students", params={"course": 2}).json()
    assert len(students) == 2
    assert all(student["course"] == 2 for student in students)


def test_filter_by_course_and_year(client):
    students = client.get(
        "/students", params={"course": 2, "enrollment_year": 2018}
    ).json()
    assert len(students) == 1
    assert students[0]["enrollment_year"] == 2018


def test_filter_by_major_ignores_case(client):
    lower = client.get("/students", params={"major": "биология"}).json()
    upper = client.get("/students", params={"major": "Биология"}).json()
    assert len(lower) == len(upper) == 3


def test_filter_without_matches_returns_empty_list(client):
    response = client.get("/students", params={"major": "Философия"})
    assert response.status_code == 200
    assert response.json() == []


def test_get_student_by_id(client):
    response = client.get("/students/1")
    assert response.status_code == 200
    assert response.json()["first_name"] == "Иван"


def test_get_missing_student_returns_404(client):
    response = client.get("/students/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Студент не найден"


def test_course_stats(client):
    stats = client.get("/stats/courses").json()
    assert sum(item["students_count"] for item in stats) == 10
    assert {item["course"] for item in stats} == {1, 2, 3, 4}


def test_majors_listed(client):
    majors = client.get("/majors").json()
    assert len(majors) == 7
    assert majors[0]["students_count"] >= majors[-1]["students_count"]


def test_openapi_generated(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/students" in response.json()["paths"]
