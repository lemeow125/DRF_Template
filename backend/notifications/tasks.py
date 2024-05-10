from celery import shared_task
from django.utils import timezone
from notifications.models import Notification


@shared_task
def cleanup_notifications():
    # Calculate the date 3 days ago
    three_days_ago = timezone.now() - timezone.timedelta(days=3)

    # Delete notifications that are older than 3 days and dismissed
    Notification.objects.filter(
        dismissed=True, timestamp__lte=three_days_ago).delete()
