from django.http import JsonResponse
from django.shortcuts import render
import redis
from core.tasks import waiting



def index(request):
    return JsonResponse({"name": "iScheduler"})


def with_celery(request):
    r = redis.Redis(host='localhost', port=6379, db=0)
    print(r.ping())
    w = waiting.delay()
    return JsonResponse({"With": "With celery"})


def without_celery(request):
    w= waiting(5)
    return JsonResponse({"Without": "Without celery"})