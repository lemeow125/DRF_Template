import json
import os

from config.settings import ROOT_DIR, SEED_DATA, get_secret
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from .models import CustomUser

# Function to fill in users table with test data on dev/staging


@receiver(post_migrate)
def create_users(sender, **kwargs):
    if sender.name == "accounts":
        with open(os.path.join(ROOT_DIR, "seed_data.json"), "r") as f:
            seed_data = json.loads(f.read())
            for user in seed_data["users"]:
                USER = CustomUser.objects.filter(email=user["email"]).first()
                if not USER:
                    if user["password"] == "USE_REGULAR":
                        password = get_secret("SEED_DATA_PASSWORD")
                    elif user["password"] == "USE_ADMIN":
                        password = get_secret("SEED_DATA_ADMIN_PASSWORD")
                    else:
                        password = user["password"]
                    if user["is_superuser"] == True:
                        # Admin users are created regardless of SEED_DATA value
                        USER = CustomUser.objects.create_superuser(
                            username=user["username"],
                            email=user["email"],
                            password=password,
                        )
                        print("Created Superuser:", user["email"])
                    else:
                        # Only create non-admin users if SEED_DATA=True
                        if SEED_DATA:
                            USER = CustomUser.objects.create_user(
                                username=user["email"],
                                email=user["email"],
                                password=password,
                            )
                            print("Created User:", user["email"])

                    USER.first_name = user["first_name"]
                    USER.last_name = user["last_name"]
                    USER.is_active = True
                    USER.save()


@receiver(post_migrate)
def create_celery_beat_schedules(sender, **kwargs):
    if sender.name == "django_celery_beat":
        with open(os.path.join(ROOT_DIR, "seed_data.json"), "r") as f:
            seed_data = json.loads(f.read())
            # Creating Schedules
            for schedule in seed_data["schedules"]:
                if schedule["type"] == "crontab":
                    # Check if Schedule already exists
                    SCHEDULE = CrontabSchedule.objects.filter(
                        minute=schedule["minute"],
                        hour=schedule["hour"],
                        day_of_week=schedule["day_of_week"],
                        day_of_month=schedule["day_of_month"],
                        month_of_year=schedule["month_of_year"],
                        timezone=schedule["timezone"],
                    ).first()
                    # If it does not exist, create a new Schedule
                    if not SCHEDULE:
                        SCHEDULE = CrontabSchedule.objects.create(
                            minute=schedule["minute"],
                            hour=schedule["hour"],
                            day_of_week=schedule["day_of_week"],
                            day_of_month=schedule["day_of_month"],
                            month_of_year=schedule["month_of_year"],
                            timezone=schedule["timezone"],
                        )
                        print(
                            f"Created Crontab Schedule for Hour:{SCHEDULE.hour},Minute:{SCHEDULE.minute}"
                        )
                    else:
                        print(
                            f"Crontab Schedule for Hour:{SCHEDULE.hour},Minute:{SCHEDULE.minute} already exists"
                        )
            for task in seed_data["scheduled_tasks"]:
                TASK = PeriodicTask.objects.filter(name=task["name"]).first()
                if not TASK:
                    if task["schedule"]["type"] == "crontab":
                        SCHEDULE = CrontabSchedule.objects.filter(
                            minute=task["schedule"]["minute"],
                            hour=task["schedule"]["hour"],
                            day_of_week=task["schedule"]["day_of_week"],
                            day_of_month=task["schedule"]["day_of_month"],
                            month_of_year=task["schedule"]["month_of_year"],
                            timezone=task["schedule"]["timezone"],
                        ).first()
                        TASK = PeriodicTask.objects.create(
                            crontab=SCHEDULE,
                            name=task["name"],
                            task=task["task"],
                            enabled=task["enabled"],
                        )
                        print(f"Created Periodic Task: {TASK.name}")
                    else:
                        raise Exception("Schedule for Periodic Task not found")
                else:
                    print(f"Periodic Task: {TASK.name} already exists")
