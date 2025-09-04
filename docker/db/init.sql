-- Инициализация демо-таблицы. Почему init.sql: удобный способ показать миграции на старте контейнера.
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    message TEXT
);

INSERT INTO notes (message) VALUES ('hello from init.sql');
