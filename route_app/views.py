from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from user_app.auth.permissions import IsBotAuthenticated
from .navigation import find_shortest_path
from rest_framework import viewsets, status
from .models import (
    Building, Floor, LocationType, Location,
    LocationCorner, Connection, Route, Tour
)
from .serializers import (
    BuildingSerializer, FloorSerializer, LocationTypeSerializer,
    LocationSerializer, LocationCornerSerializer, ConnectionSerializer,
    RouteSerializer, TourSerializer
)


# =================================================================================================
# Строения
# =================================================================================================

@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты/Строения'],
        summary="Получить список зданий",
        description="Возвращает список всех зданий.",
        responses={200: BuildingSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты/Строения'],
        summary="Получить здание по ID",
        description="Возвращает информацию о конкретном здании.",
        responses={200: BuildingSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты/Строения'],
        summary="Создать здание",
        description="Добавляет новое здание.",
        responses={201: BuildingSerializer},
        examples=[OpenApiExample(
            'Пример',
            value={"name": "Главный корпус", "description": "Описание здания"}
        )]
    ),
    update=extend_schema(
        tags=['Маршруты/Строения'],
        summary="Обновить здание (PUT)",
        description="Полностью обновляет данные здания.",
        responses={200: BuildingSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты/Строения'],
        summary="Частично обновить здание (PATCH)",
        description="Изменяет часть данных здания.",
        responses={200: BuildingSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты/Строения'],
        summary="Удалить здание",
        description="Удаляет здание по ID.",
        responses={204: OpenApiResponse(description="Здание удалено")},
    ),
)
class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


# =================================================================================================
# Этажи
# =================================================================================================


@extend_schema(tags=['Этажи'])
class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer


# =================================================================================================
# Типы локаций
# =================================================================================================


@extend_schema(tags=['Типы локаций'])
class LocationTypeViewSet(viewsets.ModelViewSet):
    queryset = LocationType.objects.all()
    serializer_class = LocationTypeSerializer


@extend_schema(tags=['Локации'])
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


@extend_schema(tags=['Углы локации'])
class LocationCornerViewSet(viewsets.ModelViewSet):
    queryset = LocationCorner.objects.all()
    serializer_class = LocationCornerSerializer


@extend_schema(tags=['Связи (навигация)'])
class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer


@extend_schema(tags=['Маршруты'])
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    @extend_schema(
        tags=['Маршруты'],
        responses={200: LocationSerializer(many=True)},
        description="Возвращает путь от начальной до конечной точки маршрута"
    )

    @action(detail=True, methods=['get'])
    def navigate(self, request, pk=None):
        route = self.get_object()
        path_ids = find_shortest_path(route.start_location, route.end_location)

        if path_ids is None:
            return Response({"detail": "Путь не найден"}, status=status.HTTP_404_NOT_FOUND)

        locations = Location.objects.filter(id__in=path_ids)
        locations_by_id = {loc.id: loc for loc in locations}
        ordered = [locations_by_id[loc_id] for loc_id in path_ids]
        serializer = LocationSerializer(ordered, many=True)

        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Туры'],
        summary="Получить список туров",
        description="Возвращает список всех туров, отсортированных по дате создания (сначала новые)."
    ),
    retrieve=extend_schema(
        tags=['Туры'],
        summary="Получить тур по ID",
        description="Возвращает детальную информацию о туре по его ID."
    ),
    create=extend_schema(
        tags=['Туры'],
        summary="Создать тур",
        description="Создает новый тур. Требуется авторизация.",
        examples=[
            OpenApiExample(
                'Пример создания',
                value={
                    "name": "Тур по Петербургу",
                    "image": None,
                    "description": "Краткое описание",
                    "full_description": "Полное описание",
                    "residents": 1
                }
            )
        ]
    ),
    update=extend_schema(
        summary="Обновить тур (PUT)",
        description="Полностью обновляет данные тура. Требуется авторизация."
    ),
    partial_update=extend_schema(
        summary="Частично обновить тур (PATCH)",
        description="Изменяет часть данных тура. Требуется авторизация."
    ),
    destroy=extend_schema(
        summary="Удалить тур",
        description="Удаляет тур по ID. Требуется авторизация."
    ),
)
class TourViewSet(ModelViewSet):
    queryset = Tour.objects.all().order_by('-created_at')
    serializer_class = TourSerializer
    permission_classes = [IsBotAuthenticated | IsAuthenticated]
