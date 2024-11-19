import time
from celery import shared_task


@shared_task
def waiting(num: int = 5):
    time.sleep(num)
    return f"Waited for {num} secs"



@shared_task
def add(x, y):
    return x + y
