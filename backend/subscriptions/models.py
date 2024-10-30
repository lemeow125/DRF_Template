from accounts.models import CustomUser
from django.db import models
from django.utils.timezone import now
from user_groups.models import UserGroup


class StripePrice(models.Model):
    annual = models.BooleanField(default=False)
    stripe_price_id = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=20)
    lookup_key = models.CharField(max_length=100, blank=True, null=True)
    prorated = models.BooleanField(default=False)

    def __str__(self):
        if self.annual:
            return f"{self.price}{self.currency}/year"
        else:
            return f"{self.price}{self.currency}/month"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1024, null=True)
    stripe_product_id = models.CharField(max_length=100)
    annual_price = models.ForeignKey(
        StripePrice, on_delete=models.SET_NULL, related_name="annual_plan", null=True
    )
    monthly_price = models.ForeignKey(
        StripePrice, on_delete=models.SET_NULL, related_name="monthly_plan", null=True
    )
    group_exclusive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


# Model for User Subscriptions


class UserSubscription(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, null=True
    )
    user_group = models.ForeignKey(
        UserGroup, on_delete=models.CASCADE, blank=True, null=True
    )
    subscription = models.ForeignKey(
        SubscriptionPlan, on_delete=models.SET_NULL, blank=True, null=True
    )
    stripe_id = models.CharField(max_length=100)
    date = models.DateTimeField(default=now, editable=False)
    valid = models.BooleanField()
    annual = models.BooleanField()

    def __str__(self):
        if self.user:
            return f"Subscription {self.subscription.name} for {self.user}"
        else:
            return f"Subscription {self.subscription.name} for {self.user_group}"
