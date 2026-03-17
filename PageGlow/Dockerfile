FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN groupadd -r django && useradd -r -g django django

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Установка рабочей директории
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt gunicorn

# Копирование проекта
COPY . .

# Создание директорий для статики и медиа
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Сбор статики
RUN python manage.py collectstatic --noinput || true

# Изменение владельца файлов
RUN chown -R django:django /app

# Переключение на непривилегированного пользователя
USER django

# Expose порт
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "--config", "gunicorn_config.py", "PageGlow.wsgi:application"]
