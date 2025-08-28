import logging
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import (extend_schema, extend_schema_view,
                                   OpenApiParameter, OpenApiResponse)
from .auth.permissions import IsAdmin, IsBotAuthenticated
from dotenv import load_dotenv
from django.conf import settings
from .serializers import UserSerializer
from avatar_app.serializers import UserAvatarProgressSerializer, UserAvatarDetailSerializer
from avatar_app.models import UserAvatarProgress
from loyalty_app.serializers import UserPromotionDisplaySerializer, PointsTransactionSerializer
from loyalty_app.models import UserPromotion, PointsTransaction
from .models import Referral

load_dotenv()
logger = logging.getLogger(__name__)

from django.contrib.auth import get_user_model
User = get_user_model()

@extend_schema_view(
    list=extend_schema(
        tags=["Пользователи"],
        summary="Список пользователей",
        description="Доступно только админам или боту. Возвращает список всех пользователей.",
        responses={200: UserSerializer(many=True)},
    ),
    create=extend_schema(
        tags=["Пользователи"],
        summary="Создание или обновление пользователя",
        description="Создаёт нового пользователя по tg_id или обновляет существующего.",
        request=UserSerializer,
        responses={201: UserSerializer, 200: UserSerializer},
    ),
    retrieve=extend_schema(
        tags=["Пользователи"],
        summary="Информация о пользователе",
        description="Возвращает данные конкретного пользователя по tg_id.",
        responses={200: UserSerializer, 404: OpenApiResponse(description="Пользователь не найден")},
    ),
    partial_update=extend_schema(
        tags=["Пользователи"],
        summary="Частичное обновление пользователя",
        description="Обновляет поля пользователя (по tg_id).",
        request=UserSerializer,
        responses={200: UserSerializer, 400: OpenApiResponse(description="Неверные данные")},
    ),
)
class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'tg_id'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsBotAuthenticated | (IsAuthenticated & IsAdmin)]
        elif self.action in ['create', 'retrieve', 'partial_update', 'get_by_phone']:
            permission_classes = [IsBotAuthenticated | IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [perm() if isinstance(perm, type) else perm for perm in permission_classes]

    @extend_schema(
        tags=["Пользователи"],
        description="Управление пользователями (доступно только админам или боту)")
    def list(self, request, *args, **kwargs):
        logger.info("Список всех пользователей")
        response = super().list(request, *args, **kwargs)
        logger.info(f"Успешно получен список {len(response.data)} пользователей")
        return response

    def create(self, request):
        data = request.data
        tg_id = data.get('tg_id')
        if not tg_id:
            logger.error("Потерян tg_id в запросе на создание")
            return Response({"detail": "tg_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Создание/обновление пользователя с tg_id={tg_id}")
        user, created = User.objects.get_or_create(
            tg_id=tg_id,
            defaults={
                'first_name': data.get('first_name', 'Unknown'),
                'last_name': data.get('last_name'),
                'username': data.get('username'),
                'is_bot': data.get('is_bot', False),
                'role': data.get('role', User.Role.USER),
            }
        )

        if not created:
            changed = False
            for field in ['first_name', 'last_name', 'username', 'role']:
                if field in data and getattr(user, field) != data.get(field):
                    setattr(user, field, data.get(field))
                    changed = True
            if changed:
                user.save()
                logger.info(f"Обновленный пользователь tg_id={tg_id} с измененными полями")
            else:
                logger.info(f"Никаких изменений для пользователя tg_id={tg_id}")

        serializer = UserSerializer(user)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        logger.info(f"Пользователь tg_id={tg_id} {'создан' if created else 'получен'}, status={status_code}")
        return Response(serializer.data, status=status_code)

    def retrieve(self, request, *args, **kwargs):
        tg_id = self.kwargs['tg_id']
        logger.info(f"Получение пользователя по tg_id={tg_id}")
        try:
            user = User.objects.get(tg_id=tg_id)
            serializer = UserSerializer(user)
            logger.info(f"Успешно получен пользователь tg_id={tg_id}")
            return Response(serializer.data)
        except User.DoesNotExist:
            logger.error(f"Пользователь с tg_id={tg_id} не найден")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        tg_id = self.kwargs['tg_id']
        logger.info(f"Частичное обновление пользователя с tg_id={tg_id}, data={request.data}")
        try:
            user = User.objects.get(tg_id=tg_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Успешно обновлен пользователь tg_id={tg_id} with data={serializer.data}")
                return Response(serializer.data)
            logger.error(f"Неверные данные для пользователя tg_id={tg_id}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error(f"Пользователь с tg_id={tg_id} не найден")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=["Пользователи"],
        summary="Поиск пользователя по номеру телефона",
        parameters=[
            OpenApiParameter(name="phone_number", type=str, location=OpenApiParameter.PATH, description="Номер телефона (+79991234567)")
        ],
        responses={200: UserSerializer, 404: OpenApiResponse(description="Не найдено"), 400: OpenApiResponse(description="Найдено несколько пользователей")}
    )
    @action(detail=False, methods=['get'], url_path='phone/(?P<phone_number>[0-9+]+)')
    def get_by_phone(self, request, phone_number=None):
        logger.info(f"Fetching user by phone_number={phone_number}")
        try:
            user = User.objects.get(phone_number=phone_number)
            serializer = UserSerializer(user)
            logger.info(f"Successfully fetched user by phone_number={phone_number}")
            return Response(serializer.data)
        except User.DoesNotExist:
            logger.warning(f"User with phone_number={phone_number} not found")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        except User.MultipleObjectsReturned:
            logger.error(f"Multiple users found for phone_number={phone_number}")
            return Response({"detail": "Найдено несколько пользователей с таким номером телефона"},
                            status=status.HTTP_400_BAD_REQUEST)


class UserMeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Пользователи"],
        summary="Текущий пользователь",
        description="Возвращает данные текущего пользователя, его активный аватар и карту лояльности.",
        responses={200: OpenApiResponse(response=dict)},
    )
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        user = request.user
        data = {
            "user": UserSerializer(user).data,
            "is_registered_in_loyalty": hasattr(user, 'loyalty_card'),
        }
        if hasattr(user, 'loyalty_card'):
            data["loyalty_card"] = {
                "card_number": user.loyalty_card.card_number,
                "created_at": user.loyalty_card.created_at,
                "balance": user.loyalty_card.get_balance(),
            }
        user_avatar = (
            UserAvatarProgress.objects
            .filter(user=user, is_active=True)
            .select_related('avatar', 'current_stage')
            .prefetch_related('avatar__avatar_stages__stage')
            .first()
        )
        data["avatar"] = UserAvatarDetailSerializer(user_avatar).data if user_avatar else None
        return Response(data)

    @extend_schema(
        tags=["Пользователи"],
        summary="Мои промокоды",
        description="Возвращает список активных промокодов текущего пользователя.",
        responses={200: UserPromotionDisplaySerializer(many=True), 404: OpenApiResponse(description="Нет промокодов")},
    )
    @action(detail=False, methods=['get'], url_path='me/promocodes')
    def my_promocodes(self, request):
        user = request.user
        user_promotions = UserPromotion.objects.filter(
            user=user,
            promotion__end_date__gte=timezone.now()
        )
        if not user_promotions.exists():
            return Response({'error': 'У Вас нет активных промокодов.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserPromotionDisplaySerializer(user_promotions, many=True)
        return Response({'promotions': serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Пользователи"],
        summary="Детали промокода",
        description="Возвращает информацию по одному промокоду текущего пользователя.",
        responses={200: UserPromotionDisplaySerializer, 404: OpenApiResponse(description="Промокод не найден")},
    )
    @action(detail=True, methods=['get'], url_path='me/promocode')
    def promocode_detail(self, request, pk=None):
        user = request.user
        try:
            user_promotion = UserPromotion.objects.get(pk=pk, user=user)
        except UserPromotion.DoesNotExist:
            return Response({'error': 'Промокод не найден.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserPromotionDisplaySerializer(user_promotion)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Пользователи"],
        summary="Моя реферальная ссылка",
        description="Возвращает персональную ссылку для приглашения друзей.",
        responses={200: OpenApiResponse(response=dict)},
    )
    @action(detail=False, methods=['get'], url_path='me/referral-link')
    def referral_link(self, request):
        user = request.user
        referral, _ = Referral.objects.get_or_create(
            inviter=user,
            invitee=None,
            defaults={'referral_code': Referral.generate_unique_code()}
        )
        bot_username = settings.TELEGRAM_BOT_USERNAME
        referral_link = f"https://t.me/{bot_username}?start={referral.referral_code}"
        return Response({'referral_link': referral_link})

    @extend_schema(
        tags=["Пользователи"],
        summary="Мои аватары",
        description="Возвращает список всех аватаров пользователя.",
        responses={200: UserAvatarProgressSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='me/avatars')
    def my_avatars(self, request):
        user = request.user
        queryset = UserAvatarProgress.objects.filter(user=user).select_related(
            'avatar', 'current_stage'
        ).prefetch_related('avatar__avatar_stages__stage')
        serializer = UserAvatarProgressSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Пользователи"],
        summary="История транзакций по баллам",
        description="Возвращает список всех транзакций пользователя по карте лояльности.",
        responses={200: PointsTransactionSerializer(many=True), 400: OpenApiResponse(description="Нет карты лояльности")},
    )
    @action(detail=False, methods=['get'], url_path='me/points-transactions')
    def points_transactions(self, request):
        user = request.user
        if not hasattr(user, 'loyalty_card'):
            return Response({'error': 'У Вас нет карты лояльности.'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = PointsTransaction.objects.filter(card_id=user.loyalty_card)
        serializer = PointsTransactionSerializer(queryset, many=True)
        return Response(serializer.data)