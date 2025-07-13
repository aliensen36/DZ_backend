from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    list_filter = ('floor', 'office')
    search_fields = ('name', 'description', 'full_address', 'email', 'phone_number', 'pin_code')
    list_per_page = 20
    ordering = ('name',)

    def get_fieldsets(self, request, obj=None):
        """Динамически добавляет photo_preview только при редактировании"""
        fieldsets = [
            ('Основная информация', {
                'fields': ('name', 'categories', 'description', 'info')
            }),
            ('Контактные данные', {
                'fields': ('email', 'phone_number', 'official_website')
            }),
            ('Расположение', {
                'fields': ('full_address', 'floor', 'office'),
                'description': 'Укажите точное расположение на территории завода'
            }),
            ('График работы', {
                'fields': ('working_time',),
                'classes': ('wide',)
            }),
        ]

        # Добавляем фото и пин-код
        photo_fields = ['photo', 'pin_code']
        if obj:  # только если объект уже существует
            photo_fields.insert(1, 'photo_preview')

        fieldsets.append((
            'Фото и прочее',
            {'fields': tuple(photo_fields)}
        ))

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        """email, phone_number и pin_code нельзя менять при редактировании"""
        ro = ['pin_code']
        if obj:
            ro += ['email', 'phone_number', 'photo_preview']
        return ro

    def floor_office(self, obj):
        return f"{obj.floor} этаж, офис {obj.office}"
    floor_office.short_description = 'Расположение'
    floor_office.admin_order_field = 'floor'

    def contact_info(self, obj):
        contacts = []
        if obj.email:
            contacts.append(f"✉ {obj.email}")
        if obj.phone_number:
            contacts.append(f"📞 {obj.phone_number}")
        return format_html("<br>".join(contacts))
    contact_info.short_description = 'Контакты'

    def pin_code_display(self, obj):
        return obj.pin_code or '—'
    pin_code_display.short_description = 'Пин-код'

    def photo_preview(self, obj):
        if obj and obj.photo:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = "Превью фото"
