FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директории для базы данных
RUN mkdir -p /app/database

# Команда для запуска приложения
CMD ["python", "main.py"]