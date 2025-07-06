from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event
from mailing_app.models import Mailing, Subscription
from mailing_app.utils import send_telegram_message
from dzavod.settings import FRONTEND_BASE_URL

@receiver(post_save, sender=Event)
def send_event_notification(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        subscription = Subscription.objects.get(name__iexact='Мероприятия')
        users = subscription.users.all()

        text = (
            f"🎉 {instance.title}\n\n"
            f"📍 {instance.location}\n"
            f"🕒 {instance.start_date.strftime('%d.%m.%Y %H:%M')}-{instance.end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"{instance.description}"
        )

        for user in users:
            Mailing.objects.create(
                text=text,
                image=instance.photo,
                button_url=f"{FRONTEND_BASE_URL}/miniapp/events/{instance.id}",
                type='text',
                tg_user_id=user.tg_id
            )

            send_telegram_message(
                user_id=user.tg_id,
                text=text,
                button_url=f"{FRONTEND_BASE_URL}/miniapp/events/{instance.id}"
            )

    except Subscription.DoesNotExist:
        print("⚠️ Подписка 'Мероприятия' не найдена.")