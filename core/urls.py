
from django.urls import path
from .views import *

urlpatterns = [
    path("", Index.as_view(), name="index"),

    # --- Core ---
    path("user/<int:pk>", UserDetail.as_view(), name="user"),
    path("tasks/<int:user>", TasksByUser.as_view(), name="tasks"),
    path("task/<int:pk>", TasksDetail.as_view(), name="tasks"),
    path("schedules/<int:user>", MySchedules.as_view(), name="schedule"),

    # --- Celery Test ---
    path("with", with_celery, name="with"),
    path("without", without_celery, name="without"),

    # --- Query Test ---
    path("test", TestQuery.as_view(), name="test"),
]