#!/bin/sh
# entrypoint.sh — waits for PostgreSQL to be ready, runs migrations, then starts the app.
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-inventory_user}"; do
  echo "PostgreSQL is unavailable — sleeping 1s"
  sleep 1
done

echo "PostgreSQL is ready. Running Alembic migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
