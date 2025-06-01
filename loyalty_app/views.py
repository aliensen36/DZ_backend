from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from .models import LoyaltyCard
from .serializers import LoyaltyCardSerializer

User = get_user_model()

import logging
logger = logging.getLogger(__name__)

class LoyaltyCardViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyCard.objects.all()
    serializer_class = LoyaltyCardSerializer
    permission_classes = []  # Разрешаем доступ без авторизации
    lookup_field = "user__tg_id"  

    def get_queryset(self):
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        logger.info(f"Полученные данные запроса: {request.data}")
        user_id = request.data.get("user_id")  

        try:
            user = User.objects.get(tg_id=user_id) 
        except User.DoesNotExist:
            logger.error(f"User with user_id {user_id} not found.")
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, есть ли уже карта у пользователя
        if LoyaltyCard.objects.filter(user=user).exists():
            logger.info(f"User with user_id {user_id} already has a loyalty card.")
            return Response(
                {"detail": "У вас уже есть карта лояльности"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем карту
        card = LoyaltyCard.objects.create(user=user)
        serializer = self.get_serializer(card)
        logger.info(f"Loyalty card created for user with user_id {user_id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_card(self, request):
        """Получение карты текущего пользователя"""
        user_id = request.query_params.get("user_id")  

        if not user_id:
            return Response({"detail": "User user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(tg_id=user_id)  # Используем tg_id вместо id
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        card = LoyaltyCard.objects.filter(user=user).first()

        if card:
            serializer = self.get_serializer(card)
            return Response(serializer.data)
        else:
            return Response({"detail": "Карта лояльности не найдена."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def image(self, request, pk=None):
        """Получение URL изображения карты"""
        card = self.get_object()
        if not card.card_image:
            return Response(
                {"detail": "Изображение карты не найдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({"image_url": request.build_absolute_uri(card.card_image.url)})