from rest_framework.reverse import reverse
from rest_framework import serializers
from .models import LoyaltyCard, PointsTransaction

import logging
logger = logging.getLogger(__name__)

from django.contrib.auth import get_user_model
User = get_user_model()

class LoyaltyCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyCard
        fields = ['card_number', 'created_at']
        read_only_fields = ['card_number', 'created_at']


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