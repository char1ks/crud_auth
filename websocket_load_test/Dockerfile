FROM ubuntu:22.04

# Избегаем интерактивных запросов при установке
ENV DEBIAN_FRONTEND=noninteractive

# Обновляем пакеты и устанавливаем необходимые утилиты
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nodejs \
    npm \
    htop \
    bmon \
    net-tools \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Artillery глобально
RUN npm install -g artillery

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .
COPY websocket.py .
COPY websocket_empty.py .
COPY test_config.yml .
COPY README.md .

# Устанавливаем Python зависимости
RUN pip3 install -r requirements.txt

# Открываем порт для WebSocket сервера
EXPOSE 8765

# Запускаем bash по умолчанию для интерактивной работы
CMD ["/bin/bash"] 