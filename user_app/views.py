import logging

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .auth.permissions import IsAdmin, IsBotAuthenticated
from dotenv import load_dotenv
from django.conf import settings

from .serializers import UserSerializer
from avatar_app.serializers import UserAvatarProgressSerializer, UserAvatarDetailSerializer
from avatar_app.models import UserAvatarProgress
from .models import Referral


load_dotenv()
logger = logging.getLogger(__name__)

from django.contrib.auth import get_user_model
User = get_user_model()

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
    permission_classes = [IsBotAuthenticated | (IsAuthenticated & IsAdmin)]

    @extend_schema(description="Manage users (design_admin only or bot)")
    def list(self, request, *args, **kwargs):
        logger.info("Listing all users")
        response = super().list(request, *args, **kwargs)
        logger.info(f"Successfully listed {len(response.data)} users")
        return response

    def create(self, request):
        data = request.data
        tg_id = data.get('tg_id')
        if not tg_id:
            logger.error("Missing tg_id in create request")
            return Response({"detail": "tg_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Creating/updating user with tg_id={tg_id}")
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
                logger.info(f"Updated user tg_id={tg_id} with changed fields")
            else:
                logger.info(f"No changes for user tg_id={tg_id}")

        serializer = UserSerializer(user)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        logger.info(f"User tg_id={tg_id} {'created' if created else 'retrieved'}, status={status_code}")
        return Response(serializer.data, status=status_code)

    def retrieve(self, request, *args, **kwargs):
        tg_id = self.kwargs['tg_id']
        logger.info(f"Retrieving user with tg_id={tg_id}")
        try:
            user = User.objects.get(tg_id=tg_id)
            serializer = UserSerializer(user)
            logger.info(f"Successfully retrieved user tg_id={tg_id}")
            return Response(serializer.data)
        except User.DoesNotExist:
            logger.error(f"User with tg_id={tg_id} not found")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        tg_id = self.kwargs['tg_id']
        logger.info(f"Partially updating user with tg_id={tg_id}, data={request.data}")
        try:
            user = User.objects.get(tg_id=tg_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Successfully updated user tg_id={tg_id} with data={serializer.data}")
                return Response(serializer.data)
            logger.error(f"Invalid data for user tg_id={tg_id}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error(f"User with tg_id={tg_id} not found")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

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
    permission_classes = [AllowAny] # Потом поменять на IsAuthenticated

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Возвращает текущего пользователя и его активный аватар (если выбран),
        а также информацию о карте лояльности (если зарегистрирован).
        """
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

    @action(detail=False, methods=['patch'], url_path='me/update')
    def update_me(self, request):
        """
        Частично обновляет данные текущего пользователя.
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='me/referral-link')
    def referral_link(self, request):
        """
        Возвращает персональную реферальную ссылку текущего пользователя.
        """
        user = request.user

        # Пытаемся найти или создать referral
        referral, _ = Referral.objects.get_or_create(
            inviter=user,
            invitee=None,
            defaults={'referral_code': Referral.generate_unique_code()}
        )

        bot_username = settings.TELEGRAM_BOT_USERNAME
        referral_link = f"https://t.me/{bot_username}?start={referral.referral_code}"

        return Response({'referral_link': referral_link})
    

class UserAvatarProgressViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserAvatarProgressSerializer

    def get_queryset(self):
        """
        Эндпоинт для просмотра всех аватаров, которых пользователь уже выбрал.
        """
        return UserAvatarProgress.objects.filter(user=self.request.user).select_related(
            'avatar', 'current_stage'
        ).prefetch_related('avatar__avatar_stages__stage')