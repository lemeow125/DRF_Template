from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "id",
        "is_active",
        "user_group",
    ) + UserAdmin.list_display
    # Editable fields per instance
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("avatar",)}),)


admin.site.register(CustomUser, CustomUserAdmin)
