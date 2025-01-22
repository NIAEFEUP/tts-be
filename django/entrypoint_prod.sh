#!/bin/bash

# Waits for PostgreSQL initialization.
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" "${POSTGRES_DB}" -c 'select 1'; do
	>&2 echo "PostgreSQL is unavailable - sleeping"
	sleep 4
done
>&2 echo "PostgreSQL is up - executing command"

# Compile protobuf files
echo "Compiling protobuf files..."
protoc --python_out=generated -I=./protos/ ./protos/**/*.proto
echo "Protobuf files compiled successfully."

# Migrate the Django.
python manage.py inspectdb >university/models.py
python manage.py makemigrations
python manage.py migrate
python manage.py migrate university --fake

python manage.py runserver 0.0.0.0:8000
