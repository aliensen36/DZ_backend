from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Category, Resident
from mailing_app.models import Subscription
from .serializers import ResidentSerializer, CategorySerializer, ResidentMapSerializer
from user_app.auth.permissions import IsAdmin, IsBotAuthenticated
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)
from django.http import Http404
from django.db import transaction

import logging
logger = logging.getLogger(__name__)



def get_descendants_ids(category):
    descendants = set()
    def collect_children(cat):
        for child in cat.children.all():
            descendants.add(child.id)
            collect_children(child)
    collect_children(category)
    return list(descendants | {category.id})

@extend_schema_view(
    list=extend_schema(
        summary="Список категорий",
        description=(
            "Возвращает список категорий.\n\n"
            "- По умолчанию возвращаются только **основные категории** (у которых `parent = null`).\n"
            "- Если передать `?tree=true`, то возвращается **вся иерархия категорий**, включая подкатегории."
        ),
        parameters=[
            OpenApiParameter(
                name='tree',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Если `true` — вернуть все категории с вложенными подкатегориями"
            )
        ]
    ),
    retrieve=extend_schema(summary="Получить категорию по ID"),
    create=extend_schema(summary="Создать категорию"),
    update=extend_schema(summary="Обновить категорию"),
    partial_update=extend_schema(summary="Частично обновить категорию"),
    destroy=extend_schema(summary="Удалить категорию"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsBotAuthenticated | IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        show_all = self.request.query_params.get('tree') == 'true'
        if show_all:
            return Category.objects.all().prefetch_related('children')
        return Category.objects.filter(parent__isnull=True).prefetch_related('children')

    def get_object(self):
        # Ищем категорию без фильтрации по parent
        queryset = Category.objects.all()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        try:
            return queryset.get(pk=self.kwargs[lookup_url_kwarg])
        except Category.DoesNotExist:
            raise Http404("Категория не найдена")

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            descendants = get_descendants_ids(instance)

            # Удаляем в транзакции
            with transaction.atomic():
                Category.objects.filter(id__in=descendants).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                {"error": "Категория не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="Список резидентов",
        description=(
            "Возвращает список резидентов с возможностью фильтрации по категории.\n\n"
            "- Если указан `category_id` и `main=true`, то выводятся все резиденты **основной категории** и всех её **подкатегорий**.\n"
            "- Если `main` не указан или `false`, то фильтрация происходит **только по указанной категории**."
        ),
        parameters=[
            OpenApiParameter(
                name='category_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ID категории, по которой фильтруются резиденты"
            ),
            OpenApiParameter(
                name='main',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Если `true` и категория — основная, то включает резидентов подкатегорий"
            )
        ]
    ),
    retrieve=extend_schema(summary="Получить резидента по ID"),
    create=extend_schema(summary="Создать резидента"),
    update=extend_schema(summary="Обновить резидента"),
    partial_update=extend_schema(summary="Частично обновить резидента"),
    destroy=extend_schema(summary="Удалить резидента"),
)
class ResidentViewSet(viewsets.ModelViewSet):
    queryset = Resident.objects.all()
    serializer_class = ResidentSerializer
    permission_classes = [IsBotAuthenticated | IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        is_main = self.request.query_params.get('main', 'false') == 'true'

        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return queryset.none()
            
            if is_main and category.parent is None:
                descendant_ids = get_descendants_ids(category)
                queryset = queryset.filter(categories__id__in=descendant_ids)
            else:
                queryset = queryset.filter(categories__id=category_id)

        return queryset.distinct()

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
    permission_classes = [IsBotAuthenticated | IsAuthenticated]

    @extend_schema(
        summary="Проверка пин-кода резидента",
        description="Принимает pin_code и возвращает информацию о резиденте, если код верный.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'pin_code': {'type': 'string'}
                },
                'required': ['pin_code']
            }
        },
        responses={
            200: ResidentSerializer,
            401: OpenApiTypes.OBJECT,
        },
    )
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


class MapResidentListView(APIView):
    permission_classes = [IsBotAuthenticated | IsAuthenticated]

    @extend_schema(
        summary="Список резидентов с координатами (для карты)",
        description="Возвращает резидентов и их метки на карте. Фильтрация по категориям.",
        parameters=[
            OpenApiParameter(
                name='category_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Список ID категорий через запятую, например: `1,2,3`'
            )
        ],
        responses={200: ResidentMapSerializer(many=True)},
    )
    def get(self, request):
        category_ids = request.query_params.get('category_id')

        queryset = Resident.objects.prefetch_related('categories', 'map_marker')

        if category_ids:
            ids = [int(i) for i in category_ids.split(',') if i.isdigit()]
            queryset = queryset.filter(categories__in=ids).distinct()

        serializer = ResidentMapSerializer(queryset, many=True)
        return Response(serializer.data)
