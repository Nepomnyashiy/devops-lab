#!/usr/bin/env python3
"""
Интеграционный тест devops-lab:
- Проверка модулей (импорт и версии)
- Проверка API: /health, /metrics, /env
- CRUD-сценарий: POST /items -> GET /items (проверка наличия записи)
Код выхода: 0 — успех, 1 — ошибка.
"""

import os
import sys
import json
import time
import uuid
from typing import Tuple

# -------- Настройки --------
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5"))
RETRIES = int(os.getenv("HTTP_RETRIES", "5"))
RETRY_DELAY = float(os.getenv("HTTP_RETRY_DELAY", "1.0"))

# -------- Утилиты --------
def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)

def http_get(session, path: str):
    import requests
    last_exc = None
    for i in range(RETRIES):
        try:
            r = session.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
            return r
        except Exception as e:
            last_exc = e
            time.sleep(RETRY_DELAY)
    raise last_exc

def http_post_json(session, path: str, payload: dict):
    import requests
    last_exc = None
    for i in range(RETRIES):
        try:
            r = session.post(f"{BASE_URL}{path}", json=payload, timeout=TIMEOUT)
            return r
        except Exception as e:
            last_exc = e
            time.sleep(RETRY_DELAY)
    raise last_exc

# -------- Тесты модулей --------
def test_modules():
    print_section("Проверка модулей (импорт и версии)")

    # requests
    import importlib
    def mod_info(name) -> Tuple[bool, str]:
        try:
            m = importlib.import_module(name)
            ver = getattr(m, "__version__", None)
            return True, ver or "unknown"
        except Exception as e:
            return False, str(e)

    modules = [
        "flask",
        "prometheus_client",
        "requests",
        "sqlalchemy",
        "psycopg2"  # может быть psycopg2-binary, но импортный модуль одинаковый
    ]
    ok_all = True
    for name in modules:
        ok, info = mod_info(name)
        print(f"[{'OK' if ok else 'FAIL'}] {name} (version: {info})")
        ok_all = ok_all and ok

    require(ok_all, "Не все требуемые модули установлены/импортируются")

# -------- Тесты API --------
def test_health_env_metrics():
    print_section("Проверка API: /health, /env, /metrics")
    import requests

    with requests.Session() as s:
        # /health
        r = http_get(s, "/health")
        require(r.status_code == 200, f"/health -> HTTP {r.status_code}")
        data = r.json()
        require(data.get("status") == "ok", f"/health payload: {data}")
        print("[OK] /health")

        # /env
        r = http_get(s, "/env")
        require(r.status_code == 200, f"/env -> HTTP {r.status_code}")
        data = r.json()
        require("app_env" in data, f"/env payload: {data}")
        print("[OK] /env")

        # /metrics
        r = http_get(s, "/metrics")
        require(r.status_code == 200, f"/metrics -> HTTP {r.status_code}")
        text = r.text
        # Базовые метрики Python/Prometheus-клиента обычно присутствуют:
