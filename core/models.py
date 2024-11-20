from datetime import timedelta
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from timescale.db.models.fields import TimescaleDateTimeField
# User
class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)

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
    )
    
    name = models.CharField(max_length=300)
    description = models.TextField(default="", blank=True)
    priority = models.IntegerField(choices=PRIORITY, default=3)
    status = models.CharField(max_length=14, choices=STATUS, default="pending")
    
    apprx_duration =  models.IntegerField(default=60, help_text="Approximate duration in minutes")
    start_dt = models.DateTimeField(default=now)  # Defaults to now
    expires = models.DateTimeField()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def is_available(self):
        today = now()
        # Ensure `start_dt` is before `today` and `end_dt` is after `today`
        is_available = (
            self.status == "pending" and 
            self.start_dt <= today <= self.end_dt
        )
        return is_available
        
    def clean(self):
        if self.end_dt <= self.start_dt:
            raise ValidationError("End date must be after start date.")

    class Meta:
        ordering = ["priority", "start_dt"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["start_dt", "end_dt"]),
        ]


# Schedule
class Schedule(models.Model):
    DURATION_CHOICES = (
        (1, "1 Day"),
        (7, "1 Week"),
        (30, "1 Month"),
        (365, "1 Year"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    tasks = models.ManyToManyField(Task, related_name="schedules", blank=True)


    # timestamps
    duration = models.IntegerField(choices=DURATION_CHOICES)  # Duration in days (1, 7, 30, 365)
    time_frame = models.CharField(max_length=10, choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')], default='day')

    start_date = models.DateField()  # The starting date of the schedule
    end_date = models.DateField()  # Automatically calculated end date
    
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        # Automatically calculate end_date based on the duration and time_frame
        if not self.end_date:
            if self.time_frame == 'day':
                self.end_date = self.start_date + timedelta(days=self.duration)
            elif self.time_frame == 'week':
                self.end_date = self.start_date + timedelta(weeks=self.duration)
            elif self.time_frame == 'month':
                self.end_date = self.start_date + timedelta(days=self.duration * 30)  # Approximation for months
            elif self.time_frame == 'year':
                self.end_date = self.start_date + timedelta(days=self.duration * 365)  # Approximation for years

        # Ensure total task duration doesn't exceed schedule duration
        if self.tasks.exists():
            total_task_duration = sum(task.estimated_duration_minutes for task in self.tasks.all())
            available_duration_minutes = (self.end_date - self.start_date).days * 24 * 60  # Total minutes in the schedule

            if total_task_duration > available_duration_minutes:
                raise ValidationError("Total task duration exceeds the available duration of the schedule.")

        super(Schedule, self).save(*args, **kwargs)

    def __str__(self):
        return f"Schedule for {self.user.username} from {self.start_date} to {self.end_date}"

    class Meta:
        unique_together = ("user", "date")
        ordering = ["date"]

