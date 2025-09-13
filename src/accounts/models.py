"""
Common model schemas
"""

from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    # Most fields are inherited from AbstractUser

    # Can be used to show tooltips for newer users
    @property
    def is_new(self):
        current_date = timezone.now()
        return self.date_joined + timedelta(days=1) < current_date

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
