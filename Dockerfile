# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код бота в контейнер
COPY . .

# Фейковый healthcheck-сервер (чтобы Render не выкидывал ошибки про порты)
EXPOSE 10000

# Запускаем HTTP-заглушку и бота одновременно
CMD ["sh", "-c", "python3 -m http.server 10000 & python3 main.py"]
