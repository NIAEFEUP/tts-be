from celery import Celery
from celery.schedules import crontab
import os

app = Celery('tasks', broker="redis://tts-be-redis_service-1:6379")

# Gets called after celery sets up. Creates a worker that runs the dump_statistics function at midnight and noon everyday
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='0', hour='0, 12'),
        dump_statistics.s(), 
        name='dump statistics'
    )

@app.task
def dump_statistics():
    command = "mysqldump -P {} -h db -u {} -p{} {} statistics > statistics.sql".format(
        os.environ["MYSQL_PORT"],
        os.environ["MYSQL_USER"],
        os.environ["MYSQL_PASSWORD"],
        os.environ["MYSQL_DATABASE"])
    os.system(command)
