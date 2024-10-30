from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%m-%d-%Y %I:%M %p", read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("id", "recipient", "content", "timestamp")
