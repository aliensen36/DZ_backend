import datetime
import re

from rest_framework import serializers
from .models import LoyaltyCard, PointsTransaction, Promotion, UserPromotion, PointsSystemSettings

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
            raise serializers.ValidationError("При начисдении бонусов число не может быть отрицательным.")
        
        if transaction_type == 'списание' and points>=0:
            raise serializers.ValidationError("При списании бонусов число не может быть положительным.")
        
        return data
    

class PromotionSerializer(serializers.ModelSerializer):
    percent_equals_points = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = '__all__'

    def get_percent_equals_points(self, obj):
        return obj.percent_equals_points()
    
    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        promotional_code = data.get('promotional_code')
        discount_percent = data.get('discount_percent')

        if start and end and end < start:
            raise serializers.ValidationError("Дата окончания мероприятия не может быть раньше даты начала.")

        if start and start < datetime.datetime.now(datetime.timezone.utc):
            raise serializers.ValidationError("Дата начала мероприятия не может быть в прошлом.")
        
        if not re.match(r'^[A-Z0-9]+$', promotional_code) and not re.search(r'\d', promotional_code):
            raise serializers.ValidationError("Промокод должен содержать только заглавные буквы, а также обязательно включать хотя бы одну цифру.")
        
        if discount_percent is not None and (discount_percent < 0 or discount_percent > 100):
            raise serializers.ValidationError("Процент скидки должен быть в диапазоне от 0 до 100.")

        return data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.photo and request:
            representation['photo'] = request.build_absolute_uri(instance.photo.url)
        else:
            representation['photo'] = None
        return representation
    

class UserPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPromotion
        fields = '__all__'
        read_only_fields = ['redeemed_at', 'user']

    def validate(self, data):
        user = self.context['request'].user
        promotion = data.get('promotion')

        if UserPromotion.objects.filter(user=user, promotion=promotion).exists():
            raise serializers.ValidationError("Пользователь уже активировал этот промокод.")
        
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

class UserPromotionDisplaySerializer(serializers.ModelSerializer):
    promotional_code = serializers.CharField(source='promotion.promotional_code')
    promotion_title = serializers.CharField(source='promotion.title')
    resident_name = serializers.CharField(source='promotion.resident.name', default='Не указан')
    start_date = serializers.DateTimeField(source='promotion.start_date')
    end_date = serializers.DateTimeField(source='promotion.end_date')
    percent_equals_points = serializers.SerializerMethodField()

    class Meta:
        model = UserPromotion
        fields = [
            'promotion_title',
            'promotional_code',
            'resident_name',
            'start_date',
            'end_date',
            'percent_equals_points',
        ]

    def get_percent_equals_points(self, obj):
        return obj.promotion.percent_equals_points()
    

class PointsSystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsSystemSettings
        fields = '__all__'

    def validate(self, data):
        if data.get('points_per_100_rubles') <= 0:
            raise serializers.ValidationError("Количество бонусов за 100 рублей должно быть положительным числом.")
        if data.get('points_per_1_percent') <= 0:
            raise serializers.ValidationError("Количество бонусов за 1% скидки должно быть положительным числом.")
        return data