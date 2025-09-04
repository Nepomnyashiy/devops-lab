#!/usr/bin/env python3
"""
Интеграционный тест devops-lab:
- Проверка модулей (импорт и версии)
- Проверка API: /health, /env, /metrics
- CRUD-сценарий: POST /items -> GET /items (проверка появления записи)
Код выхода: 0 — успех, 1 — ошибка.

Параметры окружения:
  BASE_URL            (по умолчанию http://localhost:8000)
  HTTP_TIMEOUT        (секунды, по умолчанию 5)
  HTTP_RETRIES        (число ретраев, по умолчанию 5)
  HTTP_RETRY_DELAY    (секунды между ретраями, по умолчанию 0.8)
"""

import os
import sys
import time
import uuid
from typing import Tuple

import requests


# -------- Настройки --------
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5"))
RETRIES = int(os.getenv("HTTP_RETRIES", "5"))
RETRY_DELAY = float(os.getenv("HTTP_RETRY_DELAY", "0.8"))


# -------- Утилиты --------
def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def http_get(session: requests.Session, path: str) -> requests.Response:
    last_exc = None
    for _ in range(RETRIES):
        try:
            return session.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
        except Exception as e:
            last_exc = e
            time.sleep(RETRY_DELAY)
    raise last_exc


def http_post_json(session: requests.Session, path: str, payload: dict) -> requests.Response:
    last_exc = None
    for _ in range(RETRIES):
        try:
            return session.post(f"{BASE_URL}{path}", json=payload, timeout=TIMEOUT)
        except Exception as e:
            last_exc = e
            time.sleep(RETRY_DELAY)
    raise last_exc


# -------- Тесты модулей --------
def test_modules():
    print_section("Проверка модулей (импорт и версии)")

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
        "psycopg2",  # модуль один и тот же для psycopg2-binary
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
        # Базовые метрики Python/Prometheus-клиента обычно присутствуют
        require(
            "python_gc_objects_collected_total" in text or "process_cpu_seconds_total" in text,
            "В /metrics не найдены ожидаемые базовые метрики",
        )
        print("[OK] /metrics")


# -------- Тест CRUD через REST --------
def test_items_crud():
    """
    Ожидается, что сервис реализует:
      - POST /items  с JSON {"name": "..."} -> 201 + {"message":"created","name":"..."}
      - GET  /items  -> 200 + [{"id":..,"name":".."}, ...]
    """
    print_section("Сценарий: POST /items -> GET /items (проверка появления записи)")

    uniq_name = f"loadtest-{uuid.uuid4().hex[:8]}"
    with requests.Session() as s:
        # POST /items
        r = http_post_json(s, "/items", {"name": uniq_name})
        require(r.status_code in (200, 201), f"POST /items -> HTTP {r.status_code}, body={r.text}")
        try:
            payload = r.json()
        except Exception:
            payload = {}
        require(
            ("message" in payload and payload.get("message") in ("created", "ok")) or r.status_code == 201,
            f"POST /items: неожиданный ответ {payload}",
        )
        print(f"[OK] POST /items name={uniq_name}")

        # GET /items
        r = http_get(s, "/items")
        require(r.status_code == 200, f"GET /items -> HTTP {r.status_code}")
        arr = r.json()
        require(isinstance(arr, list), f"/items должен возвращать список, получено: {type(arr)}")
        names = [it.get("name") for it in arr if isinstance(it, dict)]
        require(uniq_name in names, f"Запись {uniq_name} не найдена в ответе GET /items: {arr}")
        print("[OK] GET /items содержит новую запись")


# -------- main --------
if __name__ == "__main__":
    try:
        print(f"BASE_URL={BASE_URL}  TIMEOUT={TIMEOUT}s  RETRIES={RETRIES}")
        test_modules()
        test_health_env_metrics()
        test_items_crud()
        print("\n✅ Все проверки пройдены успешно.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
