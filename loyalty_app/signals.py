import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Promotion
from user_app.models import User
from mailing_app.models import Subscription, Mailing
from mailing_app.utils import send_telegram_message
from dzavod.settings import FRONTEND_BASE_URL

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Promotion)
def send_promotion_to_admin(sender, instance, created, **kwargs):
    """
    Отправляет уведомление всем админам с ролью DESIGN_ADMIN в Telegram при создании или изменении статуса акции.
    Включает инлайн-кнопки для подтверждения или отклонения акции.
    """
    if kwargs.get('raw'):  # Пропускать сигналы при загрузке фикстур
        logger.debug(f"Raw signal for Promotion {instance.id}, skipping")
        return

    try:
        logger.debug(f"Сигнал post_save для акции {instance.id} ({instance.title}), created={created}, update_fields={kwargs.get('update_fields')}")

        # Отправляем уведомления только при создании или изменении is_approved
        update_fields = kwargs.get('update_fields') or set()
        if not created and ('is_approved' not in update_fields):
            logger.debug(f"Пропуск уведомления для акции {instance.id}: не создание и не изменение is_approved")
            return

        # Определяем, создаётся или редактируется акция
        action = "создана" if created else "обновлена"

        # Формируем текст уведомления
        text = (
            f"<b>Акция {action}: {instance.title}</b>\n\n"
            f"Период: {instance.start_date.strftime('%d.%m.%Y %H:%M')} - {instance.end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"{instance.discount_or_bonus.capitalize()}: {instance.discount_or_bonus_value}{'%' if instance.discount_or_bonus == 'скидка' else ''}\n\n"
            f"{instance.preview()}\n\n"
            f"Ссылка: {instance.url}\n"
            f"Статус: {'Подтверждена' if instance.is_approved else 'Ожидает подтверждения'}"
        )

        # Определяем инлайн-кнопки
        buttons = [
            [
                {"text": "Подтвердить", "callback_data": f"approve_promotion:{instance.id}"},
                {"text": "Отклонить", "callback_data": f"reject_promotion:{instance.id}"}
            ]
        ]

        # Находим всех админов с ролью DESIGN_ADMIN и tg_id
        admins = User.objects.filter(role=User.Role.DESIGN_ADMIN, tg_id__isnull=False)
        if not admins:
            logger.error("Не найдено админов с ролью DESIGN_ADMIN и tg_id")
            return

        # Отправляем уведомление каждому админу
        for admin in admins:
            logger.debug(f"Отправка уведомления админу {admin.tg_id} для акции {instance.id}")
            success = send_telegram_message(
                user_id=admin.tg_id,
                text=text,
                buttons=buttons,
                image=instance.photo
            )
            if success:
                logger.info(f"Уведомление об акции {instance.id} ({instance.title}) отправлено админу {admin.tg_id}")
            else:
                logger.error(f"Не удалось отправить уведомление об акции {instance.id} ({instance.title}) админу {admin.tg_id}: chat not found or other error")

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления об акции {instance.title}: {e}")

@receiver(post_save, sender=Promotion)
def send_promotion_notification(sender, instance, created, **kwargs):
    logger.debug(f"post_save signal triggered for Promotion {instance.id}, created={created}, update_fields={kwargs.get('update_fields')}")
    if created:
        logger.debug(f"Promotion {instance.id} created, skipping notification")
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        logger.debug(f"Old instance for Promotion {instance.id} retrieved, old_is_approved={old_instance.is_approved}, new_is_approved={instance.is_approved}")
    except sender.DoesNotExist:
        logger.warning(f"Old instance for Promotion {instance.id} not found")
        return 

    # Проверяем, что is_approved изменился с False на True
    if not old_instance.is_approved and instance.is_approved:
        logger.debug(f"Promotion {instance.id} approved, triggering notification")
        resident_categories = instance.resident.categories.all()

        if not resident_categories:
            logger.warning(f"No categories found for resident {instance.resident.id}")
            return

        for category in resident_categories:
            try:
                subscription = Subscription.objects.get(name=category.name)
                logger.debug(f"Found subscription for category {category.name}")
            except Subscription.DoesNotExist:
                logger.warning(f"Subscription for category {category.name} not found")
                continue

            users = subscription.users.all()
            if not users:
                logger.warning(f"No users subscribed to category {category.name}")
                continue

            text = (
                f"<b>{instance.title}</b>\n\n"
                f"{instance.start_date.strftime('%d.%m.%Y %H:%M')} - {instance.end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"{instance.discount_or_bonus.capitalize()}: {instance.discount_or_bonus_value}{'%' if instance.discount_or_bonus == 'скидка' else ''}\n\n"
                f"{instance.preview()}\n\n"
                f"{instance.url}\n"
            )

            buttons = [
                [
                    {
                        "text": "Перейти к акции",
                        "web_app": {"url": f"{FRONTEND_BASE_URL}/miniapp/promotions/{instance.id}"}
                    }
                ]
            ]

            for user in users:
                logger.debug(f"Processing user {user.tg_id} for promotion {instance.id}")
                # Создаём запись в Mailing
                Mailing.objects.create(
                    text=text,
                    image=instance.photo,
                    button_url=f"{FRONTEND_BASE_URL}/miniapp/promotions/{instance.id}",
                    type='text',
                    tg_user_id=user.tg_id
                )

                # Отправляем уведомление
                success = send_telegram_message(
                    user_id=user.tg_id,
                    text=text,
                    buttons=buttons,
                    image=instance.photo
                )
                if success:
                    logger.info(f"Уведомление об акции {instance.id} ({instance.title}) отправлено пользователю {user.tg_id}")
                else:
                    logger.error(f"Не удалось отправить уведомление об акции {instance.id} ({instance.title}) пользователю {user.tg_id}: chat not found or other error")

    else:
        logger.debug(f"No action taken for Promotion {instance.id}, is_approved changed from {old_instance.is_approved} to {instance.is_approved}")