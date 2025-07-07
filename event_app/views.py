from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Event
from .serializers import EventSerializer
from user_app.auth.permissions import IsAdmin, IsBotAuthenticated


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsBotAuthenticated | (IsAuthenticated & IsAdmin)]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        today_only = self.request.query_params.get('today')

        if today_only == 'true':
            today = timezone.localdate()
            queryset = queryset.filter(
                Q(start_date__date=today) | Q(end_date__date=today)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    