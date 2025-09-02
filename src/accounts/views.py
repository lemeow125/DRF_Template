"""
Viewset for accounts app.
"""

import logging

from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from djoser.conf import settings
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action

from accounts import serializers
from accounts.models import CustomUser

logger = logging.getLogger(__name__)


class CustomUserViewSet(DjoserUserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = settings.PERMISSIONS.activation
    token_generator = default_token_generator

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            cache_key = "users:admin"
            queryset = cache.get(cache_key)
            if not queryset:
                queryset = CustomUser.objects.all()
                cache.set(cache_key, queryset, 60 * 60)
            return queryset
        else:
            cache_key = f"users:{user.id}"
            queryset = cache.get(cache_key)
            if not queryset:
                queryset = CustomUser.objects.filter(id=user.id)
                cache.set(cache_key, queryset, 60 * 60)
            return queryset

    def perform_update(self, serializer, *args, **kwargs):
        user = self.request.user

        super().perform_update(serializer, *args, **kwargs)

        cache.delete("users")
        cache.delete(f"users:{user.id}")

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)

        # Try-catch block for email sending
        try:
            super().perform_create(serializer, *args, **kwargs)

            # Clear cache
            cache.delete("users")
            cache.delete(f"user:{user.id}")

        except Exception as e:
            logger.warning(
                f"Registration failure, unable to send activation email for {user.id}: {e}"
            )

    @action(
        methods=["post"], detail=False, url_path="activation", url_name="activation"
    )
    def activation(self, request, *args, **kwargs):
        user = self.request.user
        super().activation(request, *args, **kwargs)

        # Clear cache
        cache.delete("users")
        cache.delete(f"users:{user.id}")
