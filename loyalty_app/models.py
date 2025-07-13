import random
import string
from django.db import models
from dzavod import settings
from resident_app.models import Resident

from django.contrib.auth import get_user_model
User = get_user_model()


class LoyaltyCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty_card', verbose_name='Пользователь')
    card_number = models.CharField(max_length=15, unique=True, verbose_name='Номер карты')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Карта лояльности'
        verbose_name_plural = 'Карты лояльности'

    def __str__(self):
        return f'Карта {self.card_number} ({self.user})'

    def generate_card_number(self):
        while True:
            number = ''.join(random.choices(string.digits, k=6))
            formatted_number = ' '.join([number[i:i + 3] for i in range(0, 6, 3)])  # Например: '123 456'
            if not LoyaltyCard.objects.filter(card_number=formatted_number).exists():
                return formatted_number

    def save(self, *args, **kwargs):
        if not self.card_number:
            self.card_number = self.generate_card_number()
        super().save(*args, **kwargs)


TRANSACTION_TYPE =[
    ('начисление', 'начисление'),
    ('списание', 'списание')
]

class PointsTransaction(models.Model):
    points = models.IntegerField(null=False, verbose_name='Баллы (-/+): списание или пополнение')
    price = models.FloatField(null=False, verbose_name='Сумма с которой начислились баллы или списались')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE, verbose_name='Тип транзакции')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата транзакции')

    card_id = models.ForeignKey(LoyaltyCard, on_delete=models.CASCADE, related_name='transactions')
    resident_id = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='transactions')

    class Meta:
        verbose_name = 'Транзакция баллов'
        verbose_name_plural = 'Транзакции баллов'

    def __str__(self):
        return f"{self.transaction_type.capitalize()} {self.points} баллов"
    

class Promotion(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название акции')
    description = models.TextField(verbose_name='Описание акции')
    start_date = models.DateTimeField(verbose_name='Дата начала акции')
    end_date = models.DateTimeField(verbose_name='Дата окончания акции')
    photo = models.ImageField(upload_to='promotions/photos/', verbose_name='Фото акции')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрена ли акция')
    url = models.URLField(max_length=255, verbose_name='Ссылка на участие в акции')
    discount_or_bonus = models.CharField(max_length=10, choices=[('скидка', 'Скидка'), ('бонус', 'Бонус')], verbose_name='Тип скидки или бонуса')
    discount_or_bonus_value = models.FloatField(verbose_name='Значение скидки или бонуса', help_text='Введите значение скидки или бонуса, например 10% или 100 баллов')

    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='promotions', verbose_name='Резидент')

    def preview(self):
        """Возвращает превью акции."""
        return self.description[:255] + '...' if len(self.description) > 255 else self.info

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'

    def __str__(self):
        return self.title