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
        tags=['Маршруты / Строения'],
        summary="Получить список зданий",
        description="Возвращает список всех зданий.",
        responses={200: BuildingSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты / Строения'],
        summary="Получить здание по ID",
        description="Возвращает информацию о конкретном здании.",
        responses={200: BuildingSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты / Строения'],
        summary="Создать здание",
        description="Добавляет новое здание.",
        responses={201: BuildingSerializer},
        examples=[OpenApiExample(
            'Пример',
            value={"name": "Главный корпус", "description": "Описание здания"}
        )]
    ),
    update=extend_schema(
        tags=['Маршруты / Строения'],
        summary="Обновить здание (PUT)",
        description="Полностью обновляет данные здания.",
        responses={200: BuildingSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты / Строения'],
        summary="Частично обновить здание (PATCH)",
        description="Изменяет часть данных здания.",
        responses={200: BuildingSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты / Строения'],
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


@extend_schema_view(
    list=extend_schema(
        tags=['Маршруты / Этажи'],
        summary="Получить список этажей",
        description="Возвращает список всех этажей.",
        responses={200: FloorSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты / Этажи'],
        summary="Получить этаж по ID",
        description="Возвращает информацию об этаже.",
        responses={200: FloorSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты / Этажи'],
        summary="Создать этаж",
        description="Добавляет новый этаж в здание.",
        responses={201: FloorSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты / Этажи'],
        summary="Обновить этаж (PUT)",
        description="Полностью обновляет данные этажа.",
        responses={200: FloorSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты / Этажи'],
        summary="Частично обновить этаж (PATCH)",
        description="Изменяет часть данных этажа.",
        responses={200: FloorSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты / Этажи'],
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
        tags=['Маршруты / Типы локаций'],
        summary="Получить список типов локаций",
        description="Возвращает список всех типов локаций.",
        responses={200: LocationTypeSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты / Типы локаций'],
        summary="Получить тип локации по ID",
        description="Возвращает информацию о типе локации.",
        responses={200: LocationTypeSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты / Типы локаций'],
        summary="Создать тип локации",
        description="Добавляет новый тип локации.",
        responses={201: LocationTypeSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты / Типы локаций'],
        summary="Обновить тип локации (PUT)",
        description="Полностью обновляет данные типа локации.",
        responses={200: LocationTypeSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты / Типы локаций'],
        summary="Частично обновить тип локации (PATCH)",
        description="Изменяет часть данных типа локации.",
        responses={200: LocationTypeSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты / Типы локаций'],
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
        tags=['Маршруты / Локации'],
        summary="Получить список локаций",
        description="Возвращает список всех локаций.",
        responses={200: LocationSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты / Локации'],
        summary="Получить локацию по ID",
        description="Возвращает информацию о конкретной локации.",
        responses={200: LocationSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты / Локации'],
        summary="Создать локацию",
        description="Добавляет новую локацию.",
        responses={201: LocationSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты / Локации'],
        summary="Обновить локацию (PUT)",
        description="Полностью обновляет данные локации.",
        responses={200: LocationSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты / Локации'],
        summary="Частично обновить локацию (PATCH)",
        description="Изменяет часть данных локации.",
        responses={200: LocationSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты / Локации'],
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
        tags=['Маршруты / Углы локации'],
        summary="Получить список углов",
        description="Возвращает список всех углов локаций.",
        responses={200: LocationCornerSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты / Углы локации'],
        summary="Получить угол по ID",
        description="Возвращает данные угла локации.",
        responses={200: LocationCornerSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты / Углы локации'],
        summary="Создать угол",
        description="Добавляет новый угол для локации.",
        responses={201: LocationCornerSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты / Углы локации'],
        summary="Обновить угол (PUT)",
        description="Полностью обновляет данные угла.",
        responses={200: LocationCornerSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты / Углы локации'],
        summary="Частично обновить угол (PATCH)",
        description="Изменяет часть данных угла.",
        responses={200: LocationCornerSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты / Углы локации'],
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
        tags=['Маршруты / Связи'],
        summary="Получить список связей",
        description="Возвращает список всех связей между локациями.",
        responses={200: ConnectionSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Маршруты / Связи'],
        summary="Получить связь по ID",
        description="Возвращает данные связи.",
        responses={200: ConnectionSerializer},
    ),
    create=extend_schema(
        tags=['Маршруты / Связи'],
        summary="Создать связь",
        description="Создает новую связь между локациями.",
        responses={201: ConnectionSerializer},
    ),
    update=extend_schema(
        tags=['Маршруты / Связи'],
        summary="Обновить связь (PUT)",
        description="Полностью обновляет данные связи.",
        responses={200: ConnectionSerializer},
    ),
    partial_update=extend_schema(
        tags=['Маршруты / Связи'],
        summary="Частично обновить связь (PATCH)",
        description="Изменяет часть данных связи.",
        responses={200: ConnectionSerializer},
    ),
    destroy=extend_schema(
        tags=['Маршруты / Связи'],
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
        tags=['Маршруты / Маршруты'],
        summary="Список маршрутов",
        description="Возвращает список всех маршрутов.",
        responses={200: RouteSerializer(many=True)}
    ),
    retrieve=extend_schema(
        tags=['Маршруты / Маршруты'],
        summary="Получить маршрут по ID",
        description="Возвращает детальную информацию о маршруте по ID.",
        responses={200: RouteSerializer, 404: OpenApiResponse(description="Маршрут не найден")}
    ),
    create=extend_schema(
        tags=['Маршруты / Маршруты'],
        summary="Создать маршрут",
        description="Создает новый маршрут.",
        responses={201: RouteSerializer}
    ),
    update=extend_schema(
        tags=['Маршруты / Маршруты'],
        summary="Обновить маршрут (PUT)",
        description="Полностью обновляет данные маршрута.",
        responses={200: RouteSerializer, 404: OpenApiResponse(description="Маршрут не найден")}
    ),
    partial_update=extend_schema(
        tags=['Маршруты / Маршруты'],
        summary="Частично обновить маршрут (PATCH)",
        description="Изменяет часть данных маршрута.",
        responses={200: RouteSerializer, 404: OpenApiResponse(description="Маршрут не найден")}
    ),
    destroy=extend_schema(
        tags=['Маршруты / Маршруты'],
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
        tags=['Маршруты / Маршруты'],
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
        tags=['Маршруты / Туры'],
        summary="Получить список туров",
        description="Возвращает список всех туров, отсортированных по дате создания (сначала новые).",
        responses={200: TourSerializer(many=True)}
    ),
    retrieve=extend_schema(
        tags=['Маршруты / Туры'],
        summary="Получить тур по ID",
        description="Возвращает детальную информацию о туре по ID.",
        responses={200: TourSerializer, 404: OpenApiResponse(description="Тур не найден")}
    ),
    create=extend_schema(
        tags=['Маршруты / Туры'],
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
                    "residents": [1]
                }
            )
        ],
        responses={201: TourSerializer}
    ),
    update=extend_schema(
        tags=['Маршруты / Туры'],
        summary="Обновить тур (PUT)",
        description="Полностью обновляет данные тура. Требуется авторизация.",
        responses={200: TourSerializer, 404: OpenApiResponse(description="Тур не найден")}
    ),
    partial_update=extend_schema(
        tags=['Маршруты / Туры'],
        summary="Частично обновить тур (PATCH)",
        description="Изменяет часть данных тура. Требуется авторизация.",
        responses={200: TourSerializer, 404: OpenApiResponse(description="Тур не найден")}
    ),
    destroy=extend_schema(
        tags=['Маршруты / Туры'],
        summary="Удалить тур",
        description="Удаляет тур по ID. Требуется авторизация.",
        responses={204: OpenApiResponse(description="Тур удалён"), 404: OpenApiResponse(description="Тур не найден")}
    ),
)
class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all().order_by('-created_at')
    serializer_class = TourSerializer
    permission_classes = [IsBotAuthenticated | IsAuthenticated]
