from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import UserGroup
from unfold.contrib.filters.admin import RangeDateFilter


@admin.register(UserGroup)
class UserGroupAdmin(ModelAdmin):
    list_filter_submit = True
    list_filter = (("date_created", RangeDateFilter),)

    list_display = ["id", "name"]
    search_fields = ["id", "name"]
