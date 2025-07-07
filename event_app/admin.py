from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import *

from django.contrib import admin
from django_celery_beat.models import SolarSchedule, ClockedSchedule

# Убираем ненужные модели из админки
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'date_range',
        'location',
        'is_active',
        'photo_preview_small',
        'created_at'
    )
    list_display_links = ('title',)
    list_filter = ('start_date', 'end_date', 'location')
    search_fields = ('title', 'description', 'info', 'location')
    list_per_page = 20
    ordering = ('start_date',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'info')
        }),
        ('Дата и место проведения', {
            'fields': (('start_date', 'end_date'), 'location')
        }),
        ('Фото мероприятия', {
            'fields': ('photo', 'photo_preview')
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'photo_preview')

    @admin.display(description='Период проведения')
    def date_range(self, obj):
        start = timezone.localtime(obj.start_date).strftime('%d.%m.%Y')
        end = timezone.localtime(obj.end_date).strftime('%d.%m.%Y')
        return f'{start} — {end}'

    @admin.display(description='Сейчас идёт', boolean=True)
    def is_active(self, obj):
        now = timezone.now()
        return obj.start_date <= now <= obj.end_date

    @admin.display(description='Фото')
    def photo_preview_small(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:40px;" />', obj.photo)
        return '—'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height:200px;" />', obj.photo)
        return 'Нет изображения'