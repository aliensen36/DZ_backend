from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import LoyaltyCard
from .serializers import LoyaltyCardSerializer
from django.shortcuts import get_object_or_404

class LoyaltyCardViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyCard.objects.all()
    serializer_class = LoyaltyCardSerializer
    permission_classes = [permissions.AllowAny]  # Временная мера

    def get_queryset(self):
        return super().get_queryset() # Временная мера

    def create(self, request, *args, **kwargs):
        """Создание карты лояльности (автоматическое)"""

        # Проверяем, есть ли уже карта у пользователя
        if LoyaltyCard.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "У вас уже есть карта лояльности"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем карту (изображение генерируется автоматически в методе save)
        card = LoyaltyCard.objects.create(user=request.user)
        serializer = self.get_serializer(card)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_card(self, request):
        """Получение карты текущего пользователя"""
        card = get_object_or_404(LoyaltyCard, user=request.user)
        serializer = self.get_serializer(card)
        return Response(serializer.data)

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
