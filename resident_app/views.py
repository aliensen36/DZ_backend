from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Category, Resident
from mailing_app.models import Subscription
from .serializers import ResidentSerializer, CategorySerializer
from user_app.auth.permissions import IsAdmin, IsBotAuthenticated


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsBotAuthenticated | (IsAuthenticated & IsAdmin)]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        # Автоматическое создание подписки, при создании категории
        Subscription.objects.create(
            name=category.name,
            description=category.description
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ResidentViewSet(viewsets.ModelViewSet):
    queryset = Resident.objects.all()
    serializer_class = ResidentSerializer
    permission_classes = [IsBotAuthenticated | (IsAuthenticated & IsAdmin)]

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
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
    

class PinCodeVerifyView(APIView):
    permission_classes = [IsBotAuthenticated | (IsAuthenticated & IsAdmin)]
    def post(self, request):
        pin_code = request.data.get('pin_code')
        try:
            resident = Resident.objects.get(pin_code=pin_code)
            serializer = ResidentSerializer(resident)
            return Response({
                'status': 'success',
                'resident': serializer.data
            }, status=status.HTTP_200_OK)
        except Resident.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Неверный пин-код или пользователь не является администратором'
            }, status=status.HTTP_401_UNAUTHORIZED)
