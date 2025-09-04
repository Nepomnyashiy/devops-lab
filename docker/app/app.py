from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import create_engine, text
import os, time, random

app = Flask(__name__)

# ---- Metrics ----
REQ = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "code"])
LAT = Histogram("http_request_duration_seconds", "Request latency seconds", ["endpoint"])

# ---- Database ----
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/appdb")
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

# ---- Helpers ----
def record(endpoint, method, code, start_time):
    REQ.labels(method, endpoint, str(code)).inc()
    LAT.labels(endpoint).observe(time.time() - start_time)

# ---- Routes ----
@app.get("/health")
def health():
    start = time.time()
    payload = {"status": "ok"}
    record("/health", "GET", 200, start)
    return jsonify(payload), 200

@app.get("/env")
def env():
    start = time.time()
    payload = {"app_env": os.getenv("APP_ENV", "dev")}
    record("/env", "GET", 200, start)
    return jsonify(payload), 200

@app.route("/items", methods=["GET", "POST"])
def items():
    start = time.time()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name") or f"item-{random.randint(1000, 9999)}"
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO items(name) VALUES (:name)"), {"name": name})
        record("/items", "POST", 201, start)
        return jsonify({"message": "created", "name": name}), 201
    else:
        with engine.begin() as conn:
            rows = conn.execute(text("SELECT id, name FROM items ORDER BY id DESC LIMIT 10")).all()
        out = [{"id": r[0], "name": r[1]} for r in rows]
        record("/items", "GET", 200, start)
        return jsonify(out), 200

@app.get("/compute")
def compute():
    start = time.time()
    n = int(request.args.get("n", "32"))
    def fib(x):
        return x if x <= 1 else fib(x-1) + fib(x-2)
    res = fib(n)
    record("/compute", "GET", 200, start)
    return jsonify({"n": n, "fib": res}), 200

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))