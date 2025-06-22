from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import LoyaltyCard, PointsTransaction

from django.contrib.auth import get_user_model
User = get_user_model()


class LoyaltyCardForm(forms.ModelForm):
    # Добавляем поля из связанной модели User
    user_first_name = forms.CharField(max_length=255, required=False, label="Имя")
    user_last_name = forms.CharField(max_length=255, required=False, label="Фамилия")

    class Meta:
        model = LoyaltyCard
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['user_first_name'].initial = self.instance.user.user_first_name
            self.fields['user_last_name'].initial = self.instance.user.user_last_name

    def save(self, commit=True):
        loyalty_card = super().save(commit=False)
        if loyalty_card.user:
            loyalty_card.user.user_first_name = self.cleaned_data['user_first_name']
            loyalty_card.user.user_last_name = self.cleaned_data['user_last_name']
            if commit:
                loyalty_card.user.save()
                loyalty_card.save()
        return loyalty_card

@admin.register(LoyaltyCard)
class LoyaltyCardAdmin(admin.ModelAdmin):
    form = LoyaltyCardForm  # Используем кастомную форму

    list_display = ('card_number', 'user_info', 'created_at')
    list_display_links = ('card_number', 'user_info', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('card_number', 'user__first_name', 'user__last_name',
                    'user__user_first_name', 'user__user_last_name')
    readonly_fields = ('card_number', 'created_at', 'card_image_preview')

    fieldsets = (
        ('Превью карты', {
            'fields': ('card_image_preview',),
            'classes': ('wide',)
        }),
        (None, {
            'fields': ('user', 'user_first_name', 'user_last_name', 'card_number', 'created_at')
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
                '<img src="{}" style="height: auto; width: 300px; border: 1px solid #ddd; padding: 5px;"/>'
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



class PointsTransactionForm(forms.ModelForm):
    class Meta:
        model = PointsTransaction
        fields = ['price', 'transaction_type', 'card_id', 'resident_id']

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        transaction_type = cleaned_data.get('transaction_type')
        card_id = cleaned_data.get('card_id')

        if price is not None and price <= 0:
            raise ValidationError({'price': 'Сумма должна быть положительной.'})

        if transaction_type == 'начисление':
            # Логика начисления: 1 балл за каждые 100 рублей
            points = int(price) // 100
            if points <= 0:
                raise ValidationError({'price': 'Недостаточно суммы для начисления баллов.'})
            cleaned_data['points'] = points
        elif transaction_type == 'списание':
            # Логика списания: до 10% от суммы
            max_deductible_points = int(price * 0.10)
            if max_deductible_points <= 0:
                raise ValidationError({'price': 'Недостаточная сумма для списания баллов.'})
            if card_id:
                current_balance = card_id.get_balance()
                if current_balance < max_deductible_points:
                    raise ValidationError({
                        'card_id': f'Недостаточно баллов. Баланс: {current_balance}, требуется: {max_deductible_points}'
                    })
                cleaned_data['points'] = -max_deductible_points
        else:
            raise ValidationError({'transaction_type': 'Недопустимый тип транзакции.'})

        return cleaned_data


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    form = PointsTransactionForm

    # Поля, отображаемые в списке транзакций
    list_display = ('transaction_type', 'points', 'price', 'created_at', 'card_number', 'resident_name')

    # Фильтры в боковой панели
    list_filter = ('transaction_type', 'created_at', 'card_id', 'resident_id')

    # Поля для поиска
    search_fields = ('card_id__card_number', 'resident_id__name', 'transaction_type')

    # Поля, доступные для редактирования в форме
    fields = ('price', 'transaction_type', 'card_id', 'resident_id', 'created_at')

    # Поля, которые нельзя редактировать
    readonly_fields = ('created_at',)

    # Сортировка по дате создания
    ordering = ('-created_at',)

    # Автодополнение для связанных объектов
    autocomplete_fields = ['card_id', 'resident_id']

    # Оптимизация запросов
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card_id', 'resident_id')

    # Отображение номера карты
    def card_number(self, obj):
        return obj.card_id.card_number if obj.card_id else '-'

    card_number.short_description = 'Номер карты'

    # Отображение имени резидента
    def resident_name(self, obj):
        return obj.resident_id.name if obj.resident_id else '-'

    resident_name.short_description = 'Резидент'

    def save_model(self, request, obj, form, change):
        # Установка points на основе логики из формы
        obj.points = form.cleaned_data['points']
        super().save_model(request, obj, form, change)
