**Схема БД (коротко):** Проекты и задачи в отдельных таблицах, задачи привязаны к проекту. Участники проектов — в таблице связей project_members. История смены статусов — в task_status_history (кто, когда, из какого статуса в какой). Индексы стоят на полях, по которым часто ищем и фильтруем: project_id, status, priority, assignee_id, created_at и пара (task_id, changed_at) для истории — чтобы списки и история открывались быстро.

---

Шаг 1. Клонировать/распаковать проект и создать venv

В терминале в папке с проектом:

python -m venv .venv
pip install -r requirements.txt

Шаг 2. Создать базу в PostgreSQL

Через pgAdmin или psql создай пустую базу с именем `tasktracker`  

Шаг 3. Настроить строку подключения

В корне проекта создай файл .env:

DATABASE_URL=postgresql+asyncpg://postgres:ПАРОЛЬ@localhost:5432/tasktracker

Шаг 4. Применить миграции

alembic upgrade head

После этого в базе появятся таблицы

Шаг 5. Запустить приложение

uvicorn app.main:app --reload

Приложение будет доступно по адресу http://127.0.0.1:8000
Swagger http://127.0.0.1:8000/docs