import django.contrib.auth.models
from rest_framework import serializers

from . import models


class SupportManager(serializers.ModelSerializer):
    id = serializers.IntegerField(
        read_only=True,
        source='pk',
    )

    class Meta:
        model = django.contrib.auth.models.User
        read_only_fields = [
            'first_name',
            'last_name',
        ]
        fields = [
            'id',
            'first_name',
            'last_name',
        ]


class TelegramUser(serializers.ModelSerializer):
    class Meta:
        model = models.get_telegram_user_model()
        read_only_fields = [
            'telegram_id',
        ]
        fields = [
            'telegram_id',
        ]


class Ticket(serializers.ModelSerializer):
    user = TelegramUser(
        read_only=True,
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=models.get_telegram_user_model().objects.all(),
        write_only=True,
        source='user',
    )
    support_manager = SupportManager(
        read_only=True,
    )
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = models.Ticket
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
        ]

    def get_last_message(self, obj: models.Ticket):
        last_message = obj.messages.order_by('created_at').last()
        if not last_message:
            return None
        return Message(last_message).data


class Message(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'ticket',
        ]
