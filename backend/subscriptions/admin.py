from django.contrib import admin
from subscriptions.models import StripePrice, SubscriptionPlan, UserSubscription
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter


@admin.register(StripePrice)
class StripePriceAdmin(ModelAdmin):
    search_fields = [
        "id",
        "lookup_key",
        "stripe_price_id",
        "price",
        "currency",
        "prorated",
        "annual",
    ]
    list_display = [
        "id",
        "lookup_key",
        "stripe_price_id",
        "price",
        "currency",
        "prorated",
        "annual",
    ]


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    list_display = ["id", "__str__", "stripe_product_id", "group_exclusive"]
    search_fields = ["id", "name", "stripe_product_id", "group_exclusive"]


@admin.register(UserSubscription)
class UserSubscriptionAdmin(ModelAdmin):
    list_filter_submit = True
    list_filter = (("date", RangeDateFilter),)
    list_display = ["id", "__str__", "valid", "annual", "date"]
    search_fields = ["id", "date"]
