# Students API

REST API на FastAPI для работы со списком студентов: фильтрация по курсу, специальности и году поступления, агрегаты по группам. Данные хранятся в SQLite, при первом запуске база создаётся и наполняется из `students.json`.

## Стек

- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/) — фреймворк, автогенерация OpenAPI
- Pydantic v2 — валидация параметров и модели ответа
- SQLite (`sqlite3`) — хранение данных, параметризованные запросы
- Uvicorn — ASGI-сервер
- pytest + httpx — тесты
- Docker и Docker Compose

## Установка

```bash
git clone https://github.com/nikitu0008-collab/students-api.git
cd students-api
python -m venv .venv
```

Активация окружения:

```bash
source .venv/bin/activate      # Linux/macOS
```

```bash
.venv\Scripts\activate         # Windows
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn app.main:app --reload
```

Документация и Swagger UI: <http://127.0.0.1:8000/docs>
OpenAPI-схема: <http://127.0.0.1:8000/openapi.json>

## Запуск через Docker

```bash
docker compose up --build
```

API будет доступен на <http://localhost:8000>, база данных сохраняется в `./data`.

## Эндпоинты

### `GET /students`

Все студенты. Фильтры необязательные и комбинируются.

| Параметр | Тип | Описание |
|---|---|---|
| `course` | int | Курс |
| `major` | str | Специальность, регистр не важен |
| `enrollment_year` | int | Год поступления |

```bash
curl http://127.0.0.1:8000/students
curl "http://127.0.0.1:8000/students?course=2"
curl "http://127.0.0.1:8000/students?course=2&enrollment_year=2018"
curl "http://127.0.0.1:8000/students?major=Биология"
```

### `GET /students/{student_id}`

Один студент по номеру записи. Если записи нет — `404`.

```bash
curl http://127.0.0.1:8000/students/1
```

### `GET /stats/courses`

Сколько студентов на каждом курсе — агрегат `GROUP BY`.

```bash
curl http://127.0.0.1:8000/stats/courses
```

### `GET /majors`

Список специальностей с количеством студентов на каждой.

```bash
curl http://127.0.0.1:8000/majors
```

## Особенность реализации

`LOWER()` в SQLite приводит к нижнему регистру только ASCII-символы, поэтому
кириллицу он не трогает. Чтобы поиск по специальности работал независимо от
регистра, при наполнении базы рядом с `major` сохраняется нормализованная
колонка `major_lower` (нормализация делается на стороне Python), а фильтр
работает по ней.

## Тесты

```bash
pytest
```

10 тестов покрывают список, все комбинации фильтров, поиск по id, ответ 404, агрегаты и генерацию OpenAPI. Тесты используют отдельную временную базу, рабочая база не затрагивается.

## Структура проекта

```text
students-api/
├── app/
│   ├── __init__.py
│   ├── main.py         # эндпоинты FastAPI
│   ├── database.py     # подключение к SQLite, схема, наполнение
│   ├── models.py       # Pydantic-модели
│   └── utils.py        # чтение и запись JSON
├── tests/
│   └── test_api.py     # pytest-тесты API
├── students.json       # данные для наполнения базы
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

## Формат записи

```json
{
  "student_id": 1,
  "first_name": "Иван",
  "last_name": "Иванов",
  "date_of_birth": "1998-05-15",
  "email": "ivan.ivanov@example.com",
  "phone_number": "+7 (123) 456-7890",
  "address": "г. Москва, ул. Пушкина, д. 10, кв. 5",
  "enrollment_year": 2017,
  "major": "Информатика",
  "course": 3,
  "special_notes": "Без особых примет"
}
```

## Лицензия

MIT — файл [LICENSE](LICENSE).

## Автор

NikiZIP — студент колледжа IT TOP.
[Telegram](https://t.me/NikiZ1p) · [GitHub](https://github.com/nikitu0008-collab)
