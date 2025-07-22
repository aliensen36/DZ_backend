from django.db import models
from django.utils.html import format_html


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
    # code = models.CharField(max_length=50, unique=True, verbose_name='Код')
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

    # def plan_preview(self):
    #     width, height = 800, 600
    #     polygons = []
    #
    #     for location in self.locations.all():
    #         corners = location.corners.all().order_by('order')
    #         if corners.count() < 3:
    #             continue
    #
    #         points = " ".join(f"{c.x},{-c.y}" for c in corners)  # Инверсия Y
    #         color = location.location_type.color if location.location_type else "#cccccc"
    #         name = location.name
    #
    #         polygons.append(f'''
    #             <polygon points="{points}" fill="{color}" stroke="#000000" stroke-width="1">
    #                 <title>{name}</title>
    #             </polygon>
    #         ''')
    #
    #     # Координатная сетка
    #     grid_lines = []
    #     step = 50
    #     for x in range(0, width + 1, step):
    #         grid_lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{-height}" stroke="#eee" stroke-width="1" />')
    #         grid_lines.append(f'<text x="{x + 2}" y="-5" font-size="10" transform="scale(1,-1)">{x}</text>')
    #
    #     for y in range(0, height + 1, step):
    #         grid_lines.append(f'<line x1="0" y1="{-y}" x2="{width}" y2="{-y}" stroke="#eee" stroke-width="1" />')
    #         grid_lines.append(f'<text x="2" y="{-y - 2}" font-size="10" transform="scale(1,-1)">{y}</text>')
    #
    #     # Вся SVG + JS
    #     svg = f'''
    #         <div style="border:1px solid #ccc; width:{width}px; height:{height}px; overflow:hidden;">
    #             <svg id="floor-map" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"
    #                  viewBox="0 {-height} {width} {height}" style="cursor: grab;">
    #                 <g id="viewport" transform="translate(0, 0) scale(1)">
    #                     {''.join(grid_lines)}
    #                     {''.join(polygons)}
    #                 </g>
    #             </svg>
    #         </div>
    #
    #         <script>
    #         (function() {{
    #             const svg = document.getElementById('floor-map');
    #             const viewport = document.getElementById('viewport');
    #             let scale = 1.0;
    #             let originX = 0;
    #             let originY = 0;
    #             let isPanning = false;
    #             let startX = 0;
    #             let startY = 0;
    #
    #             svg.addEventListener('wheel', (e) => {{
    #                 e.preventDefault();
    #                 const delta = e.deltaY > 0 ? 0.9 : 1.1;
    #                 scale *= delta;
    #                 viewport.setAttribute('transform', `translate(\${{originX}}, \${{originY}}) scale(\${{scale}})`);
    #             }});
    #
    #             svg.addEventListener('mousedown', (e) => {{
    #                 isPanning = true;
    #                 startX = e.clientX;
    #                 startY = e.clientY;
    #                 svg.style.cursor = 'grabbing';
    #             }});
    #
    #             svg.addEventListener('mousemove', (e) => {{
    #                 if (!isPanning) return;
    #                 const dx = e.clientX - startX;
    #                 const dy = e.clientY - startY;
    #                 originX += dx / scale;
    #                 originY += dy / scale;
    #                 viewport.setAttribute('transform', `translate(\${{originX}}, \${{originY}}) scale(\${{scale}})`);
    #                 startX = e.clientX;
    #                 startY = e.clientY;
    #             }});
    #
    #             svg.addEventListener('mouseup', () => {{
    #                 isPanning = false;
    #                 svg.style.cursor = 'grab';
    #             }});
    #         }})();
    #         </script>
    #     '''
    #
    #     return format_html(svg)
    #
    # plan_preview.short_description = 'Превью плана'


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
    cost = models.FloatField(default=1.0, help_text='Стоимость перехода: метры, секунды и т.п.',
                             verbose_name='Стоимость перехода')

    class Meta:
        verbose_name = 'Связь'
        verbose_name_plural = 'Связи'
        unique_together = ('from_location', 'to_location')

    def __str__(self):
        return f'Связь от {self.from_location.name} к {self.to_location.name}'

