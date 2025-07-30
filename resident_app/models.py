from django.db import models



class Category(models.Model):
    name = models.CharField(max_length=255, null=False, verbose_name='Наименование категории')
    description = models.TextField(null=True, blank=True, verbose_name='Описание категории')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Resident(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Наименование')
    description = models.TextField(null=True, blank=True, max_length=255, verbose_name='Описание')
    info = models.TextField(null=True, blank=True, verbose_name='Дополнительная информация')
    working_time = models.TextField(null=True, blank=True, verbose_name='График работы')
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True, verbose_name='Email')
    phone_number = models.CharField(max_length=16, unique=True, blank=True, null=True, verbose_name='Номер телефона')
    official_website = models.URLField(max_length=255, unique=True, blank=True, null=True, verbose_name='Официальный сайт')
    address = models.CharField(max_length=255, verbose_name='Адрес', default='ул. Большая Новодмитровская, д. 36')
    building = models.CharField(max_length=20, verbose_name='Строение')
    entrance = models.CharField(max_length=50, verbose_name='Вход', null=True, blank=True)
    floor = models.IntegerField(verbose_name='Этаж')
    office = models.IntegerField(unique=True, verbose_name='Офис/Помещение')
    photo = models.ImageField(upload_to='residents/photos/', null=True, blank=True, verbose_name='Фото')
    pin_code = models.CharField(max_length=6, unique=True, verbose_name='Пин-код')
    
    categories = models.ManyToManyField(Category, related_name='residents', verbose_name='Категории')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Резидент'
        verbose_name_plural = 'Резиденты'

    def save(self, *args, **kwargs):
        if not self.pin_code:
            self.pin_code = self._generate_pin_code()
        super().save(*args, **kwargs)

    def _generate_pin_code(self):
        import random
        import string
        while True:
            pin = ''.join(random.choices(string.digits, k=6))
            if not Resident.objects.filter(pin_code=pin).exists():
                return pin

class MapMarker(models.Model):
    resident = models.OneToOneField('Resident', on_delete=models.CASCADE, related_name='map_marker', verbose_name='Резидент')
    x = models.FloatField(verbose_name='Координата X')
    y = models.FloatField(verbose_name='Координата Y')

    def __str__(self):
        return f"Метка {self.resident.name} ({self.x}, {self.y})"

    class Meta:
        verbose_name = 'Метка на карте'
        verbose_name_plural = 'Метки на карте'
