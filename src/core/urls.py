"""
Base URL configuration for the project.

Refer to api/urls.py for actual endpoints.
"""

from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("api.urls")),
]
