from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
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
