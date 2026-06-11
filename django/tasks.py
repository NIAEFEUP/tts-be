from celery import Celery
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


