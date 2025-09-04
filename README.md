# DevOps Lab

Минимальный стенд для демонстрации навыков DevOps: контейнеризация, CI/CD, IaC и базовый деплой.

## Быстрый старт (Docker Compose)
```bash
docker compose up -d --build
```
После запуска:
- API: http://localhost:8000/health (ожидается `{"status":"ok"}`)
- Nginx проксирует на приложение (демонстрация reverse-proxy).

## Состав
- `docker/` — Dockerfile и конфиги.
- `docker-compose.yml` — запуск сервиса, БД и Nginx.
- `k8s/` — пример манифестов для Kubernetes (деплой, сервис, ингресс).
- `cicd/` — GitHub Actions workflow для сборки и публикации образа.
- `ansible/` — плейбуки для установки Docker и деплоя.
- `scripts/` — утилиты (бэкап, очистка логов, healthcheck).

Все файлы снабжены комментариями «почему именно так». Это важная часть демонстрации решений.
