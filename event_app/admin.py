from django.utils.html import format_html
from django.utils import timezone
from django.contrib import admin
from django_celery_beat.models import SolarSchedule, ClockedSchedule

from .models import Event
from .forms import EventAdminForm

# Убираем ненужные модели из админки
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = (
        'title',
        'date_range',
        'location',
        'is_active',
    )
    list_display_links = (
        'title',
        'date_range',
        'location',
        'is_active',)
    list_filter = ('start_date', 'end_date', 'location')
    search_fields = ('title', 'description', 'info', 'location')
    list_per_page = 20
    ordering = ('start_date',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Основная информация', {
                'fields': ('title', 'description', 'info')
            }),
            ('Дата и место проведения', {
                'fields': (('start_date', 'end_date'), 'location')
            }),
            ('Фото мероприятия', {
                'fields': ('photo', 'photo_preview')
            }),
            ("Регистрация", {
                "fields": ["enable_registration", "registration_url"],
            }),
            ("Билеты", {
                "fields": ["enable_tickets", "ticket_url"],
            }),
            ('Служебная информация', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        ]

        # Преобразуем в список, чтобы можно было модифицировать
        fieldsets = [list(fs) for fs in fieldsets]

        if obj and obj.enable_registration:
            fieldsets[3][1] = dict(fieldsets[3][1])  # копируем словарь
            fieldsets[3][1]["fields"] = list(fieldsets[3][1]["fields"])  # копируем список
            fieldsets[3][1]["fields"].append("registration_url")

        if obj and obj.enable_tickets:
            fieldsets[4][1] = dict(fieldsets[4][1])
            fieldsets[4][1]["fields"] = list(fieldsets[4][1]["fields"])
            fieldsets[4][1]["fields"].append("ticket_url")

        # Преобразуем обратно в кортежи
        fieldsets = [tuple(fs) for fs in fieldsets]

        return fieldsets

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

    def photo_preview(self, obj):
        if obj and obj.photo:
            return format_html('<img src="{}" style="max-height: 765px; max-width: 1280px"/>', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = "Превью фото"

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        class AdminFormWithRequest(form_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.request = request

        return AdminFormWithRequest
