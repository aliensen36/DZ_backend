from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
from django.db import models
from .models import Mailing, Subscription
from user_app.models import User
from .serializers import MailingSerializer, MailingListSerializer, MailingCreateSerializer, SubscriptionSerializer
from user_app.auth.permissions import IsAdmin, IsBotAuthenticated


class MailingViewSet(viewsets.ModelViewSet):
    queryset = Mailing.objects.all().order_by('-created_at')
    serializer_class = MailingSerializer
    permission_classes = [permissions.AllowAny]  # Временная мера

    def get_serializer_class(self):
        if self.action == 'create':
            return MailingCreateSerializer
        return MailingSerializer

    def perform_create(self, serializer):
        # Добавляем tg_user_id из запроса
        request = self.request
        tg_user_id = request.data.get('tg_user_id')
        if not tg_user_id and request.user.is_authenticated:
            tg_user_id = request.user.tg_id  # Если у вашей модели User есть tg_id

        serializer.save(tg_user_id=tg_user_id)


class AdminSubscriptionViewSet(viewsets.ModelViewSet):
    """
    Админ: может создавать, редактировать, удалять подписки
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdmin]


class UserSubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Пользователь: может смотреть подписки и подписываться/отписываться
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny | IsBotAuthenticated]  #AllowAny заменить потом на IsAuthenticated

    @action(detail=True, methods=["post"], url_path="subscribe")
    def subscribe(self, request, pk=None):
        tg_id = request.data.get("tg_id")
        if not tg_id:
            return Response({"detail": "Поле 'tg_id' обязательно."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(tg_id=tg_id)
        except User.DoesNotExist:
            raise NotFound(detail="Пользователь с таким tg_id не найден.")

        subscription = self.get_object()
        subscription.users.add(user)
        return Response({"detail": f"Вы подписались на '{subscription.name}'"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unsubscribe")
    def unsubscribe(self, request, pk=None):
        tg_id = request.data.get("tg_id")
        if not tg_id:
            return Response({"detail": "Поле 'tg_id' обязательно."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(tg_id=tg_id)
        except User.DoesNotExist:
            raise NotFound(detail="Пользователь с таким tg_id не найден.")

        subscription = self.get_object()
        subscription.users.remove(user)
        return Response({"detail": f"Вы отписались от '{subscription.name}'"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="my")  
    def my_subscriptions(self, request):
        tg_id = request.query_params.get("tg_id")
        if not tg_id:
            return Response({"detail": "Поле 'tg_id' обязательно."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(tg_id=tg_id)
        except User.DoesNotExist:
            raise NotFound(detail="Пользователь с таким tg_id не найден.")

        subscriptions = user.subscriptions.all()
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)