"""
URL configuration for accounts app
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts import views

router = DefaultRouter()
router.register(r"users", views.CustomUserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("", include("djoser.urls.jwt")),
]
