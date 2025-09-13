from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.core.cache import cache
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings

from accounts.models import CustomUser

# There can be multiple subject instances with the same name, only differing in course, year level, and semester. We filter them here


class SimpleCustomUserSerializer(ModelSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ("id", "username", "email", "full_name")


class CustomUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "is_new",
            "last_name",
        )
        read_only_fields = (
            "id",
            "username",
            "email",
        )

    def update(self, instance, validated_data):
        cache.delete(f"users:{instance.id}")

        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, style={"input_type": "password", "placeholder": "Password"}
    )
    first_name = serializers.CharField(
        required=True, allow_blank=False, allow_null=False
    )
    last_name = serializers.CharField(
        required=True, allow_blank=False, allow_null=False
    )

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password", "first_name", "last_name"]

    def validate(self, attrs):
        user_attrs = attrs.copy()
        user = self.Meta.model(**user_attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            errors = serializer_error[api_settings.NON_FIELD_ERRORS_KEY]
            if len(errors) > 1:
                raise serializers.ValidationError({"password": errors[0]})
            else:
                raise serializers.ValidationError({"password": errors})
        if self.Meta.model.objects.filter(username=attrs.get("username")).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )

        return super().validate(attrs)

    def create(self, validated_data):
        user = self.Meta.model(**validated_data)
        user.username = validated_data["username"]
        user.is_active = False
        user.set_password(validated_data["password"])
        user.save()

        cache.delete("users")

        return user
