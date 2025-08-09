import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from dzavod.settings import FRONTEND_BASE_URL

from .models import Event
from mailing_app.models import Mailing, Subscription
from mailing_app.utils import send_telegram_message
from mailing_app.utils import send_telegram_message

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Event)
def send_event_notification(sender, instance, created, **kwargs):
    try:
        subscription = Subscription.objects.get(name__iexact='Мероприятия')
        users = subscription.users.filter(enable_notifications=True)

        if created:
            intro = "🎉 Новое мероприятие!"
        else:
            intro = "🔄 Обновление мероприятия!"

        text = (
             f"{intro}\n\n"
            f"🎉 <b>{instance.title}</b>\n"
            f"{instance.description}\n\n"
            f"📆 {instance.start_date.strftime('%d.%m.%Y %H:%M')}-{instance.end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📍 {instance.location}\n"
            f"{instance.preview()}\n\n"
        )

        buttons = [
            [
                {
                    "text": "Перейти к мероприятию",
                    "web_app": {"url": f"{FRONTEND_BASE_URL}/miniapp/events/{instance.id}"}
                }
            ]
        ]

        for user in users:
            # Создаём запись в Mailing
            Mailing.objects.create(
                text=text,
                image=instance.photo,
                button_url=f"{FRONTEND_BASE_URL}/miniapp/events/{instance.id}",
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
                logger.info(f"Уведомление о мероприятии {instance.id} ({instance.title}) отправлено пользователю {user.tg_id}")
            else:
                logger.error(f"Не удалось отправить уведомление о мероприятии {instance.id} ({instance.title}) пользователю {user.tg_id}")

    except Subscription.DoesNotExist:
        logger.error("Подписка 'Мероприятия' не найдена.")