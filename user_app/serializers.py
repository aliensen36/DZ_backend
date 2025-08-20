import datetime
from datetime import timezone
import re

from rest_framework import serializers

from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['last_login']
        read_only_fields = ['tg_id']

    def validate_birth_date(self, value):
        if value:
            if isinstance(value, str):
                try:
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    raise serializers.ValidationError("Дата рождения должна быть в формате ГГГГ-ММ-ДД")
            elif isinstance(value, datetime.datetime):
                value = value.date()
            elif isinstance(value, datetime.date):
                pass
            
            if value > datetime.date.today():
                raise serializers.ValidationError("Дата рождения не может быть в будущем")
        return value

    def validate_phone_number(self, value):
        if value and not re.match(r"^\+?\d{10,15}$", value):
            raise serializers.ValidationError("Номер телефона должен содержать 10–15 цифр, возможно с '+'")
        return value

    def validate_email(self, value):
        if value and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", value):
            raise serializers.ValidationError("Неверный формат email")
        return value

