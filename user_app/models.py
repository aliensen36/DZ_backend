from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    tg_id = models.PositiveBigIntegerField(unique=True, db_index=True, verbose_name='ID')
    tg_username = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ник')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name}, ' + (f' {self.tg_username}' if self.tg_username else f'{self.tg_id}')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'