# Используем официальный Python образ на базе Alpine для меньшего размера
FROM python:3.9-alpine3.16

# Устанавливаем необходимые пакеты для компиляции и PostgreSQL
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev \
    build-base

# Копируем только файл зависимостей сначала, чтобы избежать их переустановки
COPY requirements.txt /temp/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /temp/requirements.txt

# Копируем исходный код проекта (папку service) после установки зависимостей
COPY service /service

# Устанавливаем рабочую директорию в /service
WORKDIR /service

# Открываем порт для приложения
EXPOSE 8000

# Создаем пользователя для контейнера
RUN adduser --disabled-password service-user

# Переключаемся на созданного пользователя
USER service-user

