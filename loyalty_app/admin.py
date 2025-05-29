from django.contrib import admin
from django.utils.html import format_html
from .models import LoyaltyCard


@admin.register(LoyaltyCard)
class LoyaltyCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'user_info', 'created_at')  # Убрали card_image_preview
    list_filter = ('created_at',)
    search_fields = ('card_number', 'user__first_name', 'user__last_name',
                     'user__user_first_name', 'user__user_last_name')
    readonly_fields = ('card_number', 'created_at', 'card_image_preview')

    # Новый порядок полей для страницы редактирования
    fieldsets = (
        ('Превью карты', {
            'fields': ('card_image_preview',),
            'classes': ('wide',)
        }),
        (None, {
            'fields': ('user', 'card_number', 'created_at')
        }),
        ('Изображение карты', {
            'fields': ('card_image',),
            'classes': ('collapse',)
        }),
    )

    actions = ['regenerate_card_image']

    def user_info(self, obj):
        """Отображение информации о пользователе"""
        user = obj.user
        name = user.user_first_name or user.first_name
        surname = user.user_last_name or user.last_name
        return f"{name} {surname} (ID: {user.tg_id})"

    user_info.short_description = 'Пользователь'

    def card_image_preview(self, obj):
        """Миниатюра изображения карты (только для страницы редактирования)"""
        if obj.card_image:
            return format_html(
                '<div style="margin-bottom: 20px;">'
                '<h3>Превью карты лояльности</h3>'
                '<img src="{}" style="max-height: 300px; border: 1px solid #ddd; padding: 5px;"/>'
                '</div>',
                obj.card_image.url
            )
        return format_html('<div style="color: #999;">Изображение карты отсутствует</div>')

    card_image_preview.short_description = ''
    card_image_preview.allow_tags = True

    def regenerate_card_image(self, request, queryset):
        """Действие для перегенерации изображений карт"""
        for card in queryset:
            card.generate_card_image()
            card.save()
        self.message_user(
            request,
            f"Изображения {queryset.count()} карт успешно перегенерированы"
        )

    regenerate_card_image.short_description = 'Перегенерировать изображения карт'

    def get_readonly_fields(self, request, obj=None):
        """Делаем поле user редактируемым только при создании"""
        if obj:  # Редактирование существующего объекта
            return self.readonly_fields + ('user',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """Автоматическая генерация номера и изображения при создании"""
        if not change:  # Только при создании нового объекта
            if not obj.card_number:
                obj.card_number = obj.generate_card_number()
            obj.generate_card_image()
        super().save_model(request, obj, form, change)