from rest_framework.reverse import reverse
from rest_framework import serializers
from .models import LoyaltyCard, PointsTransaction

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
    card_image_url = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyCard
        fields = ['id', 'user_first_name', 'user_last_name', 'birth_date', 'phone_number', 'email', 'card_number',
                  'created_at', 'card_image_url']
        read_only_fields = ['user_first_name', 'user_last_name', 'birth_date', 'phone_number', 'email', 'card_number',
                            'created_at', 'card_image_url']

    def create(self, validated_data):
        user = validated_data.pop('user')
        logger.info(f"Creating loyalty card for user tg_id={user.tg_id}")
        card = LoyaltyCard.objects.create(user=user, **validated_data)
        return card

    def get_card_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.pk and hasattr(obj.user, 'tg_id'):
            try:
                relative_url = reverse('loyaltycard-loyalty-card-image', kwargs={'user__tg_id': obj.user.tg_id},
                                       request=request)
                return relative_url  # теперь это абсолютный URL, например https://example.com/api/loyalty/123/card-image/
            except Exception as e:
                logger.error(f"Error generating card_image_url for tg_id={obj.user.tg_id}: {str(e)}")
        return None


class PointsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsTransaction
        fields = '__all__'

    def validate(self, data):
        price = data.get('price')
        transaction_type = data.get('transaction_type')
        points = data.get('points')

        if price<=0:
            raise serializers.ValidationError("Сумма должна быть положительной")

        if transaction_type == 'начисление' and points<=0:
            raise serializers.ValidationError("При начисдении баллов число не может быть отрицательным.")
        
        if transaction_type == 'списание' and points>=0:
            raise serializers.ValidationError("При списании баллов число не может быть положительным.")
        
        return data