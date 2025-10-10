# Базовый образ Python
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пользователя для запуска приложения
RUN useradd --create-home --shell /bin/bash bot_user && \
    chown -R bot_user:bot_user /app
USER bot_user

# Установка переменных окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "main.py"]

# Метаданные
LABEL maintainer="your-email@example.com"
LABEL description="Telegram Sales Bot with AI"
LABEL version="1.0.0"