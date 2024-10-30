import stripe
from config.settings import STRIPE_SECRET_KEY
from django.db import models
from django.utils.timezone import now

stripe.api_key = STRIPE_SECRET_KEY


class UserGroup(models.Model):
    name = models.CharField(max_length=128, null=False)
    owner = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="usergroup_owner",
    )
    managers = models.ManyToManyField(
        "accounts.CustomUser", related_name="usergroup_managers"
    )
    members = models.ManyToManyField(
        "accounts.CustomUser", related_name="usergroup_members"
    )
    date_created = models.DateTimeField(default=now, editable=False)

    # Derived from email of owner, may be used for billing
    @property
    def email(self):
        return self.owner.email

    def __str__(self):
        return self.name
