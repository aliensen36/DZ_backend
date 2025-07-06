from celery import shared_task
from django.utils import timezone
from .models import Event

@shared_task
def delete_expired_events():
    now = timezone.now()
    expired = Event.objects.filter(end_date__lt=now)
    count = expired.count()
    expired.delete()
    return f"Удалено {count} мероприятий"