#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from threading import Thread, Timer
import subprocess
import time

def main():
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
    print("lalau")
    command = "mysqldump -P {} -h db -u {} -p{} {} statistics > statistics.sql".format(
        os.environ["MYSQL_PORT"],
        os.environ["MYSQL_USER"],
        os.environ["MYSQL_PASSWORD"],
        os.environ["MYSQL_DATABASE"])
    os.system(command)


def loop_dump_statistics():
    while (True):
        time.sleep(10)
        #t = Timer(10000, dump_statistics)
        #t.start()
        dump_statistics()


if __name__ == '__main__':
    t1 = Thread(target=loop_dump_statistics, daemon=True)
    t1.start()
    main()
