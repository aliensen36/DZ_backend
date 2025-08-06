from django.db import models
from resident_app.models import Resident

class Building(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Здание'
        verbose_name_plural = 'Здания'

    def __str__(self):
        return self.name


class LocationType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    color = models.CharField(
        max_length=7,
        default='#dddddd',
        verbose_name='Цвет (hex)',
        help_text='Например, #ff0000 для красного'
    )

    class Meta:
        verbose_name = 'Тип локации'
        verbose_name_plural = 'Типы локаций'

    def __str__(self):
        return self.name


class Floor(models.Model):
    number = models.IntegerField(verbose_name='Номер')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors', verbose_name='Здание')

    class Meta:
        verbose_name = 'Этаж'
        verbose_name_plural = 'Этажи'
        unique_together = ('number', 'building')

    def __str__(self):
        return f'{self.building.name} - {self.number}'


class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='locations', verbose_name='Этаж')
    location_type = models.ForeignKey(LocationType, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='locations', verbose_name='Тип локации')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

    def get_center(self):
        corners = list(self.corners.all())
        if not corners:
            return None
        avg_x = sum(c.x for c in corners) / len(corners)
        avg_y = sum(c.y for c in corners) / len(corners)
        return avg_x, avg_y


class LocationCorner(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='corners', verbose_name='Локация')
    x = models.FloatField(help_text='Координата X угла')
    y = models.FloatField(help_text='Координата Y угла')
    order = models.PositiveSmallIntegerField(help_text='Порядок обхода углов (по часовой стрелке)',
                                             verbose_name='Порядок обхода углов')

    class Meta:
        verbose_name = 'Угол'
        verbose_name_plural = 'Углы'
        unique_together = ('location', 'order')
        ordering = ['order']

    def __str__(self):
        return f'Угол {self.order} для {self.location.name}'


class Route(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    start_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_start',
                                       verbose_name='Начальная локация')
    end_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_end',
                                     verbose_name='Конечная локация')
    image = models.ImageField(upload_to='routes/images/', verbose_name='Фото')
    description = models.models.TextField(max_length=255, verbose_name='Описание')
    fullDescription = models.CharField(verbose_name='Полное описание')
    residents = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='routes', verbose_name='Резидент')

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'

    def __str__(self):
        return self.name


class Connection(models.Model):
    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='connections_from',
                                      verbose_name='Откуда')
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='connections_to',
                                    verbose_name='Куда')
    bidirectional = models.BooleanField(default=True, verbose_name='Двунаправленная связь')
    cost = models.FloatField(default=1.0, help_text='Стоимость перехода, м',
                             verbose_name='Стоимость перехода, м')

    class Meta:
        verbose_name = 'Связь'
        verbose_name_plural = 'Связи'
        unique_together = ('from_location', 'to_location')

    def __str__(self):
        return f'Связь от {self.from_location.name} к {self.to_location.name}'

