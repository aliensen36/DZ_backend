from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import *
from django import forms
from django.contrib import admin
from django_celery_beat.models import SolarSchedule, ClockedSchedule

# Убираем ненужные модели из админки
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        # Проверка для регистрации
        if cleaned_data.get("enable_registration") and not cleaned_data.get("registration_url"):
            raise forms.ValidationError(
                "Укажите ссылку на регистрацию, если она включена."
            )

        # Проверка для билетов
        if cleaned_data.get("enable_tickets") and not cleaned_data.get("ticket_url"):
            raise forms.ValidationError(
                "Укажите ссылку на покупку билетов, если она включена."
            )

        return cleaned_data


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'date_range',
        'location',
        'is_active',
    )
    list_display_links = ('title',)
    list_filter = ('start_date', 'end_date', 'location')
    search_fields = ('title', 'description', 'info', 'location')
    list_per_page = 20
    ordering = ('start_date',)

    def get_fieldsets(self, request, obj=None):
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
            ("Регистрация", {
                "fields": ["enable_registration"],
                "classes": ("collapse",),
            }),
            ("Билеты", {
                "fields": ["enable_tickets"],
                "classes": ("collapse",),
            }),
        )


        # Добавляем поля ссылок, только если флажки включены
        if obj and obj.enable_registration:
            fieldsets[4][1]["fields"].append("registration_url")

        if obj and obj.enable_tickets:
            fieldsets[5][1]["fields"].append("ticket_url")

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
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = "Превью фото"




