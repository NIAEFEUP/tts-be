from datetime import datetime
from APScheluder.schedulers.background import BackgroundScheduler
from .jobs import stats_caching_job

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(stats_caching_job, 'interval', seconds=10)
    scheduler.start()