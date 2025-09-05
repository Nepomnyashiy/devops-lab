#!/usr/bin/env python3
"""
Интеграционный тест devops-lab:
- Проверка модулей (импорт и версии)
- Проверка API: /health, /env, /metrics
- CRUD-сценарий: POST /items -> GET /items
- Проверка доступности pgAdmin (/misc/ping или /login)

Параметры окружения:
  BASE_URL            (по умолчанию http://localhost:8000)
  PGADMIN_URL         (по умолчанию http://localhost:5050)
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

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
PGADMIN_URL = os.getenv("PGADMIN_URL", "http://localhost:5050")
TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5"))
RETRIES = int(os.getenv("HTTP_RETRIES", "5"))
RETRY_DELAY = float(os.getenv("HTTP_RETRY_DELAY", "0.8"))

def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def require(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)

def http_get(session: requests.Session, url: str) -> requests.Response:
    last = None
    for _ in range(RETRIES):
        try:
            return session.get(url, timeout=TIMEOUT)
        except Exception as e:
            last = e
            time.sleep(RETRY_DELAY)
    raise last

def http_post_json(session: requests.Session, url: str, payload: dict) -> requests.Response:
    last = None
    for _ in range(RETRIES):
        try:
            return session.post(url, json=payload, timeout=TIMEOUT)
        except Exception as e:
            last = e
            time.sleep(RETRY_DELAY)
    raise last

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
    modules = ["flask", "prometheus_client", "requests", "sqlalchemy", "psycopg2"]
    ok_all = True
    for name in modules:
        ok, info = mod_info(name)
        print(f"[{'OK' if ok else 'FAIL'}] {name} (version: {info})")
        ok_all = ok_all and ok
    require(ok_all, "Не все требуемые модули импортируются")

def test_api():
    print_section("Проверка API: /health, /env, /metrics")
    with requests.Session() as s:
        r = http_get(s, f"{BASE_URL}/health")
        require(r.status_code == 200, f"/health -> HTTP {r.status_code}")
        data = r.json()
        require(data.get("status") == "ok", f"/health payload: {data}")
        print("[OK] /health")

        r = http_get(s, f"{BASE_URL}/env")
        require(r.status_code == 200, f"/env -> HTTP {r.status_code}")
        data = r.json()
        require("app_env" in data, f"/env payload: {data}")
        print("[OK] /env")

        r = http_get(s, f"{BASE_URL}/metrics")
        require(r.status_code == 200, f"/metrics -> HTTP {r.status_code}")
        text = r.text
        require("python_gc_objects_collected_total" in text or "process_cpu_seconds_total" in text,
                "В /metrics не найдены ожидаемые базовые метрики")
        print("[OK] /metrics")

def test_crud_items():
    print_section("Сценарий: POST /items -> GET /items")
    uniq = f"loadtest-{uuid.uuid4().hex[:8]}"
    with requests.Session() as s:
        r = http_post_json(s, f"{BASE_URL}/items", {"name": uniq})
        require(r.status_code in (200, 201), f"POST /items -> HTTP {r.status_code}, body={r.text}")
        r = http_get(s, f"{BASE_URL}/items")
        require(r.status_code == 200, f"GET /items -> HTTP {r.status_code}")
        arr = r.json()
        require(any(isinstance(it, dict) and it.get("name") == uniq for it in arr),
                f"Запись {uniq} не найдена в ответе GET /items")
        print("[OK] CRUD /items")

def test_pgadmin():
    print_section("Проверка pgAdmin")
    with requests.Session() as s:
        try:
            r = http_get(s, f"{PGADMIN_URL}/misc/ping")
            if r.status_code == 200:
                print("[OK] pgAdmin /misc/ping = 200")
                return
        except Exception:
            pass
        r = http_get(s, f"{PGADMIN_URL}/login")
        require(r.status_code == 200, f"pgAdmin /login -> HTTP {r.status_code}")
        require("pgAdmin" in r.text or "pgadmin" in r.text.lower(),
                "Страница /login не похожа на pgAdmin")
        print("[OK] pgAdmin /login = 200")

if __name__ == "__main__":
    try:
        print(f"BASE_URL={BASE_URL}  PGADMIN_URL={PGADMIN_URL}  TIMEOUT={TIMEOUT}s  RETRIES={RETRIES}")
        test_modules()
        test_api()
        test_crud_items()
        test_pgadmin()
        print("\n✅ Все проверки пройдены успешно.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
