# Проверка доступности API. Почему отдельный скрипт: удобно для CI и cron.
import os, sys, urllib.request

url = os.getenv("APP_HEALTH_URL", "http://localhost:8000/health")
try:
    with urllib.request.urlopen(url, timeout=3) as r:
        body = r.read().decode("utf-8")
        print("OK:", body)
        sys.exit(0)
except Exception as e:
    print("FAIL:", e)
    sys.exit(1)
