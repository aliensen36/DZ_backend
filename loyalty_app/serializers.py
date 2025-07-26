import datetime
import re

from rest_framework import serializers
from .models import LoyaltyCard, PointsTransaction, Promotion
from django.conf import settings

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
    

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'
    
    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        promotional_code = data.get('promotional_code')

        if start and end and end < start:
            raise serializers.ValidationError("Дата окончания мероприятия не может быть раньше даты начала.")

        if start and start < datetime.datetime.now(datetime.timezone.utc):
            raise serializers.ValidationError("Дата начала мероприятия не может быть в прошлом.")
        
        if not re.match(r'^[A-Z0-9]+$', promotional_code) and not re.search(r'\d', promotional_code):
            raise serializers.ValidationError("Промокод должен содержать только заглавные буквы, а также обязательно включать хотя бы одну цифру.")

        return data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.photo and request:
            representation['photo'] = request.build_absolute_uri(instance.photo.url)
        else:
            representation['photo'] = None
        return representation
    