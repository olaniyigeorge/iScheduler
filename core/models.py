from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

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
    start_dt = models.DateTimeField(default=now)  # Defaults to now
    end_dt = models.DateTimeField()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return f"{self.name} ({self.status})"
    
    # def is_available(self):
    #     today = datetime.now()
    #     is_available = self.priority == "pending" and self.start_dt >= today and self.end_dt <= today
    #     print("is avaliable", is_available)
    #     return is_available
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

# Schedule
class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    tasks = models.ManyToManyField(Task, related_name="schedules", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Schedule for {self.user.username} on {self.date}"

    class Meta:
        unique_together = ("user", "date")
        ordering = ["date"]
