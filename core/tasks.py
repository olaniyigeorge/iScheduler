import time
from celery import shared_task


@shared_task
def waiting(num: int):
    time.sleep(num)
    return f"Waited for {num} secs"
