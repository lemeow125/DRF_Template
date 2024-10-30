from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django_resized import ResizedImageField
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    # first_name inherited from base user class
    # last_name inherited from base user class
    # email inherited from base user class
    # username inherited from base user class
    # password inherited from base user class
    # is_admin inherited from base user class

    avatar = ResizedImageField(
        null=True, force_format="WEBP", quality=100, upload_to="avatars/"
    )

    # Used for onboarding processes
    # Set this to False later on once the user makes actions
    onboarding = models.BooleanField(default=True)

    user_group = models.ForeignKey(
        "user_groups.UserGroup", on_delete=models.SET_NULL, null=True
    )

    @property
    def group_member(self):
        if self.user_group:
            return True
        else:
            return False

    # Can be used to show tooltips for newer users
    @property
    def is_new(self):
        current_date = timezone.now()
        return self.date_joined + timedelta(days=1) < current_date

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def group_member(self):
        if self.user_group:
            return True
        else:
            return False

    @property
    def group_owner(self):
        if self.user_group and self == self.user_group.owner:
            return True
        else:
            return False

    @property
    def admin_url(self):
        return reverse("admin:users_customuser_change", args=(self.pk,))
