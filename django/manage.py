#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from tasks import add


def main():
    if (sys.argv[1] == "runserver"):
        add.delay(4, 4)

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tts_be.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def dump_statistics():
    command = "mysqldump -P {} -h db -u {} -p{} {} statistics > statistics.sql".format(
        os.environ["MYSQL_PORT"],
        os.environ["MYSQL_USER"],
        os.environ["MYSQL_PASSWORD"],
        os.environ["MYSQL_DATABASE"])
    os.system(command)

if __name__ == '__main__':
    main()
