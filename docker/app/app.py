from flask import Flask, jsonify, Response
import os
# Экспорт метрик Prometheus
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUESTS = Counter('app_requests_total', 'Total HTTP requests', ['endpoint'])

@app.get("/health")
def health():
    REQUESTS.labels('/health').inc()
    return jsonify(status="ok")

@app.get("/env")
def env():
    REQUESTS.labels('/env').inc()
    return jsonify(app_env=os.getenv("APP_ENV", "dev"))

@app.get("/metrics")
def metrics():
    # Стандартная точка экспорта метрик для Prometheus
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
