#!/bin/sh

# WARNING: The script will not work if formated with CRLF.

# Configure the shell behaviour.
set -e
if [[ "${DEBUG}" == 1 ]]; then
  set -x
fi

# Get parameters.
cmd="$@"

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

# Initialize redis worker for celery and celery's beat scheduler in the background
celery -A tasks worker --loglevel=INFO &
celery -A tasks beat &

# Initializes the API.
exec $cmd
