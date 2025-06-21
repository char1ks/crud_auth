FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы приложения
COPY . .

# Явно копируем папку с шаблонами (если она находится в корне проекта)
COPY templates /app/templates
# Экспонируем порт
EXPOSE 5001

# Запускаем приложение
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]