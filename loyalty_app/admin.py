from django import forms
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from .models import LoyaltyCard, PointsTransaction
from django.contrib.auth import get_user_model

from .views import LoyaltyCardViewSet

User = get_user_model()


@staff_member_required
def admin_card_image_view(request, card_id):
    try:
        card = LoyaltyCard.objects.get(pk=card_id)
        viewset = LoyaltyCardViewSet()
        image = viewset.generate_card_image(card.user, card.card_number)  # Вызываем метод
        return HttpResponse(image.getvalue(), content_type='image/png')
    except LoyaltyCard.DoesNotExist:
        return HttpResponse("Карта не найдена", status=404)


class LoyaltyCardForm(forms.ModelForm):
    user_first_name = forms.CharField(max_length=255, required=False, label="Имя")
    user_last_name = forms.CharField(max_length=255, required=False, label="Фамилия")

    class Meta:
        model = LoyaltyCard
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['user_first_name'].initial = getattr(self.instance.user, 'user_first_name', '')
            self.fields['user_last_name'].initial = getattr(self.instance.user, 'user_last_name', '')

    def save(self, commit=True):
        loyalty_card = super().save(commit=False)
        if loyalty_card.user:
            setattr(loyalty_card.user, 'user_first_name', self.cleaned_data.get('user_first_name'))
            setattr(loyalty_card.user, 'user_last_name', self.cleaned_data.get('user_last_name'))
            if commit:
                loyalty_card.user.save()
                loyalty_card.save()
        return loyalty_card


@admin.register(LoyaltyCard)
class LoyaltyCardAdmin(admin.ModelAdmin):
    form = LoyaltyCardForm

    list_display = ('card_number', 'user_info', 'created_at')
    list_display_links = ('card_number', 'user_info', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'card_number',
        'user__first_name',
        'user__last_name',
        'user__user_first_name',
        'user__user_last_name'
    )
    readonly_fields = ('card_number', 'created_at', 'card_image_preview')  # Убрали card_image

    fieldsets = (
        ('Превью карты', {
            'fields': ('card_image_preview',),
            'classes': ('wide',)
        }),
        (None, {
            'fields': ('user', 'user_first_name', 'user_last_name', 'card_number', 'created_at')
        }),
    )

    actions = ['regenerate_card_image']

    def user_info(self, obj):
        user = obj.user
        name = user.user_first_name or user.first_name
        surname = user.user_last_name or user.last_name
        return f"{name} {surname} (ID: {user.tg_id})"

    user_info.short_description = 'Пользователь'

    def card_image_preview(self, obj):
        if not obj.pk:
            return "Сначала сохраните карту, чтобы увидеть превью."
        url = reverse('admin:admin_card_image', args=[obj.pk])
        return format_html(
            '<div style="margin-bottom: 20px;">'
            '<h3>Превью карты лояльности</h3>'
            '<img src="{}" style="max-width: 50%; border: 1px solid #ccc; padding: 5px;" />'
            '</div>', url
        )

    card_image_preview.short_description = 'Превью карты'

    def regenerate_card_image(self, request, queryset):
        viewset = LoyaltyCardViewSet()
        for card in queryset:
            image = viewset.generate_card_image(card.user, card.card_number)
        self.message_user(
            request,
            f"Изображения {queryset.count()} карт успешно перегенерированы"
        )

    regenerate_card_image.short_description = 'Перегенерировать изображения карт'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            if not obj.card_number:
                obj.card_number = obj.generate_card_number()
            obj.generate_card_image()
        super().save_model(request, obj, form, change)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('card-image/<int:card_id>/', self.admin_site.admin_view(admin_card_image_view),
                 name='admin_card_image'),
        ]
        return custom_urls + urls


# --- PointsTransaction Admin ---

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
            points = int(price) // 100
            if points <= 0:
                raise ValidationError({'price': 'Недостаточно суммы для начисления баллов.'})
            cleaned_data['points'] = points
        elif transaction_type == 'списание':
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

    list_display = ('transaction_type', 'points', 'price', 'created_at', 'card_number', 'resident_name')
    list_filter = ('transaction_type', 'created_at', 'card_id', 'resident_id')
    search_fields = ('card_id__card_number', 'resident_id__name', 'transaction_type')
    fields = ('price', 'transaction_type', 'card_id', 'resident_id', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    autocomplete_fields = ['card_id', 'resident_id']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card_id', 'resident_id')

    def card_number(self, obj):
        return obj.card_id.card_number if obj.card_id else '-'
    card_number.short_description = 'Номер карты'

    def resident_name(self, obj):
        return obj.resident_id.name if obj.resident_id else '-'
    resident_name.short_description = 'Резидент'

    def save_model(self, request, obj, form, change):
        obj.points = form.cleaned_data['points']
        super().save_model(request, obj, form, change)
