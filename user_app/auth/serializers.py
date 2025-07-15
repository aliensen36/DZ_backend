import json
from rest_framework import serializers
from django.conf import settings
from urllib.parse import parse_qs
from .telegram_utils import verify_telegram_init_data
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    init_data = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('tg_id', None)
        self.fields.pop('password', None)


    def validate(self, attrs):
        init_data = attrs.get('init_data')
        if not verify_telegram_init_data(init_data, settings.TELEGRAM_BOT_TOKEN):
            raise serializers.ValidationError('Invalid initData')

        # Извлечение user_data из initData
        params = parse_qs(init_data)
        user_data = json.loads(params.get('user', ['{}'])[0])

        # Создание/получение пользователя
        try:
            user = User.objects.get(tg_id=user_data['id'])
        except User.DoesNotExist:
            user = User.objects.create_user(
                tg_id=user_data['id'],
                username=user_data.get('username'),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                role='user'  # Роль по умолчанию
            )

        # Генерация токенов
        data = {}
        refresh = RefreshToken.for_user(user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user_id'] = user.tg_id
        data['role'] = user.role
        return data