from flask import Flask, jsonify, Response
import os
# Экспорт метрик Prometheus
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUESTS = Counter('app_requests_total', 'Total HTTP requests', ['endpoint'])

@app.get("/health")
def health():
    REQUESTS.labels('/health').inc()
    return jsonify(status="ok")from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import create_engine, text
import time
import os
import random

app = Flask(__name__)

# --- Настройка метрик ---
REQUESTS = Counter("http_requests_total", "Total requests", ["method", "endpoint"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["endpoint"])

# --- Настройка базы ---
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/appdb")
engine = create_engine(DB_URL, pool_pre_ping=True)

# --- Маршруты ---
@app.route("/health")
def health():
    REQUESTS.labels("GET", "/health").inc()
    return jsonify(status="ok")

@app.route("/items", methods=["GET", "POST"])
def items():
    start = time.time()
    if request.method == "POST":
        name = request.json.get("name", f"item-{random.randint(1,1000)}")
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO items(name) VALUES (:name)"), {"name": name})
        REQUESTS.labels("POST", "/items").inc()
        LATENCY.labels("/items").observe(time.time() - start)
        return jsonify(message="created", name=name), 201
    else:
        with engine.begin() as conn:
            rows = conn.execute(text("SELECT id, name FROM items ORDER BY id DESC LIMIT 10")).fetchall()
        REQUESTS.labels("GET", "/items").inc()
        LATENCY.labels("/items").observe(time.time() - start)
        return jsonify([{"id": r[0], "name": r[1]} for r in rows])

@app.route("/compute")
def compute():
    start = time.time()
    n = int(request.args.get("n", 32))  # по умолчанию 32-е число Фибоначчи
    def fib(x):
        return x if x <= 1 else fib(x-1) + fib(x-2)
    result = fib(n)
    REQUESTS.labels("GET", "/compute").inc()
    LATENCY.labels("/compute").observe(time.time() - start)
    return jsonify(n=n, fib=result)

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))


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
