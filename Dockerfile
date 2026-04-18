FROM python:3.12-slim

ARG SECRET_KEY=dummy-key-for-build

ENV SECRET_KEY=$SECRET_KEY

# Устанавливаем системные зависимости для PostgreSQL и Poetry
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости без виртуального окружения
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копируем весь проект
COPY . .

# Собираем статику
RUN python manage.py collectstatic --noinput

# Создаем entrypoint скрипт
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput\n\
exec gunicorn config.wsgi:application -w 4 -b 0.0.0.0:8000' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]