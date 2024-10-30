from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    model = Notification
    search_fields = ("id", "content")
    list_display = ["id", "dismissed"]
