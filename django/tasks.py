from celery import Celery
from celery.schedules import crontab

app = Celery('tasks', broker="redis://tts-be-redis_service-1:6379")

@app.task
def add(x, y):
    return x + y
