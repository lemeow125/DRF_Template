"""
Common model schemas
"""

from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    # Most fields are inherited from AbstractUser

    # Can be used to show tooltips for newer users
    @property
    def is_new(self):
        """Check if user joined within the last day."""
        return (timezone.now() - self.date_joined).days == 0

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
