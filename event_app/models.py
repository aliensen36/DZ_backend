from django.db import models

from dzavod.validators import validate_image


class Event(models.Model):
    """Модель для представления мероприятий."""
    title = models.CharField(max_length=50, unique=True, verbose_name='Название')
    description = models.TextField(max_length=100, verbose_name='Описание')
    info = models.TextField(max_length=450, verbose_name='Дополнительная информация')
    start_date = models.DateTimeField(verbose_name='Дата начала')
    end_date = models.DateTimeField(verbose_name='Дата окончания')
    location = models.CharField(max_length=100, verbose_name='Место проведения')
    photo = models.ImageField(upload_to='events/photos/', validators=[validate_image], verbose_name='Фото')
    # Флажки
    enable_registration = models.BooleanField("Доступна регистрация", default=False)
    enable_tickets = models.BooleanField("Доступна покупка билетов", default=False)
    # Ссылки (необязательные, если флажки выключены)
    registration_url = models.URLField(max_length=70, null=True, blank=True, verbose_name='Ссылка на регистрацию')
    ticket_url = models.URLField(max_length=70, null=True, blank=True, verbose_name='Ссылка на покупку билета')

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