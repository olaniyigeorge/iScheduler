from django.urls import reverse
import redis
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.viewsets import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Schedule, Task, User
from core.serializers import ScheduleSerializer, TaskSerializer
from core.tasks import generate_daily_schedules
from django.utils.timezone import now
import timeit

class Index(APIView):

    def get(self, request, format=None):
        if request.user.is_authenticated:
            print("User: ", request.user.id)
            dash =  request.build_absolute_uri(reverse("tasks",args=[1,])) # request.user.id
        else:
            dash = None
        return Response({
            "name": "iScheduler",
            "current_schedule": f"{request.build_absolute_uri(reverse("current_schedule",args=[1,]))}",
            "tasks": f"{request.build_absolute_uri(reverse("tasks",args=[1,]))}",
            "schedules": f"{request.build_absolute_uri(reverse("schedules",args=[1,]))}",
            "with": f"{request.build_absolute_uri(reverse("with"))}",
            "without": f"{request.build_absolute_uri(reverse("without"))}",
        })





# --- User ---
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()



# --- Task ---
class TasksDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


    def get_queryset(self):
        return super().get_queryset()

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
class MySchedules(generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer
    lookup_field = "user"

    def get_queryset(self):
        user_id = self.kwargs.get("user")
        queryset = Schedule.objects.filter(user_id=user_id)
        return queryset
    
class CurrentSchedule(generics.RetrieveAPIView):
    serializer_class = ScheduleSerializer
    lookup_field = "user"


    def get_queryset(self):
        user_id = self.kwargs.get("user") 
        queryset = Schedule.objects.filter(user_id=user_id, start_date=now())
        return queryset
    

def with_celery(request):
    gen = generate_daily_schedules.apply_async(queue='node-1')
    return JsonResponse({"With": "With celery"})

def without_celery(request):
    gen = generate_daily_schedules()
    return JsonResponse({"Without": "Without celery"})


