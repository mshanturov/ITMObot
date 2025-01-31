# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для PyTorch
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    gfortran \
    libopenmpi-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости, включая PyTorch
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install torch

# Копируем исходный код
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение
CMD ["python", "app.py"]
