import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from mailing_app.models import Subscription
from .models import Category


logger = logging.getLogger(__name__)

@receiver(post_save, sender=Category)
def create_subscription(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.parent is None:
        if Subscription.objects.filter(name=instance.name).exists():
            logger.warning(f'Подписка с именем "{instance.name}" уже существует.')
            return

        Subscription.objects.create(
            name=instance.name,
            description=instance.description
        )

@receiver(pre_delete, sender=Category)
def delete_subscription(sender, instance, **kwargs):
    if instance.parent is None:
        try:
            subscription = Subscription.objects.get(name=instance.name)
            subscription.delete()
        except Subscription.DoesNotExist:
            logger.warning(f'Подписка с именем "{instance.name}" не найдена для удаления.')
            return