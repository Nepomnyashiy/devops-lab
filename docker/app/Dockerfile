# Базовый образ с Python. slim — меньше размер, быстрее скачивание.
FROM python:3.12-slim

# Создаём непривилегированного пользователя — базовая мера безопасности.
RUN useradd -m appuser
WORKDIR /app

# Устанавливаем зависимости отдельно, чтобы использовать слой кеша.
COPY docker/app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем исходники.
COPY docker/app /app

# Не запускаем от root.
USER appuser

ENV PORT=5000
EXPOSE 5000

# Запускаем приложение.
CMD ["python", "app.py"]
