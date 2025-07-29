from tabnanny import verbose

from django.db import models
from rest_framework.exceptions import ValidationError


class Event(models.Model):
    """Модель для представления мероприятий."""
    title = models.CharField(max_length=255, unique=True, verbose_name='Название мероприятия')
    description = models.TextField(max_length=255, verbose_name='Описание мероприятия')
    info = models.TextField(verbose_name='Дополнительная информация')
    start_date = models.DateTimeField(verbose_name='Начало мероприятия')
    end_date = models.DateTimeField(verbose_name='Окончание мероприятия')
    location = models.CharField(max_length=255, verbose_name='Место проведения')
    photo = models.ImageField(upload_to='events/photos/', verbose_name='Фото мероприятия')
    # Флажки
    enable_registration = models.BooleanField("Доступна регистрация", default=False)
    enable_tickets = models.BooleanField("Доступна покупка билетов", default=False)
    # Ссылки (необязательные, если флажки выключены)
    registration_url = models.URLField(null=True, blank=True, verbose_name='Ссылка на регистрацию')
    ticket_url = models.URLField(null=True, blank=True, verbose_name='Ссылку на покупку билета')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')


    def preview(self):
        """Возвращает превью мероприятия."""
        if len(self.info) > 255:
            return self.info[:255] + '...'
        return self.info

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.title

    def clean(self):
        if self.enable_registration and not self.registration_url:
            raise ValidationError(
                {"registration_url": "Укажите ссылку на регистрацию, если она включена."}
            )

        if self.enable_tickets and not self.ticket_url:
            raise ValidationError(
                {"ticket_url": "Укажите ссылку на покупку билетов, если она включена."}
            )

