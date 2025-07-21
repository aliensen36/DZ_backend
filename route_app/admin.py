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
    list_display = ('id', 'name')
    search_fields = ('name',)
    inlines = [FloorInline]


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'building')
    list_filter = ('building',)
    ordering = ('building', 'number')
    search_fields = ('number', 'building__name')
    inlines = [LocationInline]
    readonly_fields = ['floor_map_preview']

    def floor_map_preview(self, obj):
        locations = obj.locations.prefetch_related('corners').all()
        location_dict = {loc.id: loc for loc in locations}
        svg_elements = []

        # 🔹 Отрисовываем локации (многоугольники)
        for loc in locations:
            corners = loc.corners.order_by('order')
            if corners.count() >= 3:
                points_str = " ".join(f"{c.x},{c.y}" for c in corners)
                svg_elements.append(f'''
                    <polygon points="{points_str}" fill="#a0d8ef" stroke="#333" stroke-width="1">
                        <title>{loc.name} ({loc.location_type})</title>
                    </polygon>
                    <text x="{corners[0].x + 5}" y="{corners[0].y - 5}" font-size="10">{loc.name}</text>
                ''')

        # 🔸 Отрисовываем связи (Connection)
        connections = Connection.objects.filter(
            from_location__floor=obj,
            to_location__floor=obj
        )

        for conn in connections:
            from_loc = location_dict.get(conn.from_location_id)
            to_loc = location_dict.get(conn.to_location_id)

            if from_loc and to_loc:
                from_corners = from_loc.corners.order_by('order')
                to_corners = to_loc.corners.order_by('order')

                if from_corners and to_corners:
                    fx = sum(c.x for c in from_corners) / len(from_corners)
                    fy = sum(c.y for c in from_corners) / len(from_corners)
                    tx = sum(c.x for c in to_corners) / len(to_corners)
                    ty = sum(c.y for c in to_corners) / len(to_corners)

                    svg_elements.append(f'''
                        <line x1="{fx}" y1="{fy}" x2="{tx}" y2="{ty}"
                              stroke="green" stroke-width="2">
                            <title>Переход: {from_loc.name} → {to_loc.name}</title>
                        </line>
                    ''')

        # ⬜ SVG с фиксированным размером
        svg_code = f'''
            <svg width="600" height="600" style="border:1px solid #ccc">
                {"".join(svg_elements)}
            </svg>
        '''
        return mark_safe(svg_code)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'floor', 'location_type')
    list_filter = ('location_type', 'floor__building')
    search_fields = ('name',)
    autocomplete_fields = ('floor',)
    inlines = [LocationCornerInline]


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_location', 'to_location', 'bidirectional', 'cost')
    list_filter = ('bidirectional',)
    raw_id_fields = ('from_location', 'to_location')
    autocomplete_fields = ('from_location', 'to_location')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_location', 'end_location')
    list_filter = ('name',)
    search_fields = ('name',)
    autocomplete_fields = ('start_location', 'end_location')
