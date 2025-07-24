from tabnanny import verbose

from django.db import models

class Event(models.Model):
    """Модель для представления мероприятий."""
    title = models.CharField(max_length=255, unique=True, verbose_name='Название мероприятия')
    description = models.TextField(max_length=255, verbose_name='Описание мероприятия')
    info = models.TextField(verbose_name='Дополнительная информация')
    start_date = models.DateTimeField(verbose_name='Начало мероприятия')
    end_date = models.DateTimeField(verbose_name='Окончание мероприятия')
    location = models.CharField(max_length=255, verbose_name='Место проведения')
    photo = models.ImageField(upload_to='events/photos/', verbose_name='Фото мероприятия')
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
