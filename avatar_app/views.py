# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from .models import Avatar, UserAvatarProgress, Stage, AvatarStage, AvatarOutfit, OutfitPurchase
from loyalty_app.models import PointsTransaction
from .serializers import AvatarSerializer, AvatarDetailSerializer, UserAvatarProgressSerializer


class AvatarViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
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
    permission_classes = [IsAuthenticated] 
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
    

class AvatarOutfitsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    queryset = AvatarOutfit.objects.all()

    def get_active_avatar_and_stage(self, user):
        """
        Возвращает активный прогресс и стадию аватара пользователя.
        """
        active_progress = UserAvatarProgress.objects.filter(
            user=user,
            is_active=True
        ).select_related('avatar', 'current_stage').first()

        if not active_progress:
            return None, None

        avatar_stage = AvatarStage.objects.filter(
            avatar=active_progress.avatar,
            stage=active_progress.current_stage
        ).first()

        if not avatar_stage:
            return None, None

        return active_progress, avatar_stage

    @action(detail=False, methods=['get'], url_path='all-outfits')
    def outfits_list(self, request):
        """
        Возвращает одежду (купленная и еще не купленная).
        """
        user = request.user
        balance = user.loyalty_card.get_balance() if hasattr(user, 'loyalty_card') else 0

        active_progress, avatar_stage = self.get_active_avatar_and_stage(user)
        if not active_progress or not avatar_stage:
            return Response({'detail': 'Активный аватар или его стадия не найдены.'}, status=400)

        outfits = AvatarOutfit.objects.filter(
            avatar_stage=avatar_stage
        ).prefetch_related('custom_animations')

        purchased_ids = set(
            OutfitPurchase.objects.filter(user=user, outfit__avatar_stage=avatar_stage)
            .values_list('outfit_id', flat=True)
        )

        purchased = []
        available = []

        for outfit in outfits:
            item = {
                'id': outfit.id,
                'preview': outfit.outfit.url,
                'price': outfit.price,
                'can_afford': balance >= outfit.price,
            }
            if outfit.id in purchased_ids:
                purchased.append(item)
            else:
                available.append(item)

        return Response({
            'purchased': purchased,
            'available': available
        })

    @action(detail=True, methods=['post'], url_path='buy')
    def buy(self, request, pk=None):
        """
        Покупка аутфита по ID (pk).
        """
        user = request.user
        if not hasattr(user, 'loyalty_card'):
            return Response({'detail': 'У вас нет карты лояльности.'}, status=400)

        outfit = self.get_object()
        balance = user.loyalty_card.get_balance()

        if OutfitPurchase.objects.filter(user=user, outfit=outfit).exists():
            return Response({'detail': 'Вы уже приобрели этот аутфит.'}, status=400)

        if balance < outfit.price:
            return Response({
                'detail': f'Недостаточно бонусов. Баланс: {balance}, требуется: {outfit.price}'
            }, status=400)

        PointsTransaction.objects.create(
            points=-outfit.price,
            price=outfit.price,
            transaction_type='списание',
            card_id=user.loyalty_card,
            resident_id=None
        )

        purchase = OutfitPurchase.objects.create(user=user, outfit=outfit)

        return Response({
            'detail': f'Успешная покупка аутфита #{purchase.outfit.id}. Списано: {outfit.price} бонусов.'
        })

    @action(detail=True, methods=['post'], url_path='wear')
    def wear(self, request, pk=None):
        """
        Надеть аутфит по ID (pk).
        """
        user = request.user
        outfit = self.get_object()

        active_progress, avatar_stage = self.get_active_avatar_and_stage(user)
        if not active_progress or not avatar_stage:
            return Response({'detail': 'Активный аватар или его стадия не найдены.'}, status=400)

        if outfit.avatar_stage != avatar_stage:
            return Response({'detail': 'Аутфит не принадлежит текущей стадии активного аватара.'}, status=400)

        if not OutfitPurchase.objects.filter(user=user, outfit=outfit).exists():
            return Response({'detail': 'Сначала необходимо приобрести аутфит.'}, status=400)

        active_progress.current_outfit = outfit
        active_progress.save(update_fields=['current_outfit'])

        return Response({'detail': f"Аватар '{active_progress.avatar.name}' успешно переодет."})

    @action(detail=True, methods=['post'], url_path='undress')
    def undress(self, request, pk=None):
        """
        Снимает одежду с активного аватара (по ID аватара).
        """
        user = request.user
        avatar = self.get_object()

        active_progress = UserAvatarProgress.objects.filter(
            user=user, is_active=True, avatar=avatar
        ).first()

        if not active_progress:
            return Response({'detail': 'Активный аватар не выбран или ID не совпадает.'}, status=400)

        if not active_progress.current_outfit:
            return Response({'detail': 'На аватаре нет одежды.'}, status=400)

        active_progress.current_outfit = None
        active_progress.save(update_fields=['current_outfit'])

        return Response({'detail': f'Одежда с аватара "{avatar.name}" успешно снята.'})