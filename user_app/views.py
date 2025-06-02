import json
import logging
import os
from urllib.parse import parse_qs

import jwt
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .serializers import UserSerializer
from django.shortcuts import render
from datetime import datetime, timedelta, timezone
from rest_framework.decorators import action
from django.conf import settings
from dotenv import load_dotenv
from django.contrib.auth import get_user_model

from .utils import verify_telegram_init_data

logger = logging.getLogger(__name__)

User = get_user_model()

load_dotenv()


# Временная стартовая страница
def home(request):
    return render(request, 'home.html', {})


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'tg_id'

    def list(self, request):
        # Проверка API-ключа для бота
        api_key = request.headers.get('X-API-Key')
        if api_key == os.getenv("BOT_API_KEY"):
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            logger.info("Бот получил доступ к списку пользователей через API-ключ")
            return Response(serializer.data)

        # Проверка JWT
        payload = verify_jwt(request)
        if not payload:
            return Response({"error": "Invalid or missing token"}, status=status.HTTP_403_FORBIDDEN)

        if not payload.get('is_staff') and not payload.get('is_superuser'):
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        tg_id = data.get('tg_id')

        user, created = User.objects.get_or_create(
            tg_id=tg_id,
            defaults={
                'first_name': data.get('first_name', 'Unknown'),
                'last_name': data.get('last_name'),
                'username': data.get('username'),
                'is_bot': data.get('is_bot', False),
            }
        )

        if not created:
            changed = False
            for field in ['first_name', 'last_name', 'username']:
                if getattr(user, field) != data.get(field):
                    setattr(user, field, data.get(field))
                    changed = True
            if changed:
                user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, tg_id=None):
        try:
            user = User.objects.get(tg_id=tg_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, tg_id=None):
        try:
            user = User.objects.get(tg_id=tg_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

def verify_jwt(request):
    """Проверка JWT в заголовке Authorization."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.error("Missing or invalid Authorization header")
        return None

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("JWT has expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid JWT")
        return None


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet для аутентификации и защищённых эндпоинтов Telegram Mini App.
    """

    @action(detail=False, methods=['post'], url_path='verify')
    def verify_init_data(self, request):
        """
        Проверяет initData, сохраняет/обновляет пользователя и выдаёт JWT.
        """
        init_data = request.data.get("init_data")
        if not init_data:
            logger.error("init_data is required")
            return Response({"error": "init_data is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка подписи initData
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN is not set")
            return Response({"error": "Server configuration error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not verify_telegram_init_data(init_data, bot_token):
            logger.error(f"Invalid initData: {init_data}")
            return Response({"error": "Invalid initData"}, status=status.HTTP_403_FORBIDDEN)

        # Извлечение данных пользователя
        params = parse_qs(init_data)
        user_data = params.get("user", [""])[0]
        if not user_data:
            logger.error("No user data in initData")
            return Response({"error": "No user data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = json.loads(user_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid user data JSON: {e}")
            return Response({"error": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        tg_id = str(user.get("id"))  # Приводим к строке, так как tg_id в модели CharField
        first_name = user.get("first_name", "")
        last_name = user.get("last_name", "")
        username = user.get("username", "")
        is_bot = user.get("is_bot", False)

        # Создание или обновление пользователя в БД
        user_obj, created = User.objects.update_or_create(
            tg_id=tg_id,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "is_bot": is_bot,
                "is_active": True,
            }
        )

        # Генерация JWT
        jwt_payload = {
            "tg_id": tg_id,
            "is_staff": user_obj.is_staff,
            "is_superuser": user_obj.is_superuser,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
            "iat": datetime.now(timezone.utc)
        }
        jwt_token = jwt.encode(jwt_payload, settings.SECRET_KEY, algorithm="HS256")

        logger.info(f"User {tg_id} authenticated, JWT issued")
        return Response({
            "status": "success",
            "token": jwt_token,
            "user": {
                "tg_id": user_obj.tg_id,
                "first_name": user_obj.first_name,
                "username": user_obj.username,
                "created": created
            }
        })

    @action(detail=False, methods=['get'], url_path='protected-endpoint')
    def protected_endpoint(self, request):
        """
        Защищённый эндпоинт, доступный только с валидным JWT.
        """
        payload = verify_jwt(request)
        if not payload:
            return Response({"error": "Invalid or missing token"}, status=status.HTTP_403_FORBIDDEN)

        tg_id = payload["tg_id"]
        try:
            user = User.objects.get(tg_id=tg_id)
            logger.info(f"Access to protected endpoint by user {tg_id}")
            return Response({
                "status": "success",
                "message": f"Protected data for {user.first_name} (@{user.username or user.tg_id})",
                "is_staff": user.is_staff
            })
        except User.DoesNotExist:
            logger.error(f"User {tg_id} not found")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
