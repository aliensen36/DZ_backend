from datetime import timezone
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from user_app.auth.permissions import IsBotAuthenticated, IsAdmin
from user_app.serializers import UserSerializer
from .models import LoyaltyCard, PointsTransaction, Promotion, PointsSystemSettings
from resident_app.models import Resident
from .serializers import PointsTransactionSerializer, PromotionSerializer, UserPromotionSerializer, PointsSystemSettingsSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes, OpenApiExample
from avatar_app.models import UserAvatarProgress

from django.contrib.auth import get_user_model
User = get_user_model()

import logging
logger = logging.getLogger(__name__)

class LoyaltyCardViewSet(viewsets.ViewSet):
    # permission_classes = [AllowAny]  # Только в разработке
    permission_classes = [IsBotAuthenticated | IsAuthenticated]
    lookup_field = "user__tg_id"

    def get_balance(self, user):
        logger.debug(f"Get balance for user tg_id={user.tg_id}")
        card = LoyaltyCard.objects.filter(user=user).first()
        if not card:
            logger.warning(f"No loyalty card found for user tg_id={user.tg_id}")
            return 0
        return card.get_balance()

    def generate_card_image(self, user, card_number):
        cream_light = (255, 255, 230)
        img = Image.new('RGB', (800, 500), color=cream_light)
        draw = ImageDraw.Draw(img)

        try:
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'arial.ttf')
            font_bold_path = os.path.join(os.path.dirname(__file__), 'fonts', 'arialbd.ttf')
            font_large = ImageFont.truetype(font_path, 40)
            font_medium = ImageFont.truetype(font_path, 30)
            font_medium_bold = ImageFont.truetype(font_bold_path, 30)
            font_small = ImageFont.truetype(font_path, 25)
        except Exception as e:
            logger.warning(f"Failed to load fonts, using default: {e}")
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_medium_bold = ImageFont.load_default()
            font_small = ImageFont.load_default()

        logo_path = os.path.join(settings.MEDIA_ROOT, 'loyalty_cards', 'logo.png')
        logo_y = 20
        logo_x = 30
        logo_height = 0
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((150, 150), Image.Resampling.LANCZOS)
            logo_height = logo.height
            img.paste(logo, (logo_x, logo_y), logo)
        else:
            logger.warning(f"Логотип не найден по пути: {logo_path}")

        first_name = getattr(user, 'user_first_name', None) or getattr(user, 'first_name', 'Не указано')
        last_name = getattr(user, 'user_last_name', None) or getattr(user, 'last_name', 'Не указано')
        balance = self.get_balance(user)

        logo_title_spacing = 50
        title_text = "Карта лояльности"
        bbox_title = draw.textbbox((0, 0), title_text, font=font_large)
        title_width = bbox_title[2] - bbox_title[0]
        title_x = (img.width - title_width) // 2
        title_y = logo_y + logo_height + logo_title_spacing
        draw.text((title_x, title_y), title_text, font=font_large, fill=(0, 0, 0))

        title_spacing = 50
        base_y = title_y + bbox_title[3] - bbox_title[1] + title_spacing

        full_name = f"{first_name} {last_name}"
        line_spacing = 50
        draw.text((50, base_y), full_name, font=font_medium, fill=(0, 0, 0))

        bbox_name = draw.textbbox((0, 0), full_name, font=font_medium)
        name_height = bbox_name[3] - bbox_name[1]
        base_y += name_height + line_spacing

        balance_prefix = "Баланс: "
        balance_suffix = " бонусов"
        x_pos = 50
        draw.text((x_pos, base_y), balance_prefix, font=font_medium, fill=(0, 0, 0))
        prefix_width = draw.textbbox((0, 0), balance_prefix, font=font_medium)[2]
        draw.text((x_pos + prefix_width, base_y), str(balance), font=font_medium_bold, fill=(0, 0, 0))
        balance_width = draw.textbbox((0, 0), str(balance), font=font_medium_bold)[2]
        draw.text((x_pos + prefix_width + balance_width, base_y), balance_suffix, font=font_medium, fill=(0, 0, 0))

        card_number_text = f"№ {card_number}"
        bbox_card = draw.textbbox((0, 0), card_number_text, font=font_small)
        card_width = bbox_card[2] - bbox_card[0]
        card_height = bbox_card[3] - bbox_card[1]
        card_x = (img.width - card_width) // 2
        card_y = img.height - card_height - 20
        draw.text((card_x, card_y), card_number_text, font=font_small, fill=(0, 0, 0))

        mascot_path = os.path.join(settings.MEDIA_ROOT, 'loyalty_cards', 'mascot.png')
        if os.path.exists(mascot_path):
            mascot = Image.open(mascot_path).convert("RGBA")
            mascot.thumbnail((200, 200), Image.Resampling.LANCZOS)
            mascot_width, mascot_height = mascot.size
            mascot_x = img.width - mascot_width - 20
            mascot_y = img.height - mascot_height - 20
            img.paste(mascot, (mascot_x, mascot_y), mascot)
        else:
            logger.warning(f"Маскот не найден по пути: {mascot_path}")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

    @action(detail=True, methods=['get'], url_path='card-image')
    def loyalty_card_image(self, request, user__tg_id=None):
        logger.info(f"Запрошено изображение карты для tg_id={user__tg_id}")
        user = User.objects.filter(tg_id=user__tg_id).first()
        if not user:
            logger.error(f"Пользователь с tg_id={user__tg_id} не найден")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, существует ли карта, и создаем, если отсутствует
        card, created = LoyaltyCard.objects.get_or_create(user=user)
        if created:
            logger.info(f"Создана новая карта лояльности для tg_id={user__tg_id}")

        try:
            image = self.generate_card_image(user, card.card_number)
        except Exception as e:
            logger.error(f"Ошибка генерации изображения карты для tg_id={user__tg_id}: {e}")
            return Response({"detail": "Ошибка генерации изображения"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return HttpResponse(image.getvalue(), content_type='image/png')

    @action(detail=True, methods=['get'], url_path='card-number')
    def card_number(self, request, user__tg_id=None):
        logger.info(f"Запрошен номер карты для tg_id={user__tg_id}")
        user = User.objects.filter(tg_id=user__tg_id).first()
        if not user:
            logger.error(f"Пользователь с tg_id={user__tg_id} не найден")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, существует ли карта, и создаем, если отсутствует
        card, created = LoyaltyCard.objects.get_or_create(user=user)
        if created:
            logger.info(f"Создана новая карта лояльности для tg_id={user__tg_id}")

        return Response({"card_number": card.card_number}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'card-number/(?P<card_number>[0-9\s]+)')
    def get_by_card_number(self, request, card_number=None):
        logger.info(f"Fetching user by card_number={card_number}")
        try:
            # Нормализуем номер карты (с пробелом, например, "123 456")
            card_number_clean = card_number.strip()
            card = LoyaltyCard.objects.get(card_number=card_number_clean)
            user = card.user
            serializer = UserSerializer(user)
            logger.info(f"Successfully fetched user by card_number={card_number}")
            return Response(serializer.data)
        except LoyaltyCard.DoesNotExist:
            logger.warning(f"Card with card_number={card_number} not found")
            return Response({"detail": "Карта не найдена"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            logger.error(f"User associated with card_number={card_number} not found")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='card-id')
    def card_id(self, request, user__tg_id=None):
        logger.info(f"Запрошен ID карты для tg_id={user__tg_id}")
        user = User.objects.filter(tg_id=user__tg_id).first()
        if not user:
            logger.error(f"Пользователь с tg_id={user__tg_id} не найден")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, существует ли карта, и создаем, если отсутствует
        card, created = LoyaltyCard.objects.get_or_create(user=user)
        if created:
            logger.info(f"Создана новая карта лояльности для tg_id={user__tg_id}")

        return Response({"card_id": card.id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'card-number/(?P<card_number>[0-9\s]+)')
    def get_by_card_number(self, request, card_number=None):
        logger.info(f"Fetching user by card_number={card_number}")
        try:
            # Нормализуем номер карты (с пробелом, например, "123 456")
            card_number_clean = card_number.strip()
            card = LoyaltyCard.objects.get(card_number=card_number_clean)
            user = card.user
            serializer = UserSerializer(user)
            logger.info(f"Successfully fetched user by card_number={card_number}")
            return Response(serializer.data)
        except LoyaltyCard.DoesNotExist:
            logger.warning(f"Card with card_number={card_number} not found")
            return Response({"detail": "Карта не найдена"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            logger.error(f"User associated with card_number={card_number} not found")
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)


class PointsTransactionResidenrViewSet(viewsets.ModelViewSet):
    queryset = PointsTransaction.objects.all()
    serializer_class = PointsTransactionSerializer
    # permission_classes = [AllowAny]  # Только в разработке
    # permission_classes = [IsBotAuthenticated | IsResident]
    permission_classes = [IsBotAuthenticated | IsAuthenticated]

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
        description="Метод для начисления бонусов по сумме.",
        request=PointsTransactionSerializer,
        responses={
            201: OpenApiResponse(description="Транзакция успешно создана", response=PointsTransactionSerializer),
            400: OpenApiResponse(description="Ошибка при начислении бонусов")
        },
        parameters=[
            OpenApiParameter(
                name="price",  
                type=OpenApiTypes.NUMBER, 
                description="Сумма для начисления бонусов (в рублях)", 
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

        # Получаем resident_id из заголовка
        resident_id = request.headers.get('X-Resident-ID')
        if not resident_id:
            return Response({'error': 'Не передан X-Resident-ID в заголовке'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not Resident.objects.filter(id=resident_id).exists():
            return Response({'error': 'Резидент с таким ID не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        card_id = request.data.get('card_id')
        try:
            card = LoyaltyCard.objects.select_related('user').get(id=card_id)
        except LoyaltyCard.DoesNotExist:
            return Response({'error': 'Карта лояльности не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        points_settings = PointsSystemSettings.objects.first()

        if not points_settings:
            return Response({'error': 'Настройки программы лояльности не найдены'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            points_per_100_rub = points_settings.points_per_100_rubles

        points_to_accrue = round(int(price) * points_per_100_rub // 100)

        if points_to_accrue <= 0:
            return Response({'error': 'Недостаточно суммы для начисления бонусов'}, status=status.HTTP_400_BAD_REQUEST)

        user = card.user

        # Обновляем прогресс аватара пользователя
        user_avatar = UserAvatarProgress.objects.filter(user=user, is_active=True).first()
        if user_avatar:
            user_avatar.total_spending += price
            user_avatar.save()
            user_avatar.check_for_upgrade()

        transaction_data = {
            'price': price,
            'points': points_to_accrue,
            'transaction_type': 'начисление',
            'card_id': request.data.get('card_id'),
            'resident_id': resident_id,
        }

        serializer = self.get_serializer(data=transaction_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class PromotionViewSet(viewsets.ModelViewSet):
    serializer_class = PromotionSerializer
    # permission_classes = [AllowAny]  # Только в разработке
    # permission_classes = [IsBotAuthenticated | (IsAuthenticated & IsResident)]
    permission_classes = [IsBotAuthenticated | IsAuthenticated]

    def get_queryset(self):
        queryset = Promotion.objects.all().filter(is_approved=True)

        resident_id = self.request.query_params.get('resident')
        if resident_id:
            try:
                queryset = queryset.filter(resident_id=int(resident_id))
            except ValueError:
                logger.error(f"Invalid resident_id in query parameter: {resident_id}")
                queryset = queryset.none()
        return queryset
    
    def get_object(self):
        # Снимаем фильтр is_approved только для confirm/reject
        if self.action in ["approve", "reject"]:
            return Promotion.objects.get(pk=self.kwargs["pk"])
        return super().get_object()
    
    def create(self, request, *args, **kwargs):
        if 'photo' not in request.FILES:
            return Response({"photo": ["Фото мероприятия обязательно."]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.photo = request.FILES['photo']
        instance.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)

            updated_fields = []
            for field, value in serializer.validated_data.items():
                if field != 'is_approved' and getattr(instance, field) != value:
                    setattr(instance, field, value)
                    updated_fields.append(field)

            if 'photo' in request.FILES:
                instance.photo = request.FILES['photo']
                updated_fields.append('photo')

            if updated_fields:
                instance.is_approved = False
                updated_fields.append('is_approved')

            if updated_fields:
                instance.save(update_fields=updated_fields)
                logger.info(f"Promotion {instance.id} updated with fields: {updated_fields}, is_approved set to False")
            else:
                logger.debug(f"No fields changed for promotion {instance.id}")

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Promotion.DoesNotExist:
            logger.error(f"Promotion {kwargs.get('pk')} not found")
            return Response({'error': 'Акция не найдена'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating promotion {kwargs.get('pk')}: {str(e)}")
            return Response({'error': f'Ошибка при обновлении акции: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsBotAuthenticated])
    def approve(self, request, pk=None):
        """
        Подтверждает акцию, устанавливая is_approved=True.
        """
        try:
            promotion = self.get_object()
            logger.debug(f"Approving promotion {promotion.id}, current is_approved={promotion.is_approved}")
            promotion.is_approved = True
            promotion.save(update_fields=['is_approved'])  # Указываем, что обновляется только is_approved
            logger.info(f"Promotion {promotion.id} approved successfully, triggering post_save")
            return Response({'status': 'Акция подтверждена'}, status=status.HTTP_200_OK)
        except Promotion.DoesNotExist:
            return Response(
                {'error': 'Акция не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error approving promotion {pk}: {str(e)}")
            return Response(
                {'error': f'Ошибка при подтверждении акции: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsBotAuthenticated])
    def reject(self, request, pk=None):
        """
        Отклоняет акцию, устанавливая is_approved=False и удаляет её из базы.
        """
        try:
            promotion = self.get_object()
            promotion.is_approved = False
            promotion.save(update_fields=['is_approved'])  # Обновляем только статус

            # Удаляем акцию из базы данных
            promotion.delete()
            
            return Response({'status': 'Акция отклонена и удалена'}, status=status.HTTP_200_OK)
        except Promotion.DoesNotExist:
            return Response(
                {'error': 'Акция не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Ошибка при отклонении акции: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=True, methods=['post'], url_path='buy-promocode')
    def buy_promocode(self, request, pk=None):
        user = request.user

        try:
            promotion = self.get_object()
        except Promotion.DoesNotExist:
            return Response({'error': 'Акция не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        if promotion.end_date < timezone.now():
            return Response({'error': 'Акция уже завершилась.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            card = LoyaltyCard.objects.get(user=user)
        except LoyaltyCard.DoesNotExist:
            return Response({'error': 'Карта не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        points_settings = PointsSystemSettings.objects.first()
        if not points_settings:
            return Response({'error': 'Настройки программы лояльности не найдены'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        points_per_1_percent = points_settings.points_per_1_percent
        current_balance = card.get_balance()
        points_to_deduct = round(float(promotion.discount_percent) * points_per_1_percent)

        if current_balance < points_to_deduct:
            return Response({
                'error': f'Недостаточно бонусов.\n'
                        f'Баланс: <b>{current_balance}</b>.\n'
                        f'требуется: <b>{points_to_deduct}</b>'
            }, status=status.HTTP_400_BAD_REQUEST)

        PointsTransaction.objects.create(
            points=points_to_deduct,
            price=0.0,
            transaction_type='списание',
            card_id=card,
            resident_id=promotion.resident
        )

        serializer = UserPromotionSerializer(data={'user': user.id, 'promotion': promotion.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'Промокод успешно активирован.',
            'promotion': promotion.title,
            'promotional_code': promotion.promotional_code,
            'discount_percent': promotion.discount_percent,
            'points_to_deduct': points_to_deduct
        }, status=status.HTTP_201_CREATED)
        

class PointsSystemSettingsViewSet(viewsets.ViewSet):
    queryset = PointsSystemSettings.objects.all()
    serializer_class = PointsSystemSettingsSerializer
    permission_classes = [IsBotAuthenticated | IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="single")
    def get_single(self, request):
        settings = PointsSystemSettings.objects.first()
        if not settings:
            return Response({"detail": "Настройки не найдены"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(settings)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if PointsSystemSettings.objects.exists():
            return Response(
                {"detail": "Настройки программы лояльности уже созданы"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        settings = serializer.save()
        return Response(self.serializer_class(settings).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None, *args, **kwargs):
        settings = PointsSystemSettings.objects.filter(pk=pk).first()
        if not settings:
            return Response({"detail": "Настройки программы лояльности не найдены"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)



