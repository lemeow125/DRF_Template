from subscriptions.serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
)
from subscriptions.models import SubscriptionPlan, UserSubscription
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from django.core.cache import cache


class SubscriptionPlanViewset(viewsets.ModelViewSet):
    http_method_names = ["get"]
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    queryset = SubscriptionPlan.objects.all()

    def get_queryset(self):
        key = "subscriptionplans"
        queryset = cache.get(key)
        if not queryset:
            queryset = super().get_queryset()
            cache.set(key, queryset, 60 * 60)
        return queryset


class UserSubscriptionViewset(viewsets.ModelViewSet):
    http_method_names = ["get"]
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserSubscription.objects.all()

    def get_queryset(self):
        user = self.request.user
        key = f"subscriptions_user:{user.id}"
        queryset = cache.get(key)
        if not queryset:
            queryset = UserSubscription.objects.filter(user=user)
            cache.set(key, queryset, 60 * 60)
        return queryset


class UserGroupSubscriptionViewet(viewsets.ModelViewSet):
    http_method_names = ["get"]
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserSubscription.objects.all()

    def get_queryset(self):
        user = self.request.user
        if not user.user_group:
            return UserSubscription.objects.none()
        else:
            key = f"subscriptions_usergroup:{user.user_group.id}"
            queryset = cache.get(key)
            if not cache:
                queryset = UserSubscription.objects.filter(user_group=user.user_group)
                cache.set(key, queryset, 60 * 60)
            return queryset
