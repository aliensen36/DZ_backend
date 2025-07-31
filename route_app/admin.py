from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from .models import Building, Floor, Location, Connection, Route, LocationCorner, LocationType
from django.utils.safestring import mark_safe
from django import forms


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