from rest_framework import serializers
from .models import LoyaltyCard

class LoyaltyCardSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyCard
        fields = ['card_number', 'card_image', 'created_at', 'user_full_name']
        read_only_fields = fields  # Все поля только для чтения

    def get_user_full_name(self, obj):
        """Возвращает полное имя пользователя"""
        return f"{obj.user.user_first_name or obj.user.first_name} {obj.user.user_last_name or obj.user.last_name}"
