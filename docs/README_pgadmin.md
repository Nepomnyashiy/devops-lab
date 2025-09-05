# PgAdmin Integration (Separate Service)

Этот пакет добавляет **pgAdmin как отдельный контейнер** к вашему стеку и включает healthcheck для Postgres.

## Состав
- `docker-compose.pgadmin.yml` — оверрайд для основного `docker-compose.yml`. Добавляет сервис `pgadmin` и healthcheck для `db`.
- `scripts/test_app.py` — интеграционный тест, который проверяет:
  - модули Python
  - API приложения (`/health`, `/env`, `/metrics`)
  - CRUD `/items` (POST/GET)
  - доступность pgAdmin (`/misc/ping` или `/login`)

## Установка
Распакуйте архив в корень проекта **devops-lab** (рядом с вашим `docker-compose.yml`).

## Запуск
```bash
docker compose -f docker-compose.yml -f docker-compose.pgadmin.yml up -d --build
```

pgAdmin будет доступен по адресу: **http://localhost:5050**  
Учетные данные (можно изменить в `docker-compose.pgadmin.yml`):
```
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin123
```

Подключение к БД в pgAdmin:
- Name: любое (например, devops-lab)
- Host: `db`
- Port: `5432`
- Username: `postgres`
- Password: `postgres`
- Database: `appdb`

## Запуск тестов
Рекомендуется использовать виртуальное окружение Python:
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests
python scripts/test_app.py
```

Переменные окружения:
- `BASE_URL` (по умолчанию `http://localhost:8000`)
- `PGADMIN_URL` (по умолчанию `http://localhost:5050`)
- `HTTP_TIMEOUT`, `HTTP_RETRIES`, `HTTP_RETRY_DELAY`
