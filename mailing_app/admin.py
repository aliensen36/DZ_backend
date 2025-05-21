from django.contrib import admin
from django.utils.html import format_html

from .models import Mailing

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_text', 'type', 'created_at', 'image_preview')
    list_filter = ('type', 'created_at')
    search_fields = ('text', 'button_url')
    readonly_fields = ('created_at',)
    # Поля, которые можно редактировать прямо из списка
    list_editable = ('type',)
    # Пагинация
    list_per_page = 20
    # Отображение полей при редактировании
    fieldsets = (
        (None, {
            'fields': ('text', 'type')
        }),
        ('Дополнительные настройки', {
            'fields': ('image', 'button_url'),
            'classes': ('collapse',)  # Сворачиваемый блок
        }),
    )

    def truncated_text(self, obj):
        """Укорачиваем текст для отображения в списке"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = 'Текст сообщения'

    def image_preview(self, obj):
        """Превью изображения, если URL указан"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image)
        return "—"
    image_preview.short_description = 'Превью'
