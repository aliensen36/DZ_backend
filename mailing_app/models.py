from django.db import models
from django.contrib.auth import get_user_model

from user_app.models import User

User = get_user_model()


class Mailing(models.Model):
    """Модель для хранения информации о рассылках"""
    text = models.TextField(verbose_name='Текст сообщения')
    image = models.ImageField(max_length=255, null=True, blank=True, verbose_name='Изображение')
    button_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='Ссылка')
    type = models.CharField(max_length=20, default='text', verbose_name='Тип рассылки')
    tg_user_id = models.BigIntegerField(verbose_name='ID пользователя Telegram')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return f"{self.created_at}"


class Subscription(models.Model):
    """Модель для хранения подписок пользователей"""
    name = models.CharField(max_length=255, unique=True, null=False, verbose_name='Наименование расслыки')
    description = models.TextField(null=True, blank=True, verbose_name='Описание подписки')
    users = models.ManyToManyField(User, related_name='subscriptions', blank=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.name
