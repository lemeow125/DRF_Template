from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter

from .models import UserGroup


@admin.register(UserGroup)
class UserGroupAdmin(ModelAdmin):
    list_filter_submit = True
    list_filter = (("date_created", RangeDateFilter),)

    list_display = ["id", "name"]
    search_fields = ["id", "name"]
