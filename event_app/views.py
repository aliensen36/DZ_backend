from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Event
from .serializers import EventSerializer
from user_app.auth.permissions import IsAdmin, IsBotAuthenticated


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsBotAuthenticated | (IsAuthenticated & IsAdmin)]
    parser_classes = [MultiPartParser, FormParser]

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