from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Event
from .serializers import EventSerializer
from user_app.auth.permissions import IsAdmin, IsBotAuthenticated


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # permission_classes = [AllowAny]  # Только в разработке
    permission_classes = [IsBotAuthenticated | IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=['get'], url_path='today')
    def today_events(self, request):
        """
        Возвращает мероприятия, которые проходят сегодня.
        """
        today = timezone.localdate()
        events = self.queryset.filter(
            Q(start_date__date=today) | Q(end_date__date=today)
        ).order_by('-created_at')

        if not events.exists():
            return Response({'detail': 'На сегодня мероприятий нет.'}, status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='exclude_today')
    def exclude_today_events(self, request):
        """
        Возвращает мероприятия, которые НЕ проходят сегодня.
        """
        today = timezone.localdate()
        events = self.queryset.exclude(
            Q(start_date__date=today) | Q(end_date__date=today)
        ).order_by('-created_at')

        if not events.exists():
            return Response({'detail': 'Все мероприятия проходят сегодня.'}, status=status.HTTP_204_NO_CONTENT)
    
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if 'photo' not in request.FILES:
            return Response({"photo": ["Фото мероприятия обязательно."]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.photo = request.FILES['photo']
        instance.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if 'photo' in request.FILES:
            instance.photo = request.FILES['photo']
            instance.save()

        return Response(serializer.data)