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

        enable_registration = cleaned_data.get('enable_registration')
        registration_url = cleaned_data.get('registration_url')
        enable_tickets = cleaned_data.get('enable_tickets')
        ticket_url = cleaned_data.get('ticket_url')

        errors = {}

        if enable_registration and not registration_url:
            errors['registration_url'] = 'Укажите ссылку на регистрацию, если она включена.'

        if enable_tickets and not ticket_url:
            errors['ticket_url'] = 'Укажите ссылку на покупку билетов, если она включена.'

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data


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
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = "Превью фото"

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        class AdminFormWithRequest(form_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.request = request

        return AdminFormWithRequest
