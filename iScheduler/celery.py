from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import redis
from celery.schedules import crontab
# from dotenv import load_dotenv # type: ignore

# load_dotenv()

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iScheduler.settings')

app = Celery('iScheduler')


# Ping redis
# r = redis.Redis(host='localhost', port=6379, db=0)
# print(r.ping())


# Directly set broker URL for testing
app.conf.broker_url = 'redis://localhost:6379/0'


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# app.conf.update(
#     CELERY_BROKER_URL='redis://redis:6379/0',  # Or use the Redis container's name if in Docker
#     CELERY_RESULT_BACKEND='redis://redis:6379/0',  # Same for result backend if you're using one
# )


# Load task modules from all registered Dj  ango apps.
app.autodiscover_tasks()


CELERY_BEAT_SCHEDULE = {
    'test-waiting': {
        'task': 'core.tasks.waiting',
        'schedule': 2,  # Every two seconds
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')