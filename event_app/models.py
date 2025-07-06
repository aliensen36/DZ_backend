from django.db import models

class Event(models.Model):
    """Модель для представления мероприятий."""
    title = models.CharField(max_length=255, verbose_name='Название мероприятия')
    description = models.CharField(max_length=255, verbose_name='Описание мероприятия')
    info = models.TextField(verbose_name='Дополнительная информация')
    start_date = models.DateTimeField(verbose_name='Начало мероприятия')
    end_date = models.DateTimeField(verbose_name='Окончание мероприятия')
    location = models.CharField(max_length=255, verbose_name='Место проведения')
    photo = models.CharField(max_length=255, verbose_name='Фото мероприятия')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.title
