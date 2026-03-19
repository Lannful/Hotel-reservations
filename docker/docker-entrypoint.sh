#!/bin/bash
set -e

echo "Preparing application environment..."

# Проверка обязательных переменных
: "${POSTGRES_USER:?Need to set POSTGRES_USER}"
: "${POSTGRES_DB:?Need to set POSTGRES_DB}"

# Можно добавить другие проверки
# например: : "${SECRET_KEY:?Need to set SECRET_KEY}"

echo "Waiting for PostgreSQL..."

until pg_isready -h db -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"; do
  echo "PostgreSQL is not ready — sleeping..."
  sleep 2
done

echo "PostgreSQL is ready"

echo "Running migrations..."
alembic upgrade head

echo "📊 Preparing Prometheus multiprocess dir..."
mkdir -p /tmp/prometheus
rm -rf /tmp/prometheus/*
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus

echo "Starting application..."

exec gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000



