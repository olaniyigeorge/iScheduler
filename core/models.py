from datetime import timedelta
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
import uuid


# User
class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    notification_preferences = models.JSONField(default=dict, blank=True)  # Email, push, SMS preferences
    working_hours_start = models.TimeField(default="09:00:00")  # Defaults to 9 AM
    working_hours_end = models.TimeField(default="17:00:00")    # Defaults to 5 PM

    def __str__(self):
        return self.username
 
# Task
class Task(models.Model):
    PRIORITY = (
        (1, "Very Important"),
        (2, "Mildly Important"),
        (3, "Important"),
        (4, "Less Important"),
        (5, "Not Important"),
    )
    STATUS = (
        ("pending", "Pending"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
        ("missed", "Missed"),
    )
    
    name = models.CharField(max_length=300)
    description = models.TextField(default="", blank=True)
    priority = models.IntegerField(choices=PRIORITY, default=3)
    status = models.CharField(max_length=14, choices=STATUS, default="pending")
    
    apprx_duration =  models.DurationField(default=timedelta(minutes=30), help_text="Approximate duration in minutes")
    start_dt = models.DateTimeField(default=now)
    expires = models.DateTimeField(default=None, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    external_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID from an external system (e.g., Google Calendar)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notification flags
    notified = models.BooleanField(default=False) 
    push_notified = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.expires:
            self.expires = self.start_dt + self.apprx_duration
        super().save(*args, **kwargs)

    def clean(self):
        if self.expires and self.expires <= self.start_dt:
            self.expires = self.start_dt + self.apprx_duration
            # raise ValidationError("Expiry date must be after start date.")
        super().clean()

    def is_available(self):
        today = now()
        # Ensure `start_dt` is before `today` and `end_dt` is after `today`
        is_available = (
            self.status == "pending" and 
            self.start_dt <= today <= self.expires
        )
        return is_available
         
    class Meta:
        ordering = ["start_dt", "priority", "apprx_duration"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["start_dt", "expires"]),
        ]

# Schedule
class Schedule(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    tasks = models.ManyToManyField(Task, related_name="schedules", blank=True)

    # timestamps
    start_date = models.DateField(default=now)  # The starting date of the schedule
    duration = models.IntegerField(default=1, help_text="Duration in days")  # Duration in days -- min=1, max=366
    end_date = models.DateField(default=None, blank=True, null=True)  # Automatically calculated end date
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + timedelta(days=self.duration)
        super().save(*args, **kwargs)

    def validate_task_durations(self):
        total_minutes = self.duration * 24 * 60
        tasks_duration = sum(task.apprx_duration.total_seconds() / 60 for task in self.tasks.all())
        if tasks_duration > total_minutes:
            raise ValidationError("Total task duration exceeds the available schedule duration.")
        return True

    def __str__(self):
        return f"{self.user.username.title()}'s Schedule ({self.start_date} to {self.end_date})"
    
    def tasks_count(self):
        return self.tasks.count()

    class Meta:
       unique_together = ("user", "start_date") 
       ordering = ["created_at"]

