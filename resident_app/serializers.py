import re
from rest_framework import serializers

from .models import Resident

class ResidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resident
        fields = '__all__'

    def validate_phone_number(self, value):
        phone_regex = re.compile(r"^\+?\d{10,15}$")
        if value and not phone_regex.match(value):
            raise serializers.ValidationError(
                "Некорректный номер телефона: 10–15 цифр, можно с '+'. Пример: +79001234567"
            )
        return value

    def validate_floor(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Этаж должен быть от 1 до 5.")
        return value
    
    def validate_office(self, value):
        if value < 1 or value > 66:
            raise serializers.ValidationError("Офис должен быть от 1 до 66.")
        return value

    def validate(self, data):
        instance = self.instance
        errors = {}

        def is_duplicate(field):
            value = data.get(field)
            if not value:
                return False
            qs = Resident.objects.filter(**{field: value})
            if instance:
                qs = qs.exclude(pk=instance.pk)
            return qs.exists()

        for field in ['name', 'email', 'phone_number', 'full_address', 'official_website', 'office']:
            if is_duplicate(field):
                errors[field] = f"{field.capitalize()} уже используется другим резидентом."

        if errors:
            raise serializers.ValidationError(errors)

        return data