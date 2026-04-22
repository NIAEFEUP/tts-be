#!/bin/sh

# WARNING: Format this file with LF line endings, not CRLF.

set -e

# Wait for PostgreSQL to be ready
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" "${POSTGRES_DB}" -c 'select 1' > /dev/null 2>&1; do
  >&2 echo "Waiting for PostgreSQL..."
  sleep 2
done
>&2 echo "PostgreSQL is up."

# Detect fresh database: django_migrations table missing means nothing has run yet
DB_FRESH=0
TABLE_EXISTS=$(PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" "${POSTGRES_DB}" -tAc \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='django_migrations'")

if [ "$TABLE_EXISTS" = "0" ]; then
  DB_FRESH=1
  >&2 echo "Fresh database detected — running full setup."
else
  >&2 echo "Existing database detected — applying new migrations only."
fi

# Apply migrations (safe to run on existing DB — Django skips already-applied ones)
python manage.py migrate

if [ "$DB_FRESH" = "1" ]; then
  # Load mock exchange/course data
  if [ -f "/mock-data.sql" ]; then
    >&2 echo "Loading mock data..."
    SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
    # Replace the <username> placeholder with the actual admin username
    sed "s/<username>/$SUPERUSER_USERNAME/g" /mock-data.sql | \
      PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" "${POSTGRES_DB}"
    >&2 echo "Mock data loaded."
  else
    >&2 echo "No mock-data.sql found at /mock-data.sql — skipping seed."
  fi

  # Create Django superuser
  if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
    >&2 echo "Creating superuser '${DJANGO_SUPERUSER_USERNAME}'..."
    python manage.py createsuperuser --noinput || true
  fi
fi

exec "$@"
