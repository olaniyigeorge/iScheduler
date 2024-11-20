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
    list_display = ("name", "user", "priority", "status", "start_dt",  "end_dt")
    list_filter = ("priority", "status")
    search_fields = ("name", "description")

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "created_at")
    list_filter = ("date",)
    search_fields = ("user__username",)