devops-lab/
│── README.md              # Подробное описание проекта
│── docker/                # Dockerfile и образы
│   ├── app/               # Пример Python/Django/Flask сервиса
│   ├── db/                # PostgreSQL с инициализацией
│   └── nginx/             # Nginx как reverse-proxy
│── k8s/                   # Kubernetes манифесты
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap-secret.yaml
│── ansible/               # Playbooks для серверов
│   ├── install_docker.yml
│   ├── deploy_app.yml
│   └── monitor.yml
│── cicd/                  # CI/CD pipeline (GitHub Actions/GitLab CI)
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
