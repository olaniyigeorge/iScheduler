from django.http import JsonResponse
from django.shortcuts import render

from core.tasks import waiting



def index(request):
    return JsonResponse({"name": "iScheduler"})


def with_celery(request):
    w= waiting.delay(5)
    return JsonResponse({"With": "With celery"})


def without_celery(request):
    w= waiting(5)
    return JsonResponse({"Without": "Without celery"})