from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import redis
from celery.schedules import crontab
from kombu import Queue, Exchange

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iScheduler.settings')

app = Celery('iScheduler')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

nodes = [
    "node-1",
    "node-2",
]

CELERY_TASK_QUEUES = []
CELERY_BEAT_SCHEDULE = {}
for node in nodes:
    CELERY_TASK_QUEUES.append(
        Queue(node, Exchange(node), routing_key=node),
    )



CELERY_BEAT_SCHEDULE = {
    # Tasks for node-1
    "make-todays-schedule": {
        "task": "core.tasks.generate_todays_schedule",
        "schedule": 30.0,  # crontab(minute=0, hour=0,)   --- Midnight, 1st of the month
        "options": {"queue": "node-1"},
    },
    "create-schedule-every-week": {
        "task": "core.tasks.create_schedule_for_week",
        "schedule": crontab(minute=0, hour=0, day_of_week=0),  # Midnight, Sunday
        "options": {"queue": "node-1"},
    },
    # "create-schedule-every-month": {
    #     "task": "your_app.tasks.create_schedule_for_month",
    #     "schedule": crontab(minute=0, hour=0, day_of_month=1),  # Midnight, 1st of the month
    #     "options": {"queue": "node-1"},
    # },
    # # Tasks for node-2
    # "create-schedule-every-day": {
    #     "task": "your_app.tasks.create_schedule_for_today",
    #     "schedule": crontab(minute=0, hour=0),  # Midnight, every day
    #     "options": {"queue": "node-2"},
    # },
    # "create-schedule-every-week": {
    #     "task": "your_app.tasks.create_schedule_for_week",
    #     "schedule": crontab(minute=0, hour=0, day_of_week=0),  # Midnight, Sunday
    #     "options": {"queue": "node-2"},
    # },
}


app.conf.task_queues = CELERY_TASK_QUEUES
# celery -A cfehome worker -Q node-2 -l info
# celery -A cfehome beat -l info
app.conf.beat_schedule = CELERY_BEAT_SCHEDULE


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    
