from rest_framework import viewsets
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from rest_framework.exceptions import PermissionDenied
from django.core.cache import cache


class NotificationViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "delete"]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def get_queryset(self):
        user = self.request.user
        key = f"notifications_user:{user.id}"
        queryset = cache.get(key)
        if not queryset:
            queryset = Notification.objects.filter(recipient=user).order_by(
                "-timestamp"
            )
            cache.set(key, queryset, 60 * 60)
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.recipient != request.user:
            raise PermissionDenied(
                "You do not have permission to update this notification."
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.recipient != request.user:
            raise PermissionDenied(
                "You do not have permission to delete this notification."
            )
        return super().destroy(request, *args, **kwargs)
