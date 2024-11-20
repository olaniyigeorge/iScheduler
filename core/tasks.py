from datetime import timedelta
import time
from celery import shared_task


@shared_task
def waiting(num: int = 5):
    time.sleep(num)
    return f"Waited for {num} secs"



@shared_task
def add(x, y):
    return x + y


## **Proposed Tasks**

# Automatically adjust tasks based on priority, 
#       time constraints, 
#       and availability.

# Notify users about upcoming tasks via multiple channels 
#       email and push notifications.

# Integrate with External Systems:
#       Sync with Google Calendar, 
#       Microsoft Outlook, or 
#       CRM systems.

# Analyze user activity to recommend better scheduling 
#       habits or optimize resource allocation 
#       for businesses.



from celery import shared_task
from django.utils.timezone import now
from .models import User, Schedule, Task

from celery import shared_task
from django.utils.timezone import now
from .models import User, Task, Schedule

@shared_task
def generate_daily_schedule(user_id):
    user = User.objects.get(id=user_id)
    
    # Create a new schedule for the user (defaulting to 1 day)
    start_date = now().date()
    schedule = Schedule.objects.create(
        user=user,
        start_date=start_date,
        duration=1,  # 1 Day
        time_frame="day"
    )
    
    # Get all tasks for the user that are not completed or cancelled
    tasks = Task.objects.filter(user=user, status__in=["pending", "done", "cancelled"])
    
    # Sort tasks by priority and allocate them to the schedule
    total_duration = 0
    for task in tasks:
        if total_duration + task.estimated_duration_minutes <= schedule.duration * 24 * 60:
            schedule.tasks.add(task)
            total_duration += task.estimated_duration_minutes
    
    schedule.save()

    return f"Schedule for {user.username} created successfully for {start_date}."

@shared_task
def create_schedule_for_today():
    today = now().date()
    
    # Loop through all users
    users = User.objects.all()
    
    for user in users:
        # Check if a schedule for today already exists for the user
        schedule, created = Schedule.objects.get_or_create(user=user, date=today)
        
        if created:
            print(f"Schedule created for {user.username} on {today}")
        else:
            print(f"Schedule already exists for {user.username} on {today}")

@shared_task
def create_schedule_for_week():
    # Create schedules for a whole week (from today to 6 days after)
    today = now().date()
    users = User.objects.all()
    
    for user in users:
        for i in range(7):  # 7 days from today
            date = today + timedelta(days=i)
            schedule, created = Schedule.objects.get_or_create(user=user, date=date)
            
            if created:
                print(f"Schedule created for {user.username} on {date}")
            else:
                print(f"Schedule already exists for {user.username} on {date}")

@shared_task
def create_schedule_for_month():
    # Create schedules for the whole month
    today = now().date()
    users = User.objects.all()
    
    for user in users:
        # Loop through all days of the current month
        for day in range(1, 32):  # Maximum days in a month
            try:
                date = today.replace(day=day)
                schedule, created = Schedule.objects.get_or_create(user=user, date=date)
                if created:
                    print(f"Schedule created for {user.username} on {date}")
            except ValueError:
                # Skip invalid dates (like February 30th)
                continue



# @shared_task
# def generate_schedule(user_id, time_frame="day", duration=1):
#     from django.utils.timezone import now
#     from datetime import timedelta
#     from .models import User, Task, Schedule

#     user = User.objects.get(id=user_id)
#     start_date = now().date()

#     # Get or create a schedule for the specified duration and time frame
#     schedule, created = Schedule.objects.get_or_create(
#         user=user,
#         start_date=start_date,
#         duration=duration,
#         time_frame=time_frame
#     )

#     # Fetch pending tasks not already in the schedule
#     tasks = Task.objects.filter(user=user, status="pending").exclude(schedules=schedule).order_by("priority")

#     # Total minutes available in the schedule
#     total_minutes = schedule.duration * 24 * 60
#     used_minutes = 0

#     # Reset task start_dt and end_dt intelligently
#     current_start_dt = schedule.start_date

#     for task in tasks:
#         if used_minutes + task.estimated_duration_minutes <= total_minutes:
#             # Assign new start and end times to the task
#             task_start_dt = current_start_dt
#             task_end_dt = task_start_dt + timedelta(minutes=task.estimated_duration_minutes)

#             # Ensure the new end time does not exceed the schedule's end date
#             if task_end_dt.date() > schedule.end_date:
#                 break

#             task.start_dt = task_start_dt
#             task.end_dt = task_end_dt
#             task.save()

#             # Add the task to the schedule
#             schedule.tasks.add(task)

#             # Update the current start time and used minutes
#             current_start_dt = task_end_dt
#             used_minutes += task.estimated_duration_minutes

#     schedule.save()
#     return f"Schedule for {user.username} ({time_frame}) {'created' if created else 'updated'} successfully."
