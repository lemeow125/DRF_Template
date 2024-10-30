from django.dispatch import receiver
from django.db.models.signals import post_save
from notifications.models import Notification
from django.core.cache import cache

# Template for running actions after user have paid for a subscription


@receiver(post_save, sender=Notification)
def clear_cache_after_notification_update(sender, instance, **kwargs):
    # Clear cache
    cache.delete("notifications")
    cache.delete(f"notifications_user:{instance.recipient.id}")
