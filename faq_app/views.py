from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import QuestionType, FAQ
from .serializers import QuestionTypeSerializer, FAQSerializer
from user_app.auth.permissions import IsAdmin


class QuestionTypeAdminViewSet(viewsets.ModelViewSet):
    queryset = QuestionType.objects.all()
    serializer_class = QuestionTypeSerializer
    permission_classes = [(IsAuthenticated & IsAdmin)]

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
    

class QuestionTypeUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuestionType.objects.all()
    serializer_class = QuestionTypeSerializer
    permission_classes = [AllowAny]  # Потом заменить на IsAuthenticated
    

class FAQAdminViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [(IsAuthenticated & IsAdmin)]

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
    

class FAQUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]  # Потом заменить на IsAuthenticated

    def get_queryset(self):
        queryset = super().get_queryset()
        question_type = self.request.query_params.get('type')
        if question_type:
            queryset = queryset.filter(type_id=question_type)
        return queryset