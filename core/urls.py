
from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("with", with_celery, name="with"),
    path("without", without_celery, name="without"),
]