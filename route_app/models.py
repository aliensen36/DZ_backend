from django.db import models


class Building(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Здание'
        verbose_name_plural = 'Здания'


class Floor(models.Model):
    number = models.IntegerField()
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')

    class Meta:
        verbose_name = 'Этаж'
        verbose_name_plural = 'Этажи'
        unique_together = ('number', 'building')


class LocationType(models.TextChoices):
    OFFICE = 'office', 'Офис'
    HALL = 'hall', 'Зал'
    CORRIDOR = 'corridor', 'Коридор'
    ELEVATOR = 'elevator', 'Лифт'
    STAIRS = 'stairs', 'Лестница'
    ENTRY = 'entry', 'Вход'
    OTHER = 'other', 'Другое'

class Location(models.Model):
    name = models.CharField(max_length=100)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='locations')
    location_type = models.CharField(max_length=20, choices=LocationType.choices)
    x = models.FloatField(help_text='Координата X на плане')
    y = models.FloatField(help_text='Координата Y на плане')

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

class Connection(models.Model):
    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='connections_from')
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='connections_to')
    bidirectional = models.BooleanField(default=True)
    cost = models.FloatField(default=1.0, help_text='Стоимость перехода: метры, секунды и т.п.')

    class Meta:
        verbose_name = 'Связь'
        verbose_name_plural = 'Связи'
        unique_together = ('from_location', 'to_location')


class Route(models.Model):
    name = models.CharField(max_length=100)
    start_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_start')
    end_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_end')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'