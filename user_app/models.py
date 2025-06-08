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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'