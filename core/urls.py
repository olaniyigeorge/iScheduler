
from django.urls import path
from .views import *

urlpatterns = [
    path("", Index.as_view(), name="index"),

    # --- Core ---
    path("user/<int:pk>", UserDetail.as_view(), name="user"),
    path("tasks/<int:user>", TasksByUser.as_view(), name="tasks"),
    path("task/<int:pk>", TasksDetail.as_view(), name="tasks"),
    path("schedule/<int:user>", MySchedule.as_view(), name="schedule"),

    # --- Celery Test ---
    path("with", with_celery, name="with"),
    path("without", without_celery, name="without"),
]