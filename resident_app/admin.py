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
    search_fields = ('name', 'description', 'full_address', 'email', 'phone_number')
    list_per_page = 20
    ordering = ('name',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description')
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
    )

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
    contact_info.allow_tags = True

    def working_time_short(self, obj):
        if len(obj.working_time) > 50:
            return f"{obj.working_time[:50]}..."
        return obj.working_time

    working_time_short.short_description = 'График работы'

    def get_readonly_fields(self, request, obj=None):
        """Делаем email и phone_number read-only при редактировании"""
        if obj:  # При редактировании существующего объекта
            return ('email', 'phone_number')
        return ()
