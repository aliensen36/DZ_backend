from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Building, Floor, Location, Connection, Route, LocationCorner, LocationType, Tour
from django import forms
from django.utils.html import mark_safe
from django.db import models


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


class LocationTypeForm(forms.ModelForm):
    class Meta:
        model = LocationType
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


@admin.register(LocationType)
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    form = LocationTypeForm

    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
                obj.color
            )
        return '-'

    color_preview.short_description = 'Цвет'


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
    list_display = ('building', 'number' )
    list_display_links = ('building', 'number')
    list_filter = ('building',)
    ordering = ('building', 'number')
    search_fields = ('number', 'building__name')
    inlines = [LocationInline]
    readonly_fields = ['plan_link']

    def plan_link(self, obj):
        url = reverse('floor_plan_preview', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Открыть превью плана</a>', url)

    plan_link.short_description = 'Превью плана'


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    list_display_links = ('name', 'created_at')
    search_fields = ('name', 'residents__name')
    list_filter = ('residents',)
    filter_horizontal = ('residents',)
    readonly_fields = ('image_preview', 'created_at')
    formfield_overrides = {
        models.ImageField: {'help_text': "Допустимые размеры: от 1024x512 до 1280x720 пикселей"},
    }

    fieldsets = (
        (None, {
            'fields': ('name', 'image', 'image_preview', 'description', 'full_description', 'residents', 'created_at')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="200" style="object-fit: cover; border-radius: 8px;" />')
        return 'Нет изображения'

    image_preview.short_description = 'Превью изображения'
