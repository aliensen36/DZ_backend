from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.db import models
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    tg_id = models.PositiveBigIntegerField(unique=True, db_index=True,
                                           verbose_name='TG_ID')
    username = models.CharField(max_length=255, blank=True,
                                null=True, verbose_name='Никнейм')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, null=True, blank=True,
                                 verbose_name='Фамилия')
    is_bot = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now,
                                       verbose_name='Дата регистрации')
    last_activity = models.DateTimeField(auto_now=True,
                                         verbose_name='Последняя активность')
    is_staff = models.BooleanField(default=False, verbose_name='Админ')
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперюзер')

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'