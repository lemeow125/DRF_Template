from rest_framework import serializers
from .models import UserGroup


class SimpleUserGroupSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format="%m-%d-%Y %I:%M %p", read_only=True)

    class Meta:
        model = UserGroup
        fields = ["id", "name", "date_created"]
        read_only_fields = ["id", "name", "date_created"]
