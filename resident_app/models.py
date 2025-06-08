from django.db import models

RESIDENT_CATEGORY = [
    ("services", "Услуги и развлечения"),
    ("retail", "Ритейл"),
    ("gastro", "Гастро")
]

class Resident(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Наименование')
    description = models.TextField(verbose_name='Описание')
    working_time = models.TextField(verbose_name='График работы')
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True, verbose_name='Email')
    phone_number = models.CharField(max_length=16, unique=True, blank=True, null=True, verbose_name='Номер телефона')
    official_website = models.URLField(max_length=255, unique=True, blank=True, null=True, verbose_name='Официальный сайт')
    full_address = models.CharField(max_length=255, unique=True, verbose_name='Полный адрес на территории завода')
    floor = models.IntegerField(verbose_name='Этаж')
    office = models.IntegerField(verbose_name='Офис/Помещение')
    category = models.CharField(max_length=32, choices=RESIDENT_CATEGORY, verbose_name='Категория')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Резидент'
        verbose_name_plural = 'Резиденты'