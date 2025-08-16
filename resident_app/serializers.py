import re
from rest_framework import serializers
from .models import Category, Resident, MapMarker


class RecursiveCategorySerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children']


class ResidentSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, many=True, source='categories'
    )
    class Meta:
        model = Resident
        fields = '__all__'
        extra_kwargs = {
            'pin_code': {'required': False}
        }

    def create(self, validated_data):
        # Создаем экземпляр без pin_code, чтобы сработал метод save() модели
        if 'pin_code' not in validated_data:
            validated_data['pin_code'] = None
        return super().create(validated_data)

    def validate_phone_number(self, value):
        phone_regex = re.compile(r"^\+?\d{10,15}$")
        if value and not phone_regex.match(value):
            raise serializers.ValidationError(
                "Некорректный номер телефона: 10–15 цифр, можно с '+'. Пример: +79001234567"
            )
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

        for field in ['name', 'email', 'phone_number', 'official_website']:
            if is_duplicate(field):
                errors[field] = f"{field.capitalize()} уже используется другим резидентом."

        if errors:
            raise serializers.ValidationError(errors)

        return data


class MapMarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapMarker
        fields = ['x', 'y']


class ResidentMapSerializer(serializers.ModelSerializer):
    map_marker = MapMarkerSerializer()
    categories = CategorySerializer(many=True)

    class Meta:
        model = Resident
        fields = ['id', 'name', 'map_marker', 'categories']
