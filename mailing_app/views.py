from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from .models import Mailing
from .serializers import MailingSerializer, MailingListSerializer, MailingCreateSerializer


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
