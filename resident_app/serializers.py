import re
from rest_framework import serializers

from .models import Resident

class ResidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resident
        fields = '__all__'

    def validate(self, data):
        instance = self.instance  # None при создании, объект при обновлении

        def is_duplicate(field):
            value = data.get(field)
            if not value:
                return False
            qs = Resident.objects.filter(**{field: value})
            if instance:
                qs = qs.exclude(pk=instance.pk)
            return qs.exists()

        # Валидация для российского номера телефона
        def validate_phone_number(phone_number):
            # Регулярное выражение для проверки российского номера
            phone_regex = re.compile(r"^\+?\d{10,15}$")
            if phone_number and not phone_regex.match(phone_number):
                raise serializers.ValidationError("Некорректный номер телефона, 10–15 цифр, можно с '+'. Пример: +79001234567")
            return phone_number

        errors = {}

        phone_number = data.get('phone_number')
        if phone_number:
            try:
                validate_phone_number(phone_number)
            except serializers.ValidationError as e:
                errors['phone_number'] = str(e)

        # Проверка на дубликаты
        for field in ['name', 'email', 'phone_number', 'address']:
            if is_duplicate(field):
                errors[field] = f"{field.capitalize()} уже используется другим резидентом."

        if errors:
            raise serializers.ValidationError(errors)

        return data