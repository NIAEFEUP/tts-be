#!/bin/bash

# Waits for PostgreSQL initialization.
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" "${POSTGRES_DB}" -c 'select 1'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 4
done
>&2 echo "PostgreSQL is up - executing command"

# Migrate the Django.
python manage.py makemigrations # default django migrations
python manage.py makemigrations university
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
