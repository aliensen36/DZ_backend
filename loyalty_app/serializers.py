from rest_framework import serializers
from .models import LoyaltyCard

import logging
logger = logging.getLogger(__name__)

from django.contrib.auth import get_user_model
User = get_user_model()

class LoyaltyCardSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source="user.user_first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.user_last_name", read_only=True)
    birth_date = serializers.DateField(source="user.birth_date", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    card_image = serializers.ImageField(read_only=True)

    class Meta:
        model = LoyaltyCard
        fields = ['user_first_name', 'user_last_name', 'user_last_name', 'birth_date', 'phone_number', 'email', 'card_image', 'card_number', 'created_at']
        read_only_fields = ['user_first_name', 'user_last_name', 'user_last_name', 'birth_date', 'phone_number', 'email', 'card_image', 'card_number', 'created_at']

    def validate_user(self, value):
        logger.info(f"Validating user ID: {value.id}")
        return value

    def create(self, validated_data):
        user = validated_data.pop('user')
        logger.info(f"Creating loyalty card for user tg_id={user.tg_id}")
        card = LoyaltyCard.objects.create(user=user, **validated_data)
        return card
