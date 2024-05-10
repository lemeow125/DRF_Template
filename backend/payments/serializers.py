from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField()
    annual = serializers.BooleanField()
