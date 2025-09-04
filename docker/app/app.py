# Минимальное Flask-приложение.
# Почему Flask: быстрый старт, небольшой вес, удобно демонстрировать healthcheck и метрики.
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.get("/health")
def health():
    # Healthcheck endpoint для Kubernetes/NGINX и скриптов мониторинга
    return jsonify(status="ok")

@app.get("/env")
def env():
    # Демонстрация работы с переменными окружения (ConfigMap/Secrets)
    return jsonify(app_env=os.getenv("APP_ENV", "dev"))

if __name__ == "__main__":
    # 0.0.0.0 важно для доступа извне контейнера
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
