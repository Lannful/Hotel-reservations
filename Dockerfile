FROM python:3.12

WORKDIR /booking

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client curl && \
    rm -rf /var/lib/apt/lists/*

# Сначала зависимости (лучше для кеширования)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Копируем entrypoint
COPY docker/docker-entrypoint.sh /booking/docker-entrypoint.sh
RUN chmod +x /booking/docker-entrypoint.sh

ENTRYPOINT ["/booking/docker-entrypoint.sh"]

