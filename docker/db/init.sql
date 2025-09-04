-- Инициализация схемы для демонстрации CRUD
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
-- Существующая демо-таблица из прежнего примера (если была) — оставляем:
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    message TEXT
);
INSERT INTO notes (message) VALUES ('hello from init.sql') ON CONFLICT DO NOTHING;
