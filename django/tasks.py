from celery import Celery
from celery.schedules import crontab
import os
from dotenv import dotenv_values

CONFIG={
    **dotenv_values(".env"),  # load variables
    **os.environ,  # override loaded values with environment variables
}

username_password_str = '' 
if os.getenv('TTS_REDIS_USERNAME') != '' and os.getenv('TTS_REDIS_PASSWORD') != '':
    username_password_str = f"{os.getenv('TTS_REDIS_USERNAME')}:{os.getenv('TTS_REDIS_PASSWORD')}@"

app = Celery('tasks', broker=f"redis://{username_password_str}{os.getenv('TTS_REDIS_HOST')}:{os.getenv('TTS_REDIS_PORT')}")

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
