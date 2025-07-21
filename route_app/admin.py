from django.contrib import admin
from .models import Building, Floor, Location, Connection, Route, LocationCorner
from django.utils.safestring import mark_safe


class FloorInline(admin.TabularInline):
    model = Floor
    extra = 1
    ordering = ['number']

class LocationInline(admin.TabularInline):
    model = Location
    extra = 1
    ordering = ['name']

class LocationCornerInline(admin.TabularInline):
    model = LocationCorner
    extra = 0


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [FloorInline]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'floor', 'location_type')
    list_filter = ('location_type', 'floor__building')
    search_fields = ('name',)
    autocomplete_fields = ('floor',)
    inlines = [LocationCornerInline]


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('from_location', 'to_location', 'bidirectional', 'cost')
    list_filter = ('bidirectional',)
    raw_id_fields = ('from_location', 'to_location')
    autocomplete_fields = ('from_location', 'to_location')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_location', 'end_location')
    list_filter = ('name',)
    search_fields = ('name',)
    autocomplete_fields = ('start_location', 'end_location')


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('number', 'building')
    list_filter = ('building',)
    ordering = ('building', 'number')
    search_fields = ('number', 'building__name')
    inlines = [LocationInline]
    readonly_fields = ['floor_map_preview']

    def floor_map_preview(self, obj):
        locations = obj.locations.prefetch_related('corners').all()

        all_x = []
        all_y = []
        for loc in locations:
            for c in loc.corners.order_by('order'):
                all_x.append(c.x)
                all_y.append(c.y)

        if not all_x or not all_y:
            return "Нет данных для отображения плана."

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        padding = 50  # Отступы вокруг плана внутри SVG
        width = max_x - min_x + padding * 2
        height = max_y - min_y + padding * 2

        # Смещение для нормализации координат (чтобы все было в положительных координатах с отступом)
        offset_x = -min_x + padding
        offset_y = -min_y + padding

        # Шаг сетки и диапазон для подписей (от мин до макс с шагом)
        grid_step = 50

        svg_elements = []

        # Рисуем сетку — вертикальные линии и подписи по X
        x_lines = range(int(min_x // grid_step * grid_step), int(max_x + grid_step), grid_step)
        for x in x_lines:
            x_pos = x + offset_x
            svg_elements.append(f'''
                <line x1="{x_pos}" y1="0" x2="{x_pos}" y2="{height}" stroke="#ddd" stroke-width="1"/>
                <text x="{x_pos + 2}" y="14" font-size="12" fill="#666">{x}</text>
            ''')

        # Горизонтальные линии и подписи по Y
        y_lines = range(int(min_y // grid_step * grid_step), int(max_y + grid_step), grid_step)
        for y in y_lines:
            y_pos = y + offset_y
            svg_elements.append(f'''
                <line x1="0" y1="{y_pos}" x2="{width}" y2="{y_pos}" stroke="#ddd" stroke-width="1"/>
                <text x="2" y="{y_pos - 4}" font-size="12" fill="#666">{y}</text>
            ''')

        # Рисуем локации (полигоны)
        for loc in locations:
            corners = loc.corners.order_by('order')
            if corners.count() >= 3:
                points_str = " ".join(f"{c.x + offset_x},{c.y + offset_y}" for c in corners)
                svg_elements.append(f'''
                    <polygon points="{points_str}" fill="#a0d8ef" stroke="#333" stroke-width="1">
                        <title>{loc.name} ({loc.location_type})</title>
                    </polygon>
                    <text x="{corners[0].x + offset_x + 5}" y="{corners[0].y + offset_y - 5}" font-size="12"
                          fill="#000" font-weight="bold" text-anchor="start">{loc.name}</text>
                ''')

        # Здесь можно добавить связи, если нужно, по аналогии с полигоном

        svg_id = f"map-svg-{obj.pk}"

        html_code = f'''
        <div style="position: relative; max-width: 100%; overflow: auto; user-select:none;">
            <svg id="{svg_id}" viewBox="0 0 {width} {height}" width="100%" height="600"
                 style="border:1px solid #ccc; background:#f9f9f9; cursor: grab;"
                 preserveAspectRatio="xMidYMid meet"
                 onmousedown="startPan(evt)" onmouseup="endPan(evt)" onmousemove="pan(evt)">
                {"".join(svg_elements)}
            </svg>
        </div>

        <script>
            let svg = document.getElementById("{svg_id}");
            let isPanning = false;
            let startPoint = {{ x: 0, y: 0 }};
            let viewBox = {{ x: 0, y: 0, width: {width}, height: {height} }};

            function startPan(evt) {{
                isPanning = true;
                startPoint = {{ x: evt.clientX, y: evt.clientY }};
                svg.style.cursor = 'grabbing';
            }}

            function endPan(evt) {{
                isPanning = false;
                svg.style.cursor = 'grab';
            }}

            function pan(evt) {{
                if (!isPanning) return;
                evt.preventDefault();

                let dx = (startPoint.x - evt.clientX) * (viewBox.width / svg.clientWidth);
                let dy = (startPoint.y - evt.clientY) * (viewBox.height / svg.clientHeight);

                viewBox.x += dx;
                viewBox.y += dy;
                svg.setAttribute('viewBox', `${{viewBox.x}} ${{viewBox.y}} ${{viewBox.width}} ${{viewBox.height}}`);

                startPoint = {{ x: evt.clientX, y: evt.clientY }};
            }}

            svg.addEventListener('wheel', function(evt) {{
                evt.preventDefault();
                const scaleFactor = 1.1;
                let direction = evt.deltaY > 0 ? 1 : -1;

                let mx = evt.offsetX;
                let my = evt.offsetY;

                let svgRect = svg.getBoundingClientRect();

                let svgX = viewBox.x + (mx / svg.clientWidth) * viewBox.width;
                let svgY = viewBox.y + (my / svg.clientHeight) * viewBox.height;

                let newWidth = direction > 0 ? viewBox.width * scaleFactor : viewBox.width / scaleFactor;
                let newHeight = direction > 0 ? viewBox.height * scaleFactor : viewBox.height / scaleFactor;

                let newX = svgX - (mx / svg.clientWidth) * newWidth;
                let newY = svgY - (my / svg.clientHeight) * newHeight;

                viewBox = {{ x: newX, y: newY, width: newWidth, height: newHeight }};
                svg.setAttribute('viewBox', `${{viewBox.x}} ${{viewBox.y}} ${{viewBox.width}} ${{viewBox.height}}`);
            }}, {{ passive: false }});
        </script>
        '''

        return mark_safe(html_code)
