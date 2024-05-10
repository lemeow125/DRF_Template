from rest_framework import serializers
from subscriptions.models import SubscriptionPlan, UserSubscription, StripePrice
from accounts.serializers import SimpleCustomUserSerializer


class SimpleStripePriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = StripePrice
        fields = ['price', 'currency', 'prorated']


class SubscriptionPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'description',
                  'annual_price', 'monthly_price', 'group_exclusive']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['annual_price'] = SimpleStripePriceSerializer(
            instance.annual_price, many=False).data
        representation['monthly_price'] = SimpleStripePriceSerializer(
            instance.monthly_price, many=False).data
        return representation


class UserSubscriptionSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M %p", read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'user_group', 'subscription',
                  'date', 'valid', 'annual']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = SimpleCustomUserSerializer(
            instance.user, many=False).data
        representation['subscription'] = SubscriptionPlanSerializer(
            instance.subscription, many=False).data
        return representation
