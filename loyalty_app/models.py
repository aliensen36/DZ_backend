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
    
    def get_balance(self):
        return PointsTransaction.objects.filter(card_id=self.id).aggregate(total=models.Sum('points'))['total'] or 0

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
    points = models.IntegerField(null=False, verbose_name='Баллы')
    price = models.FloatField(null=False, verbose_name='Сумма операции')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE, verbose_name='Тип транзакции')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата транзакции')

    card_id = models.ForeignKey(LoyaltyCard, on_delete=models.CASCADE, related_name='transactions', verbose_name='Карта лояльности')
    resident_id = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='transactions', verbose_name='Резидент')

    class Meta:
        verbose_name = 'Транзакция баллов'
        verbose_name_plural = 'Транзакции баллов'

    def __str__(self):
        return f"{self.transaction_type.capitalize()} {self.points} баллов"
    

class PointsSystemSettings(models.Model):
    points_per_100_rubles = models.PositiveIntegerField(verbose_name='Кол-во баллов за 100 р.')
    points_per_1_percent = models.PositiveIntegerField(verbose_name='Кол-во баллов за 1%')

    def save(self, *args, **kwargs):
        if not self.pk and PointsSystemSettings.objects.exists():
            raise ValueError('You can only create one entry PointsSystemSettings')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Настройки программы лояльности'
        verbose_name_plural = 'Настройки программы лояльности'
    

class Promotion(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название акции')
    description = models.TextField(max_length=750, verbose_name='Описание акции')
    start_date = models.DateTimeField(verbose_name='Дата начала акции')
    end_date = models.DateTimeField(verbose_name='Дата окончания акции')
    photo = models.ImageField(upload_to='promotions/photos/', verbose_name='Фото акции')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрена ли акция')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=False, blank=False, verbose_name='Процент скидки')
    promotional_code = models.CharField(max_length=20, unique=True, verbose_name='Промокод')
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='promotions', verbose_name='Резидент')

    def preview(self):
        """Возвращает превью акции."""
        if len(self.description) > 255:
            return self.description[:255] + '...'
        return self.description
    
    # Сохраняет оригинальное значение поля при инициализации
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_is_approved = self.is_approved

    def percent_equals_points(self):
        """Возвращает процент скидки и количество бонусов."""
        try:
            settings_instance = PointsSystemSettings.objects.first()
            if settings_instance:
                points = round(float(self.discount_percent) * settings_instance.points_per_1_percent)
                return f"{self.discount_percent}% = {points} бонусов"
            else:
                return "Настройки бонусов не заданы"
        except Exception as e:
            return f"Ошибка: {e}"

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'

    def __str__(self):
        return self.title
    

class UserPromotion(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_promotions')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='purchased_by_users')
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'promotion')
        verbose_name = 'Участие пользователя в акции'
        verbose_name_plural = 'Участия пользователей в акциях'
        ordering = ['-redeemed_at']

    def __str__(self):
        return f"{self.user} — {self.promotion.title}"
    

