from celery import Celery
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tts_be.settings'


app = Celery('tts_be')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()