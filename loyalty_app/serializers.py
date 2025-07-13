import datetime

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

        if start and end and end < start:
            raise serializers.ValidationError("Дата окончания мероприятия не может быть раньше даты начала.")

        if start and start < datetime.datetime.now(datetime.timezone.utc):
            raise serializers.ValidationError("Дата начала мероприятия не может быть в прошлом.")

        return data
    
    # Для локальной разработки
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.photo:
            # Используем SITE_URL для формирования публичного URL
            photo_path = instance.photo.url 
            photo_url = f"{settings.SITE_URL}{photo_path}"
            representation['photo'] = photo_url
        else:
            representation['photo'] = None
        return representation


    # Для продакшена нужно раскомментировать следующий метод
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     request = self.context.get('request')
    #     if instance.photo and request:
    #         representation['photo'] = request.build_absolute_uri(instance.photo.url)
    #     else:
    #         representation['photo'] = None
    #     return representation
    