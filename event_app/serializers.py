import datetime
from rest_framework import serializers

from .models import Event
from django.conf import settings



class EventSerializer(serializers.ModelSerializer):
    has_registration = serializers.SerializerMethodField()
    has_ticket = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'info', 'start_date', 'end_date', 'location', 'photo', 'ticket_url', 'registration_url', 'created_at']
        extra_kwargs = {
            'photo': {'required': True}
        }

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')

        if start and end and end < start:
            raise serializers.ValidationError("Дата окончания мероприятия не может быть раньше даты начала.")

        if start and start < datetime.datetime.now(datetime.timezone.utc):
            raise serializers.ValidationError("Дата начала мероприятия не может быть в прошлом.")

        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.photo and request:
            representation['photo'] = request.build_absolute_uri(instance.photo.url)
        else:
            representation['photo'] = None
        return representation

    def get_has_registration(self, obj):
        # Возвращает True, если есть ссылка на регистрацию
        return bool(obj.enable_registration)

    def get_has_ticket(self, obj):
        # Возвращает True, если есть ссылка на покупку билета
        return bool(obj.enable_tickets)