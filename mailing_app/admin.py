from django.contrib import admin
from django.utils.html import format_html

from .models import Mailing, Subscription


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_text', 'created_at')
    list_display_links = ('id', 'truncated_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'button_url')
    readonly_fields = ('created_at',)
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'users_count')
    search_fields = ('name',)
    filter_horizontal = ('users',)
    list_filter = ('name',)

    def users_count(self, obj):
       return obj.users.count()
    users_count.short_description = 'Количество пользователей'

    class Meta:
        model = Subscription
