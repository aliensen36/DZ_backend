from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from user_app.auth.permissions import IsBotAuthenticated
from .models import LoyaltyCard, PointsTransaction
from .serializers import LoyaltyCardSerializer, PointsTransactionSerializer
from user_app.auth.permissions import IsResident
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes, OpenApiExample

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
    
    @extend_schema(description="Получить баланс карты лояльности")
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def balance(self, request):
        user = request.user
        logger.info(f"Fetching balance for tg_id={user.tg_id}")

        card = LoyaltyCard.objects.filter(user=user).first()
        if not card:
            return Response({"detail": "Карта лояльности не найдена"}, status=status.HTTP_404_NOT_FOUND)

        # Получаем баланс
        balance = card.get_balance()
        logger.info(f"Balance fetched for tg_id={user.tg_id}: {balance}")

        return Response({"balance": balance}, status=status.HTTP_200_OK)


class PointsTransactionViewSet(viewsets.ModelViewSet):
    queryset = PointsTransaction.objects.all()
    serializer_class = PointsTransactionSerializer
    permission_classes = [IsResident]

    def list(self, request):
        return Response({"detail": "Этот эндпоинт отключен."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request):
        return Response({"detail": "Этот эндпоинт отключен."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        return Response({"detail": "Этот эндпоинт отключен."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, pk=None):
        return Response({"detail": "Этот эндпоинт отключен."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None):
        return Response({"detail": "Этот эндпоинт отключен."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    @extend_schema(
        description="Метод для начисления баллов по сумме. 1 балл начисляется за каждые 100 рублей.",
        request=PointsTransactionSerializer,
        responses={
            201: OpenApiResponse(description="Транзакция успешно создана", response=PointsTransactionSerializer),
            400: OpenApiResponse(description="Ошибка при начислении баллов")
        },
        parameters=[
            OpenApiParameter(
                name="price",  
                type=OpenApiTypes.NUMBER, 
                description="Сумма для начисления баллов (в рублях)", 
                examples=[OpenApiExample(name="default", value=500)],
            ),
            OpenApiParameter(
                name="card_id",  
                type=OpenApiTypes.INT,  
                description="ID карты лояльности", 
                examples=[OpenApiExample(name="default", value=1)],
            ),
            OpenApiParameter(
                name="resident_id",  
                type=OpenApiTypes.INT,  
                description="ID резидента", 
                examples=[OpenApiExample(name="default", value=2)],
            ),
        ]
    )
    @action(detail=False, methods=['post'], url_path='accrue')
    def accrue_points(self, request):
        try:
            price = float(request.data.get('price'))
        except (TypeError, ValueError):
            return Response({'error': 'Сумма должна быть числом'}, status=status.HTTP_400_BAD_REQUEST)

        if price <= 0:
            return Response({'error': 'Сумма должна быть положительной'}, status=status.HTTP_400_BAD_REQUEST)

        accrue_points = int(price) // 100  # 1 балл за каждые 100 рублей

        if accrue_points <= 0:
            return Response({'error': 'Недостаточно суммы для начисления баллов'}, status=status.HTTP_400_BAD_REQUEST)

        transaction_data = {
            'price': price,
            'points': accrue_points,
            'transaction_type': 'начисление',
            'card_id': request.data.get('card_id'),
            'resident_id': request.data.get('resident_id')
        }

        serializer = self.get_serializer(data=transaction_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Метод для списания баллов. Баллы списываются на основе указанной суммы.",
        request=PointsTransactionSerializer,
        responses={
            201: OpenApiResponse(description="Транзакция успешно создана", response=PointsTransactionSerializer),
            400: OpenApiResponse(description="Ошибка при списании баллов"),
            404: OpenApiResponse(description="Карта не найдена"),
        },
        parameters=[
            OpenApiParameter(
                name="price",  
                type=OpenApiTypes.NUMBER,  
                description="Сумма для списания баллов (в рублях)", 
                examples=[OpenApiExample(name="default", value=500)],  # Пример с использованием OpenApiExample
            ),
            OpenApiParameter(
                name="card_id",  
                type=OpenApiTypes.INT,  
                description="ID карты лояльности", 
                examples=[OpenApiExample(name="default", value=1)], 
            ),
            OpenApiParameter(
                name="resident_id",  
                type=OpenApiTypes.INT,  
                description="ID резидента", 
                examples=[OpenApiExample(name="default", value=2)],
            ),
        ]
    )
    @action(detail=False, methods=['post'], url_path='deduct')
    def deduct_points(self, request):
        try:
            price = float(request.data.get('price'))
        except (TypeError, ValueError):
            return Response({'error': 'Сумма должна быть числом.'}, status=status.HTTP_400_BAD_REQUEST)

        if price <= 0:
            return Response({'error': 'Сумма должна быть положительной.'}, status=status.HTTP_400_BAD_REQUEST)

        card_id = request.data.get('card_id')
        resident_id = request.data.get('resident_id')

        if not card_id or not resident_id:
            return Response({'error': 'Необходимо указать ID карты и ID резидента.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            card = LoyaltyCard.objects.get(id=card_id)
        except LoyaltyCard.DoesNotExist:
            return Response({'error': 'Карта не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        current_balance = card.get_balance()
        max_deductible_points = int(price * 0.10)  # 10% от суммы

        if max_deductible_points <= 0:
            return Response({'error': 'Недостаточная сумма для списания баллов.'}, status=status.HTTP_400_BAD_REQUEST)

        if current_balance < max_deductible_points:
            return Response({
                'error': f'Недостаточно баллов. Баланс: {current_balance}, требуется: {max_deductible_points}'
            }, status=status.HTTP_400_BAD_REQUEST)

        transaction_data = {
            'points': -max_deductible_points,
            'price': price,
            'transaction_type': 'списание',
            'card_id': card_id,
            'resident_id': resident_id
        }

        serializer = self.get_serializer(data=transaction_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)