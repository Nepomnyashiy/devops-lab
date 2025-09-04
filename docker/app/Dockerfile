FROM python:3.12-slim

# Создаём пользователя и рабочую директорию
RUN useradd -m appuser
WORKDIR /app

# Ставим зависимости как root (системно) — бинарь gunicorn окажется в /usr/local/bin
COPY docker/app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем код
COPY docker/app /app

# Дальше работаем непривилегированным пользователем
USER appuser

# На всякий случай добавим ~/.local/bin в PATH (полезно для будущих pip --user)
ENV PATH="/home/appuser/.local/bin:${PATH}" \
    PORT=5000

EXPOSE 5000

# Запуск под gunicorn — стабильнее dev-сервера Flask
CMD ["gunicorn","-w","2","--threads","4","-b","0.0.0.0:5000","app:app"]
