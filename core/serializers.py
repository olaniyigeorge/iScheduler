
from rest_framework import serializers

from core.models import Task, Schedule



class TaskSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "priority",
            "status",
            "apprx_duration",
            "start_dt",
            "expires",
            "user",
            "is_available"   
        ]

    def get_is_available(self, obj):
        return obj.is_available()


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model= Schedule
        fields = "__all__"