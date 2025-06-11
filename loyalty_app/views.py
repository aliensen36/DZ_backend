from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from user_app.auth.permissions import IsBotAuthenticated
from .models import LoyaltyCard
from .serializers import LoyaltyCardSerializer

from django.contrib.auth import get_user_model
User = get_user_model()

import logging
logger = logging.getLogger(__name__)

class LoyaltyCardViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyCard.objects.all()
    serializer_class = LoyaltyCardSerializer
    permission_classes = [IsBotAuthenticated | IsAuthenticated]
    lookup_field = "user__tg_id"

    def get_queryset(self):
        if getattr(self.request, 'user', None) and self.request.user.is_authenticated:
            logger.info(f"Filtering queryset for user tg_id={self.request.user.tg_id}")
            return self.queryset.filter(user=self.request.user)
        logger.info("Returning full queryset for bot")
        return self.queryset

    @extend_schema(description="Create a loyalty card (bot only, requires user_id)")
    def create(self, request, *args, **kwargs):
        logger.info(f"Create loyalty card request: {request.data}")
        user_id = request.data.get("user_id")

        if not user_id:
            logger.error("Missing user_id in create request")
            return Response({"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(tg_id=user_id)
        except User.DoesNotExist:
            logger.error(f"User with tg_id={user_id} not found")
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if LoyaltyCard.objects.filter(user=user).exists():
            logger.info(f"Loyalty card already exists for tg_id={user_id}")
            return Response(
                {"detail": "У вас уже есть карта лояльности"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data={"user": user.id})
        serializer.is_valid(raise_exception=True)
        card = LoyaltyCard(user=user)  # Явно задаем user
        serializer.save(user=user)  # Передаем user в save
        logger.info(f"Loyalty card created for tg_id={user_id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(description="Get the current user's loyalty card (TMA only)")
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_card(self, request):
        user = request.user
        logger.info(f"Fetching loyalty card for tg_id={user.tg_id}")

        card = LoyaltyCard.objects.filter(user=user).first()
        if card:
            serializer = self.get_serializer(card)
            logger.info(f"Loyalty card found for tg_id={user.tg_id}")
            return Response(serializer.data)
        logger.warning(f"No loyalty card found for tg_id={user.tg_id}")
        return Response({"detail": "Карта лояльности не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(description="Get the loyalty card image URL (bot or TMA)")
    @action(detail=True, methods=['get'])
    def image(self, request, user__tg_id=None):
        logger.info(f"Fetching card image for tg_id={user__tg_id}")
        try:
            card = self.get_object()
        except LoyaltyCard.DoesNotExist:
            logger.error(f"Loyalty card not found for tg_id={user__tg_id}")
            return Response({"detail": "Карта лояльности не найдена"}, status=status.HTTP_404_NOT_FOUND)

        if not card.card_image:
            logger.warning(f"No card image for tg_id={user__tg_id}")
            return Response({"detail": "Изображение карты не найдено"}, status=status.HTTP_404_NOT_FOUND)
        logger.info(f"Card image found for tg_id={user__tg_id}")
        return Response({"image_url": request.build_absolute_uri(card.card_image.url)})
