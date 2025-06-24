from rest_framework import serializers
from .models import Mailing, Subscription
from django.contrib.auth import get_user_model

User = get_user_model()


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'
        read_only_fields = ('created_at',)


class MailingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = ['text', 'image', 'button_url', 'type', 'tg_user_id']

    def create(self, validated_data):
        # Не нужно привязывать пользователя Django, используем только tg_user_id
        return Mailing.objects.create(**validated_data)


class MailingListSerializer(serializers.ModelSerializer):
    preview = serializers.SerializerMethodField()

    class Meta:
        model = Mailing
        fields = ['id', 'type', 'created_at', 'preview']

    def get_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'name', 'description']