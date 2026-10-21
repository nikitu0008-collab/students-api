"""Pydantic-модели для описания ответа API."""

from typing import Optional

from pydantic import BaseModel, Field


class Student(BaseModel):
    """Студент колледжа."""

    student_id: int = Field(..., description="Номер записи")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    date_of_birth: str = Field(..., description="Дата рождения")
    email: str = Field(..., description="Email")
    phone_number: str = Field(..., description="Номер телефона")
    address: str = Field(..., description="Адрес")
    enrollment_year: Optional[int] = Field(None, description="Год поступления")
    major: Optional[str] = Field(None, description="Специальность")
    course: int = Field(..., description="Курс")
    special_notes: Optional[str] = Field(None, description="Дополнительные заметки")


class CourseStats(BaseModel):
    """Количество студентов на одном курсе."""

    course: int
    students_count: int
