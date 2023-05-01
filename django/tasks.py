from celery import Celery
from celery.schedules import crontab
import os

app = Celery('tasks', broker="redis://tts-be-redis_service-1:6379")

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute = '0', hour = '0, 12'), 
        dump_statistics.s(), 
        name='dump statistics'
    )

@app.task
def add(x, y):
    return x + y

@app.task
def dump_statistics():
    print("lalau")
    command = "mysqldump -P {} -h db -u {} -p{} {} statistics > statistics.sql".format(
        os.environ["MYSQL_PORT"],
        os.environ["MYSQL_USER"],
        os.environ["MYSQL_PASSWORD"],
        os.environ["MYSQL_DATABASE"])
    os.system(command)
