from datetime import timedelta
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
import uuid
# User
class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
    




# Task

def_task_duration = timedelta(minutes=30)
expiry = def_task_duration + now()
print("Default Duration: ", def_task_duration+now())

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
    
    apprx_duration =  models.DurationField(default=def_task_duration, help_text="Approximate duration in minutes")
    start_dt = models.DateTimeField(default=now)  # Defaults to now
    expires = models.DateTimeField(default=expiry)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        self.expires = self.start_dt + self.apprx_duration
        super(Task, self).save(*args, **kwargs)
    
    def is_available(self):
        today = now()
        # Ensure `start_dt` is before `today` and `end_dt` is after `today`
        is_available = (
            self.status == "pending" and 
            self.start_dt <= today <= self.expires
        )
        return is_available
        
    def clean(self):
        if self.expires:
            if self.expires <= self.start_dt:
                raise ValidationError("Expiry date must be after start date.")
        

    class Meta:
        ordering = ["priority", "start_dt"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["start_dt", "expires"]),
        ]


# Schedule

def_end_date = timedelta(hours=24) + now()
class Schedule(models.Model):

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    tasks = models.ManyToManyField(Task, related_name="schedules", blank=True)

    # timestamps
    duration = models.IntegerField(default=1, help_text="Duration in days")  # Duration in days -- min=1, max=366
    start_date = models.DateField(default=now)  # The starting date of the schedule
    end_date = models.DateField(default=def_end_date)  # Automatically calculated end date
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        # Automatically calculate end_date based on the duration and time_frame
        self.end_date = self.start_date + timedelta(days=self.duration)  # Approximation for years

        # Ensure total task duration doesn't exceed schedule duration only after the schedule has been created(has id)
        # if self.id and self.tasks.exists():
        #     total_task_duration = sum(task.apprx_duration for task in self.tasks.all())
        #     available_duration_minutes = (self.end_date - self.start_date).days * 24 * 60  # Total minutes in the schedule

        #     if total_task_duration > available_duration_minutes:
        #         raise ValidationError("Total task duration exceeds the available duration of the schedule.")

        super(Schedule, self).save(*args, **kwargs)

    def tasks_count(self):
        return self.tasks.count()

    def __str__(self):
        return f"{self.user.username.title()}'s Schedule for from {self.start_date} to {self.end_date}"

    class Meta:
       unique_together = ("user", "duration", "start_date") 
       ordering = ["created_at"]

