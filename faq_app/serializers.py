from rest_framework import serializers

from .models import QuestionType, FAQ


class QuestionTypeSerializer(serializers.Serializer):
    class Meta:
        model = QuestionType
        fields = '__all__'


class FAQSerializer(serializers.Serializer):
    class Meta:
        model = FAQ
        fields = '__all__'