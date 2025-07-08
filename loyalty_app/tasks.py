from celery import shared_task
from django.utils import timezone
from .models import Promotion

@shared_task
def delete_expired_promotions():
    now = timezone.now()
    expired = Promotion.objects.filter(end_date__lt=now)
    count = expired.count()
    expired.delete()
    return f"Удалено {count} акций"