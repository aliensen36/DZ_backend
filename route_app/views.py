from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
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
        tags=['Маршруты'],
        summary="Список строений",
        description="Возвращает список всех строений.",
        responses={200: BuildingSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты'],
        summary="Получить строение по ID",
        description="Возвращает информацию о конкретном строении.",
        responses={200: BuildingSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты'],
        summary="Создать строение",
        description="Добавляет новое строение.",
        responses={201: BuildingSerializer},
        examples=[OpenApiExample(
            'Пример',
            value={"name": "2", "description": "Описание строения"}
        )]
    ),
    update=extend_schema(
        tags=['Маршруты'],
        summary="Обновить данные строения",
        description="Полностью обновляет данные строения.",
        responses={200: BuildingSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты'],
        summary="Частично обновить данные строения",
        description="Изменяет часть данных строения.",
        responses={200: BuildingSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты'],
        summary="Удалить строение",
        description="Удаляет строение по ID.",
        responses={204: OpenApiResponse(description="Здание удалено")},
    ),
)
class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


# =================================================================================================
# Этажи
# =================================================================================================


@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты'],
        summary="Список этажей",
        description="Возвращает список всех этажей.",
        responses={200: FloorSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты'],
        summary="Получить этаж по ID",
        description="Возвращает информацию об этаже.",
        responses={200: FloorSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты'],
        summary="Создать этаж",
        description="Добавляет новый этаж.",
        responses={201: FloorSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты'],
        summary="Обновить этаж",
        description="Полностью обновляет данные этажа.",
        responses={200: FloorSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты'],
        summary="Частично обновить этаж",
        description="Изменяет часть данных этажа.",
        responses={200: FloorSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты'],
        summary="Удалить этаж",
        description="Удаляет этаж по ID.",
        responses={204: OpenApiResponse(description="Этаж удалён")},
    ),
)
class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer


# =================================================================================================
# Типы локаций
# =================================================================================================


@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты'],
        summary="Список типов локаций",
        description="Возвращает список всех типов локаций.",
        responses={200: LocationTypeSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты'],
        summary="Получить тип локации по ID",
        description="Возвращает информацию о типе локации.",
        responses={200: LocationTypeSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты'],
        summary="Создать тип локации",
        description="Добавляет новый тип локации.",
        responses={201: LocationTypeSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты'],
        summary="Обновить тип локации",
        description="Полностью обновляет данные типа локации.",
        responses={200: LocationTypeSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты'],
        summary="Частично обновить тип локации",
        description="Изменяет часть данных типа локации.",
        responses={200: LocationTypeSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты'],
        summary="Удалить тип локации",
        description="Удаляет тип локации по ID.",
        responses={204: OpenApiResponse(description="Тип удалён")},
    ),
)
class LocationTypeViewSet(viewsets.ModelViewSet):
    queryset = LocationType.objects.all()
    serializer_class = LocationTypeSerializer


# =================================================================================================
# Локации
# =================================================================================================


@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты'],
        summary="Список локаций",
        description="Возвращает список всех локаций.",
        responses={200: LocationSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты'],
        summary="Получить локацию по ID",
        description="Возвращает информацию о конкретной локации.",
        responses={200: LocationSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты'],
        summary="Создать локацию",
        description="Добавляет новую локацию.",
        responses={201: LocationSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты'],
        summary="Обновить локацию",
        description="Полностью обновляет данные локации.",
        responses={200: LocationSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты'],
        summary="Частично обновить локацию",
        description="Изменяет часть данных локации.",
        responses={200: LocationSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты'],
        summary="Удалить локацию",
        description="Удаляет локацию по ID.",
        responses={204: OpenApiResponse(description="Локация удалена")},
    ),
)
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


# =================================================================================================
# Углы локации
# =================================================================================================


@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты'],
        summary="Список углов",
        description="Возвращает список всех углов локаций.",
        responses={200: LocationCornerSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты'],
        summary="Получить угол по ID",
        description="Возвращает данные угла локации.",
        responses={200: LocationCornerSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты'],
        summary="Создать угол",
        description="Добавляет новый угол для локации.",
        responses={201: LocationCornerSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты'],
        summary="Обновить угол",
        description="Полностью обновляет данные угла.",
        responses={200: LocationCornerSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты'],
        summary="Частично обновить угол",
        description="Изменяет часть данных угла.",
        responses={200: LocationCornerSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты'],
        summary="Удалить угол",
        description="Удаляет угол по ID.",
        responses={204: OpenApiResponse(description="Угол удалён")},
    ),
)
class LocationCornerViewSet(viewsets.ModelViewSet):
    queryset = LocationCorner.objects.all()
    serializer_class = LocationCornerSerializer


# =================================================================================================
# Связи
# =================================================================================================


@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты'],
        summary="Список связей",
        description="Возвращает список всех связей между локациями.",
        responses={200: ConnectionSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты'],
        summary="Получить связь по ID",
        description="Возвращает данные связи.",
        responses={200: ConnectionSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты'],
        summary="Создать связь",
        description="Создает новую связь между локациями.",
        responses={201: ConnectionSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты'],
        summary="Обновить связь",
        description="Полностью обновляет данные связи.",
        responses={200: ConnectionSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты'],
        summary="Частично обновить связь",
        description="Изменяет часть данных связи.",
        responses={200: ConnectionSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты'],
        summary="Удалить связь",
        description="Удаляет связь по ID.",
        responses={204: OpenApiResponse(description="Связь удалена")},
    ),
)
class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer


# =================================================================================================
# Маршруты
# =================================================================================================

@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты'],
        summary="Список маршрутов",
        description="Возвращает список всех маршрутов.",
        responses={200: RouteSerializer(many=True)}
    ),
    retrieve=extend_schema(
        tags=['Маршруты'],
        summary="Получить маршрут по ID",
        description="Возвращает детальную информацию о маршруте по ID.",
        responses={200: RouteSerializer, 404: OpenApiResponse(description="Маршрут не найден")}
    ),
    create=extend_schema(
        tags=['Маршруты'],
        summary="Создать маршрут",
        description="Создает новый маршрут.",
        responses={201: RouteSerializer}
    ),
    update=extend_schema(
        tags=['Маршруты'],
        summary="Обновить маршрут",
        description="Полностью обновляет данные маршрута.",
        responses={200: RouteSerializer, 404: OpenApiResponse(description="Маршрут не найден")}
    ),
    partial_update=extend_schema(
        tags=['Маршруты'],
        summary="Частично обновить маршрут",
        description="Изменяет часть данных маршрута.",
        responses={200: RouteSerializer, 404: OpenApiResponse(description="Маршрут не найден")}
    ),
    destroy=extend_schema(
        tags=['Маршруты'],
        summary="Удалить маршрут",
        description="Удаляет маршрут по ID.",
        responses={204: OpenApiResponse(description="Маршрут удалён"), 404: OpenApiResponse(description="Маршрут не найден")}
    ),
)
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsBotAuthenticated | IsAuthenticated]

    @extend_schema(
        tags=['Маршруты'],
        summary="Навигация по маршруту",
        description="Возвращает путь от начальной до конечной точки маршрута.",
        responses={
            200: LocationSerializer(many=True),
            404: OpenApiResponse(description="Путь не найден")
        }
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


# =================================================================================================
# Туры
# =================================================================================================

@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты'],
        summary="Список туров",
        description="Возвращает список всех туров.",
        responses={200: TourSerializer(many=True)}
    ),
    retrieve=extend_schema(
        tags=['Маршруты'],
        summary="Получить тур по ID",
        description="Возвращает детальную информацию о туре по ID.",
        responses={200: TourSerializer, 404: OpenApiResponse(description="Тур не найден")}
    ),
    create=extend_schema(
        tags=['Маршруты'],
        summary="Создать тур",
        description="Создает новый тур.",
        examples=[
            OpenApiExample(
                'Пример создания',
                value={
                    "name": "Тур по детским магазинам",
                    "image": None,
                    "description": "Краткое описание",
                    "full_description": "Полное описание",
                    "residents": [1]
                }
            )
        ],
        responses={201: TourSerializer}
    ),
    update=extend_schema(
        tags=['Маршруты'],
        summary="Обновить тур",
        description="Полностью обновляет данные тура.",
        responses={200: TourSerializer, 404: OpenApiResponse(description="Тур не найден")}
    ),
    partial_update=extend_schema(
        tags=['Маршруты'],
        summary="Частично обновить тур",
        description="Изменяет часть данных тура.",
        responses={200: TourSerializer, 404: OpenApiResponse(description="Тур не найден")}
    ),
    destroy=extend_schema(
        tags=['Маршруты'],
        summary="Удалить тур",
        description="Удаляет тур по ID.",
        responses={204: OpenApiResponse(description="Тур удалён"), 404: OpenApiResponse(description="Тур не найден")}
    ),
)
class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all().order_by('-created_at')
    serializer_class = TourSerializer
    permission_classes = [IsBotAuthenticated | IsAuthenticated]
