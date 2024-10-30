from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    model = Notification
    search_fields = ("id", "content")
    list_display = ["id", "dismissed"]
