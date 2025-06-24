from django.db import models
from user_app.models import User


class Category(models.Model):
    name = models.CharField(max_length=255, null=False, verbose_name='Наименование категории')
    description = models.TextField(null=True, verbose_name='Описание категории')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Resident(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Наименование')
    description = models.TextField(verbose_name='Описание')
    working_time = models.TextField(verbose_name='График работы')
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True, verbose_name='Email')
    phone_number = models.CharField(max_length=16, unique=True, blank=True, null=True, verbose_name='Номер телефона')
    official_website = models.URLField(max_length=255, unique=True, blank=True, null=True, verbose_name='Официальный сайт')
    full_address = models.CharField(max_length=255, verbose_name='Полный адрес на территории завода')
    floor = models.IntegerField(verbose_name='Этаж')
    office = models.IntegerField(unique=True, verbose_name='Офис/Помещение')

    categories = models.ManyToManyField(Category, related_name='residents')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resident')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Резидент'
        verbose_name_plural = 'Резиденты'



