import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Promotion
from user_app.models import User
from mailing_app.models import Subscription, Mailing
from mailing_app.utils import send_telegram_message
from dzavod.settings import FRONTEND_BASE_URL

logger = logging.getLogger(__name__)

# Отправляет уведомление всем админам 
def send_promotion_to_admin(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        logger.debug(f"Raw signal for Promotion {instance.id}, skipping")
        return

    try:
        update_fields = kwargs.get('update_fields')
        logger.debug(f"Сигнал post_save для акции {instance.id} ({instance.title}), created={created}, update_fields={update_fields}")

        if not created and (update_fields is None or update_fields == {'is_approved'}):
            logger.debug(f"Пропуск уведомления для акции {instance.id}: обновление только is_approved")
            return

        other_fields_updated = created or any(field != 'is_approved' for field in update_fields or [])
        if not other_fields_updated:
            logger.debug(f"Пропуск уведомления для акции {instance.id}: нет изменений кроме is_approved")
            return
        
        action = "создана" if created else "обновлена"
        text = (
            f"<b>Акция {action}: {instance.title}</b>\n\n"
            f"Описание: {instance.description}\n\n"
            f"Период: {instance.start_date.strftime('%d.%m.%Y %H:%M')} - {instance.end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"{instance.discount_or_bonus.capitalize()}: {instance.discount_or_bonus_value}{'%' if instance.discount_or_bonus == 'скидка' else ''}\n\n"
            f"Ссылка: {instance.url}\n"
            f"Статус: {'Подтверждена' if instance.is_approved else 'Ожидает подтверждения'}"
        )

        buttons = []
        if not instance.is_approved:
            buttons = [
                [
                    {"text": "Подтвердить", "callback_data": f"approve_promotion:{instance.id}"},
                    {"text": "Отклонить", "callback_data": f"reject_promotion:{instance.id}"}
                ]
            ]

        resident = instance.resident
        if not resident:
            logger.error(f"No resident associated with promotion {instance.id}")
            return

        admins = User.objects.filter(
            role=User.Role.DESIGN_ADMIN,
            tg_id__isnull=False
        ).exclude(id=resident.id)
        if not admins:
            logger.error("Не найдено админов с ролью DESIGN_ADMIN и tg_id")
            return

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

# Рассылка пользователям
@receiver(post_save, sender=Promotion)
def send_promotion_notification(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"Promotion {instance.id} was just created — skipping")
        return
    
    if not getattr(instance, '_original_is_approved', False) and instance.is_approved:
        logger.info(f"Promotion {instance.id} was just approved — sending notifications")

        resident_categories = instance.resident.categories.all()
        if not resident_categories:
            logger.warning(f"No categories found for resident {instance.resident.id}")
            return

        for category in resident_categories:
            try:
                subscription = Subscription.objects.get(name=category.name)
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
                f"{instance.discount_or_bonus.capitalize()}: "
                f"{instance.discount_or_bonus_value}{'%' if instance.discount_or_bonus == 'скидка' else ' бонусов'}\n\n"
                f"{instance.preview()}\n\n"
                f"{instance.url}\n"
            )

            buttons = [[
                {
                    "text": "Перейти к акции",
                    "web_app": {"url": f"{FRONTEND_BASE_URL}/miniapp/promotions/{instance.id}"}
                }
            ]]

            for user in users:
                logger.debug(f"Sending promotion {instance.id} to user {user.tg_id}")

                Mailing.objects.create(
                    text=text,
                    image=instance.photo,
                    button_url=f"{FRONTEND_BASE_URL}/miniapp/promotions/{instance.id}",
                    type='text',
                    tg_user_id=user.tg_id
                )

                success = send_telegram_message(
                    user_id=user.tg_id,
                    text=text,
                    buttons=buttons,
                    image=instance.photo
                )

                if success:
                    logger.info(f"Notification sent for promotion {instance.id} to user {user.tg_id}")
                else:
                    logger.error(f"Failed to send promotion {instance.id} to user {user.tg_id}")