import uuid
import random
import string
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.db import models
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        DESIGN_ADMIN = 'design_admin', 'Админ завода'
        RESIDENT = 'resident', 'Резидент'
        USER = 'user', 'Пользователь'

    tg_id = models.PositiveBigIntegerField(unique=True, db_index=True, verbose_name='TG_ID')
    username = models.CharField(max_length=255, blank=True, null=True, verbose_name='Никнейм из Telegram')
    first_name = models.CharField(max_length=255, verbose_name='Имя из Telegram')
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Фамилия из Telegram')

    # Для карты лояльности
    user_first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Имя')
    user_last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фамилия')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name='Email')
    phone_number = models.CharField(max_length=16, blank=True, null=True, verbose_name='Номер телефона')

    # роли пользователя
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль пользователя'
    )

    is_bot = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Дата регистрации')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Последняя активность')
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    is_staff = models.BooleanField(default=False, verbose_name='Админ')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперюзер')
    enable_notifications = models.BooleanField(default=True, verbose_name='Уведомления')
    referral_code_used = models.CharField(max_length=20, null=True, blank=True, verbose_name='Использованный реферальный код')

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Автоматически выставлять is_staff/is_superuser по роли
        if self.role == self.Role.DESIGN_ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.RESIDENT:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

    def is_design_admin(self):
        return self.role == self.Role.DESIGN_ADMIN

    def is_resident(self):
        return self.role == self.Role.RESIDENT

    def __str__(self):
        return f'{self.first_name}'
    
    def get_or_create_referral_link(self):
        referral, _ = Referral.objects.get_or_create(
            inviter=self,
            defaults={'referral_code': uuid.uuid4().hex[:8]}
        )
        return f"https://t.me/your_bot?start={referral.referral_code}"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Referral(models.Model):
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_sent', verbose_name='Приглашающий')
    invitee = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='referral_used', null=True, blank=True, verbose_name='Кого пригласили')
    referral_code = models.CharField(max_length=20, unique=True, verbose_name='Реферальный код')
    referral_code_used = models.CharField(max_length=20, blank=True, null=True, verbose_name='Использованный реферальный код')
    is_rewarded = models.BooleanField(default=False, verbose_name='Награда начислена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f"{self.inviter} → {self.invitee or 'ожидается'}"
    
    class Meta:
        unique_together = ('inviter', 'invitee')
        verbose_name = 'Реферальная ссылка'
        verbose_name_plural = 'Реферальные ссылки'

    @classmethod
    def generate_unique_code(cls, length=10):
        """Генерирует уникальный реферальный код."""
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            if not cls.objects.filter(referral_code=code).exists():
                return code


class ReferralSettings(models.Model):
    inviter_points = models.PositiveIntegerField(default=0, verbose_name='Баллы для приглашающего')
    invitee_points = models.PositiveIntegerField(default=0, verbose_name='Баллы для приглашаемого')

    def __str__(self):
        return f"Баллы для рефералов: {self.inviter_points} для приглашающего, {self.invitee_points} для приглашаемого"
    
    class Meta:
        verbose_name = 'Настройки реферальных баллов'
        verbose_name_plural = 'Настройки реферальных баллов'