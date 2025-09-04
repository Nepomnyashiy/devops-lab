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

# DevOps Lab

Учебный проект, демонстрирующий навыки DevOps-инженера: контейнеризация, CI/CD, инфраструктура как код, мониторинг и автоматизация.

---

## Цели проекта
- Показать практический опыт работы с Docker, Kubernetes, Ansible, CI/CD, Prometheus, Grafana, Loki.
- Создать демонстрационный стенд, который можно развернуть локально или в облаке.
- Продемонстрировать умение строить инфраструктуру как код (IaC).

---

## Технологии
- Контейнеризация и оркестрация: Docker, Docker Compose, Kubernetes
- CI/CD: GitHub Actions, GitLab CI/CD
- IaC: Ansible
- Мониторинг и логирование: Prometheus, Grafana, Loki, Promtail
- Языки: Python, Bash
- Базы данных: PostgreSQL
- Сетевые сервисы: Nginx (reverse proxy)

---

## Структура репозитория
```
devops-lab/
│── README.md              # Описание проекта
│── docker/                # Dockerfile и образы
│   ├── app/               # Пример Python-сервиса
│   ├── db/                # PostgreSQL с init-скриптами
│   └── nginx/             # Nginx reverse-proxy
│── k8s/                   # Kubernetes манифесты
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap-secret.yaml
│── ansible/               # Playbooks для серверов
│   ├── install_docker.yml
│   ├── deploy_app.yml
│   └── monitor.yml
│── cicd/                  # CI/CD pipeline
│   ├── github-actions.yml
│   └── gitlab-ci.yml
│── monitoring/            # Prometheus + Grafana + Loki
│   ├── prometheus.yml
│   ├── grafana-dashboards/
│   └── loki-config.yml
│── scripts/               # Bash и Python для автоматизации
│   ├── backup.sh
│   ├── cleanup_logs.sh
│   └── healthcheck.py
```

---

## Быстрый старт
### Запуск с Docker Compose
```bash
git clone https://github.com/username/devops-lab.git
cd devops-lab
docker-compose up -d
```

### Деплой в Kubernetes
```bash
kubectl apply -f k8s/
```

### Ansible
```bash
ansible-playbook ansible/install_docker.yml
ansible-playbook ansible/deploy_app.yml
```

---

## Мониторинг
- Prometheus собирает метрики (CPU, RAM, network).
- Grafana визуализирует дашборды.
- Loki + Promtail собирают логи.

Примеры дашбордов находятся в папке `monitoring/grafana-dashboards`.

---

## Автоматизация
- `scripts/backup.sh` — резервное копирование PostgreSQL.
- `scripts/cleanup_logs.sh` — очистка старых логов.
- `scripts/healthcheck.py` — проверка доступности API.

---

## Лицензия
MIT License
