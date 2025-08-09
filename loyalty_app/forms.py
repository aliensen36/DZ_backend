import re

from django import forms
from django.core.exceptions import ValidationError

from .models import LoyaltyCard, PointsTransaction, Promotion, PointsSystemSettings


class LoyaltyCardForm(forms.ModelForm):
    user_first_name = forms.CharField(max_length=255, required=False, label="Имя")
    user_last_name = forms.CharField(max_length=255, required=False, label="Фамилия")

    class Meta:
        model = LoyaltyCard
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
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
    

class PointsTransactionForm(forms.ModelForm):
    class Meta:
        model = PointsTransaction
        fields = ['price', 'transaction_type', 'card_id', 'resident_id']

    class PointsTransactionForm(forms.ModelForm):
    class Meta:
        model = PointsTransaction
        fields = ['price', 'transaction_type', 'card_id', 'resident_id']

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        transaction_type = cleaned_data.get('transaction_type')
        card = cleaned_data.get('card_id')
        resident = cleaned_data.get('resident_id')

        if price is not None and price <= 0:
            raise ValidationError({'price': 'Сумма должна быть положительной.'})

        settings = PointsSystemSettings.objects.first()
        if not settings:
            raise ValidationError('Не заданы настройки программы лояльности.')

        if transaction_type == 'начисление':
            if not resident:
                raise ValidationError({'resident_id': 'Нужно выбрать резидента для расчета баллов.'})

            points = int((price / 100) * settings.points_per_100_rubles)
            if points <= 0:
                raise ValidationError({'price': 'Недостаточно суммы для начисления баллов.'})
            cleaned_data['points'] = points

        elif transaction_type == 'списание':
            if not card:
                raise ValidationError({'card_id': 'Нужно выбрать карту.'})

            max_percent = settings.points_per_1_percent / 100
            max_deductible_points = int(price * max_percent)
            current_balance = card.get_balance()

            if max_deductible_points <= 0:
                raise ValidationError({'price': 'Недостаточная сумма для списания баллов.'})
            if current_balance < max_deductible_points:
                raise ValidationError({
                    'card_id': f'Недостаточно баллов. Баланс: {current_balance}, требуется: {max_deductible_points}'
                })
            cleaned_data['points'] = -max_deductible_points

        else:
            raise ValidationError({'transaction_type': 'Недопустимый тип транзакции.'})

        return cleaned_data


class PromotionAdminForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = '__all__'

    def clean_promotional_code(self):
        code = self.cleaned_data.get('promotional_code')

        if not re.match(r'^[A-Z0-9]+$', code) or not re.search(r'\d', code):
            raise ValidationError(
                "Промокод должен содержать только заглавные латинские буквы и хотя бы одну цифру."
            )

        # Проверка уникальности
        qs = Promotion.objects.filter(promotional_code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Такой промокод уже существует.")

        return code
    

class PointsSystemSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = PointsSystemSettings
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        points_per_100_rubles = cleaned_data.get('points_per_100_rubles')
        points_per_1_percent = cleaned_data.get('points_per_1_percent')

        if points_per_100_rubles is not None and points_per_100_rubles <= 0:
            raise ValidationError("Количество бонусов за 100 рублей должно быть положительным числом.")

        if points_per_1_percent is not None and points_per_1_percent <= 0:
            raise ValidationError("Количество бонусов за 1% скидки должно быть положительным числом.")

        return cleaned_data