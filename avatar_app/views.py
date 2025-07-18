# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Prefetch

from .models import Avatar, UserAvatarProgress, Stage, AvatarStage
from .serializers import AvatarSerializer, AvatarDetailSerializer, UserAvatarProgressSerializer


class AvatarViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]  # Потом заменить на IsAuthenticated

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AvatarDetailSerializer
        return AvatarSerializer

    def get_queryset(self):
        """
        Эндпоинт для просмотра доступных аватаров.
        """
        avatar_qs = Avatar.objects.all()

        # Все стадии для конкретного аватара
        if self.kwargs.get("pk"):
            return avatar_qs.prefetch_related('avatar_stages__stage')

        # Для списка — только начальная стадия
        min_stage = Stage.objects.order_by('required_spending').first()
        if not min_stage:
            return Avatar.objects.none()

        return avatar_qs.prefetch_related(
            Prefetch(
                'avatar_stages',
                queryset=AvatarStage.objects.filter(stage=min_stage).select_related('stage'),
                to_attr='start_stage'
            )
        )
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def choose(self, request, pk=None):
        """
        Выбор аватара пользователем. Создаёт UserAvatarProgress и делает его активным.
        Только если нет незавершённых аватаров.
        """
        avatar = self.get_object()
        user = request.user

        user_progress = UserAvatarProgress.objects.filter(user=user).select_related('current_stage')

        if user_progress.exists():
            # Проверка стадии имеющихся аватаров пользователя
            for progress in user_progress:
                next_stage = Stage.objects.filter(
                    required_spending__gt=progress.current_stage.required_spending
                ).order_by('required_spending').first()

                if next_stage:
                    return Response(
                        {'detail': 'Вы не можете выбрать новый аватар, пока не завершены текущие аватары (не достигнута последняя стадия)'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            # Проверка выбран ли аватар
            if user_progress.filter(avatar=avatar).exists():
                return Response({'detail': 'Аватар уже выбран'}, status=status.HTTP_400_BAD_REQUEST)

        # Начальная стадия
        start_stage = Stage.objects.order_by('required_spending').first()
        if not start_stage:
            return Response({'detail': 'Нет доступной стартовой стадии'}, status=status.HTTP_400_BAD_REQUEST)

        progress = UserAvatarProgress.objects.create(
            user=user,
            avatar=avatar,
            current_stage=start_stage,
            total_spending=0,
            is_active=True
        )

        # Всех остальных аватаров выключаем
        UserAvatarProgress.objects.filter(user=user).exclude(id=progress.id).update(is_active=False)

        return Response(UserAvatarProgressSerializer(progress).data, status=status.HTTP_201_CREATED)
    

class UserAvatarProgressViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]  # Потом заменить на IsAuthenticated
    serializer_class = UserAvatarProgressSerializer

    def get_queryset(self):
        return UserAvatarProgress.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Ставит выбранный UserAvatarProgress активным. Остальные становятся неактивными.
        """
        user = request.user
        try:
            selected = UserAvatarProgress.objects.get(id=pk, user=user)
        except UserAvatarProgress.DoesNotExist:
            return Response({'detail': 'Аватар не найден'}, status=404)

        # Сбросить активный флаг у всех
        UserAvatarProgress.objects.filter(user=user).update(is_active=False)

        # Сделать выбранный активным
        selected.is_active = True
        selected.save()

        return Response({'detail': f"Аватар '{selected.avatar.name}' выбран как активный"})