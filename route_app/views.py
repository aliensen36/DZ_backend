from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.decorators import action
from .navigation import find_shortest_path
from rest_framework import viewsets, status



from .models import (
    Building, Floor, LocationType, Location,
    LocationCorner, Connection, Route
)
from .serializers import (
    BuildingSerializer, FloorSerializer, LocationTypeSerializer,
    LocationSerializer, LocationCornerSerializer, ConnectionSerializer,
    RouteSerializer
)


@extend_schema(tags=['Buildings'])
class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


@extend_schema(tags=['Floors'])
class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer


@extend_schema(tags=['Location Types'])
class LocationTypeViewSet(viewsets.ModelViewSet):
    queryset = LocationType.objects.all()
    serializer_class = LocationTypeSerializer


@extend_schema(tags=['Locations'])
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


@extend_schema(tags=['Location Corners'])
class LocationCornerViewSet(viewsets.ModelViewSet):
    queryset = LocationCorner.objects.all()
    serializer_class = LocationCornerSerializer


@extend_schema(tags=['Connections'])
class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer


@extend_schema(tags=['Routes'])
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    @extend_schema(
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


