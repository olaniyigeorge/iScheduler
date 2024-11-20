from django.urls import reverse
import redis
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.viewsets import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Schedule, Task, User
from core.serializers import ScheduleSerializer, TaskSerializer
from core.tasks import waiting
from django.utils.timezone import now


class Index(APIView):

    def get(self, request, format=None):
        if request.user.is_authenticated:
            print("User: ", request.user.id)
            dash =  request.build_absolute_uri(reverse("tasks",args=[1,])) # request.user.id
        else:
            dash = None
        return Response({
            "name": "iScheduler",
            "dash": f"{request.build_absolute_uri(reverse("tasks",args=[1,]))}",
            "task": reverse("tasks", args=(1,)),
            "schedule": reverse('schedule', args=(1,)),
            "with": reverse("with"),
            "without": reverse('without'),
        })

def with_celery(request):
    w = waiting.delay()
    return JsonResponse({"With": "With celery"})

def without_celery(request):
    w= waiting(5)
    return JsonResponse({"Without": "Without celery"})




# --- User ---
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()


# --- Task ---
class TasksDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TasksByUser(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    lookup_field = "user"

    def get_queryset(self):
        # Fetch user ID from the URL kwargs
        user_id = self.kwargs.get("user")
        # Start with filtering by user ID
        queryset = Task.objects.filter(user_id=user_id)
        
        # Apply additional filtering based on query parameters
        is_available = self.request.GET.get("is_available")
        if is_available is not None:  # Check if 'is_available' is in the query params
            # Convert 'is_available' to a boolean value and filter accordingly
            queryset = queryset.filter(is_available=is_available.lower() == "true")
        
        return queryset

# --- Schedule ---
class MySchedule(generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer
    lookup_field = "user"

    def get_queryset(self):
        coverage = "today" # 2024-11-19 or 2024-11

        # calculate today's schedule -- 
        # select all tasks where today is within start_dt and end-dt
        user_id = self.kwargs.get("user")  # Fetch user ID from the URL
        queryset = Schedule.objects.filter(user_id=user_id, date=now())

        return queryset