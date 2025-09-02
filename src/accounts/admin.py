"""
Admin configuration for accounts app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "id",
        "is_active",
        "is_new",
    ) + UserAdmin.list_display


admin.site.register(CustomUser, CustomUserAdmin)
