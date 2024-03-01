#!bin/sh

# WARNING: The script will not work if formated with CRLF.

# Configure the shell behaviour.
set -e
if [[ ${DEBUG} == 1 ]]; then
	set -x
fi

# Get parameters.
database_host="$1" # The database host and should be provided the container name.
shift
cmd="$@"

# Waits for mysql initialization.
until mysql -h "$database_host" -u ${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e 'select 1'; do
	echo >&2 "MySQL is unavailable - sleeping"
	sleep 4
done
echo >&2 "Mysql is up - executing command"

# Migrate the Django.
python manage.py inspectdb >university/models.py
python manage.py makemigrations
python manage.py migrate --fake sessions zero
python manage.py migrate university --fake
python manage.py migrate --fake-initial

# Initialize redis worker for celery and celery's beat scheduler in the background
celery -A tasks worker --loglevel=INFO &
celery -A tasks beat &

# Initializes the API.
exec $cmd
