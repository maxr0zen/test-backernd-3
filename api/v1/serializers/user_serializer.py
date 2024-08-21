from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Subscription, Balance

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def get_balance(self, obj):
        try:
            balance = Balance.objects.get(user=obj)
            return balance.balance
        except Balance.DoesNotExist:
            return 0


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    user = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'id',
            'user',
            'course',
            'created_at',
        )
        read_only_fields = ('created_at',)