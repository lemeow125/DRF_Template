from rest_framework import status
from accounts.models import CustomUser
from accounts import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.conf import settings
from djoser.views import UserViewSet as DjoserUserViewSet
from django.contrib.auth.tokens import default_token_generator
from djoser import signals
from djoser.compat import get_user_email
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated


class CustomUserViewSet(DjoserUserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = settings.PERMISSIONS.activation
    token_generator = default_token_generator

    def get_queryset(self):
        user = self.request.user
        # If user is admin, show all active users
        if user.is_superuser:
            key = "users"
            # Get cache
            queryset = cache.get(key)
            # Set cache if stale or does not exist
            if not queryset:
                queryset = CustomUser.objects.filter(is_active=True)
                cache.set(key, queryset, 60 * 60)
            return queryset
        elif not user.user_group:
            key = f"user:{user.id}"
            queryset = cache.get(key)
            if not queryset:
                queryset = CustomUser.objects.filter(is_active=True)
                cache.set(key, queryset, 60 * 60)
            return queryset
        elif user.user_group:
            key = f"usergroup_users:{user.user_group.id}"
            queryset = cache.get(key)
            if not queryset:
                queryset = CustomUser.objects.filter(user_group=user.user_group)
                cache.set(key, queryset, 60 * 60)
            return queryset
        else:
            return CustomUser.objects.none()

    def perform_update(self, serializer, *args, **kwargs):
        user = self.request.user

        # Clear cache
        cache.delete(f"users")
        cache.delete(f"user:{user.id}")
        if user.user_group:
            cache.delete(f"usergroup_users:{user.user_group.id}")

        super().perform_update(serializer, *args, **kwargs)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )
        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)

        # Silently error out if email sending fails
        try:
            signals.user_registered.send(
                sender=self.__class__, user=user, request=self.request
            )
            context = {"user": user}
            to = [get_user_email(user)]

            if settings.SEND_ACTIVATION_EMAIL:
                settings.EMAIL.activation(self.request, context).send(to)
            elif settings.SEND_CONFIRMATION_EMAIL:
                settings.EMAIL.confirmation(self.request, context).send(to)

            # Clear cache
            cache.delete("users")
            cache.delete(f"user:{user.id}")
            if user.user_group:
                cache.delete(f"usergroup_users:{user.user_group.id}")

        except Exception as e:
            print("Warning: Unable to send email")
            print(e)

    @action(
        methods=["post"], detail=False, url_path="activation", url_name="activation"
    )
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        # Construct a response with user's first name, last name, and email
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
        }

        # Clear cache
        cache.delete("users")
        cache.delete(f"user:{user.id}")
        if user.user_group:
            cache.delete(f"usergroup_users:{user.user_group.id}")

        return Response(user_data, status=status.HTTP_200_OK)
