from django.core.cache import cache
from django.db import models


class Notification(models.Model):
    recipient = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE)
    content = models.CharField(max_length=1000, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    dismissed = models.BooleanField(default=False)

    def __str__(self):
        return self.content

    def save(self, **kwargs):
        cache.delete(f"notifications_user:{self.recipient.id}")
        super().save(**kwargs)
