from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import Schedule, Task, User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "username", "email", "first_name", "last_name", "bio", "is_staff")
    search_fields = ("username", "email")

admin.site.register(User, CustomUserAdmin)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "apprx_duration", "status", "start_dt",  "expires")
    list_filter = ("priority", "status")
    search_fields = ("name", "description")

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("user", "duration", "start_date", "tasks_count")
    list_filter = ("start_date", "duration",)
    search_fields = ("user__username",)