from django.core.cache import cache
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated


class NotificationViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "delete"]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        if instance.recipient != request.user:
            raise PermissionDenied(
                "You do not have permission to delete this notification."
            )

        cache.delete(f"notifications_user:{user.id}")

        return super().destroy(request, *args, **kwargs)
