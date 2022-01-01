#!bin/sh 

python manage.py inspectdb > university/models.py
python manage.py makemigrations
python manage.py migrate university --fake
exec "$@"