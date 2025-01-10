import time
from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from .models import User, Task, Schedule
from django.db.models import Prefetch


# Create schedule and po[ulate with pending tasks
@shared_task
def generate_daily_schedules():
    today = now().date()
    total_minutes = 24 * 60  # 1 day in minutes

    # Prefetch tasks for all users in a single query
    users_with_tasks = User.objects.prefetch_related(
        Prefetch(
            'tasks', 
            queryset=Task.objects.filter(status="pending").order_by("priority"),
            to_attr='pending_tasks'
        )
    )    
    schedules_to_create = []
    schedules_to_update = []

    # Iterate through users and their prefetched tasks
    for user in users_with_tasks:
        # Get or create schedule
        schedule, created = Schedule.objects.get_or_create(
            user=user, 
            start_date=today, 
            defaults={'duration': 1}
        )

        used_minutes = 0
        tasks_to_add = []

        for task in getattr(user, 'pending_tasks', []):
            task_minutes = task.apprx_duration.total_seconds() / 60
            if used_minutes + task_minutes <= total_minutes:
                tasks_to_add.append(task)
                used_minutes += task_minutes
            else:
                break

        if tasks_to_add:
            schedule.tasks.add(*tasks_to_add)

        # Optionally, collect schedules for bulk update (if needed)
        schedules_to_update.append(schedule)

    # Save schedules in bulk if necessary
    Schedule.objects.bulk_update(schedules_to_update, ['duration'])

    return "Daily schedules generated successfully."

@shared_task
def create_schedule_for_week():
    today = now().date()
    total_minutes = 7 * 24 * 60  # 7 day in minutes

    # Prefetch tasks for all users in a single query
    users_with_tasks = User.objects.prefetch_related(
        Prefetch(
            'tasks', 
            queryset=Task.objects.filter(status="pending").order_by("priority"),
            to_attr='pending_tasks'
        )
    )    
    schedules_to_create = []
    schedules_to_update = []

    # Iterate through users and their prefetched tasks
    for user in users_with_tasks:
        # Get or create schedule
        schedule, created = Schedule.objects.get_or_create(
            user=user, 
            start_date=today, 
            defaults={'duration': 7}
        )

        used_minutes = 0
        tasks_to_add = []

        for task in getattr(user, 'pending_tasks', []):
            task_minutes = task.apprx_duration.total_seconds() / 60
            if used_minutes + task_minutes <= total_minutes:
                tasks_to_add.append(task)
                used_minutes += task_minutes
            else:
                break

        if tasks_to_add:
            schedule.tasks.add(*tasks_to_add)

        # Optionally, collect schedules for bulk update (if needed)
        schedules_to_update.append(schedule)

    # Save schedules in bulk if necessary
    Schedule.objects.bulk_update(schedules_to_update, ['duration'])

    return "Weekly schedules generated successfully."

# Notify users about upcoming tasks via multiple channels: email and push notifications.
@shared_task
def notify_upcoming_tasks():
    tasks = Task.objects.filter(
        status="pending", 
        start_dt__range=[now(), now() + timedelta(hours=1)],
        notified=False  # Only select tasks that haven’t been notified
    )
    for task in tasks:
        user = task.user
        # Send email
        print(f"Notified {user.username} about task: {task.name}")
        task.notified = True  # Mark as notified
        task.save(update_fields=["notified"])  # Save only the notified field to reduce overhead

    return f"Notified users about {tasks.count()} upcoming tasks."

@shared_task
def notify_imminent_tasks():
    tasks = Task.objects.filter(
        status="pending", 
        start_dt__range=[now(), now() + timedelta(minutes=15)],
        push_notified=False  # Only select tasks not yet push-notified
    )
    for task in tasks:
        user = task.user
        # Send push notification
        print(f"Push notified {user.username} about task: {task.name}")
        task.push_notified = True  # Mark as push-notified
        task.save(update_fields=["push_notified"])

    return f"Push notified users about {tasks.count()} imminent tasks."

# Integrate with External Systems: Sync with Google Calendar, 
##  Microsoft Outlook, or CRM systems
@shared_task
def sync_with_google_calendar(user_id):
    user = User.objects.get(id=user_id)
    # Fetch Google Calendar events and map them to Task instances
    print(f"Synced tasks for {user.username} with Google Calendar.")


# Analyze user activity and schedule to recommend better scheduling
@shared_task
def analyze_user_habits():
    users = User.objects.all()
    for user in users:
        cancelled_tasks = Task.objects.filter(user=user, status="cancelled").count()
        missed_tasks = Task.objects.filter(user=user, status="missed").count()
        print(f"User: {user.username}, Cancelled: {cancelled_tasks}, Missed: {missed_tasks}")
    return "User habits analyzed."




@shared_task
def generate_todays_schedule():
    users = User.objects.all()
    for user in users:        
        # Create a new schedule for the user (defaulting to 1 day)
        start_date = now().date()
        schedule, created = Schedule.objects.get_or_create(
            user=user,
            start_date=start_date,
            duration=1,  # 1 Day
        )
        
        # Get all tasks for the user that are not completed or cancelled
        tasks = Task.objects.filter(user=user, status="pending")
        # print("Available tasks: ", tasks)
        
        # Sort tasks by priority and allocate them to the schedule
        total_duration = timedelta(days=0)
        for task in tasks:
            if total_duration + task.apprx_duration <= timedelta(minutes=schedule.duration * 24 * 60):
                schedule.tasks.add(task)
                total_duration += task.apprx_duration
        
        schedule.save()

    return f"\n\nSchedule for {user.username} created successfully for {start_date}."




# ----- MISC -----

@shared_task
def create_schedule_for_today():
    today = now().date()
    
    # Loop through all users
    users = User.objects.all()
    
    for user in users:
        # Check if a schedule for today already exists for the user
        schedule, created = Schedule.objects.get_or_create(user=user, start_date=today)
        
        if created:
            print(f"Schedule created for {user.username} on {today}")
        else:
            print(f"Schedule already exists for {user.username} on {today}")

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
                schedule, created = Schedule.objects.get_or_create(user=user, start_date=date)
                if created:
                    print(f"Schedule created for {user.username} on {date}")
            except ValueError:
                # Skip invalid dates (like February 30th)
                continue

@shared_task
def generate_schedule(user_id, time_frame="day", duration=1):
    user = User.objects.get(id=user_id)
    start_date = now().date()

    # Get or create a schedule for the specified duration and time frame
    schedule, created = Schedule.objects.get_or_create(
        user=user,
        start_date=start_date,
        duration=duration,
        time_frame=time_frame
    )

    # Fetch pending tasks not already in the schedule
    tasks = Task.objects.filter(user=user, status="pending").exclude(schedules=schedule).order_by("priority")

    # Total minutes available in the schedule
    total_minutes = schedule.duration * 24 * 60
    used_minutes = 0

    # Reset task start_dt and end_dt intelligently
    current_start_dt = schedule.start_date

    for task in tasks:
        if used_minutes + task.apprx_duration <= total_minutes:
            # Assign new start and end times to the task
            task_start_dt = current_start_dt
            task_end_dt = task_start_dt + timedelta(minutes=task.apprx_duration)

            # Ensure the new end time does not exceed the schedule's end date
            if task_end_dt.date() > schedule.end_date:
                break

            task.start_dt = task_start_dt
            task.end_dt = task_end_dt
            task.save()

            # Add the task to the schedule
            schedule.tasks.add(task)

            # Update the current start time and used minutes
            current_start_dt = task_end_dt
            used_minutes += task.apprx_duration

    schedule.save()
    return f"Schedule for {user.username} ({time_frame}) {'created' if created else 'updated'} successfully."
