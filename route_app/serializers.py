from rest_framework import serializers
from .models import (
    Building, Floor, LocationType, Location,
    LocationCorner, Connection, Route
)


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name', 'description']


class FloorSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    building_id = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all(),
        source='building',
        write_only=True
    )

    class Meta:
        model = Floor
        fields = ['id', 'number', 'building', 'building_id']


class LocationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationType
        fields = ['id', 'name']


class LocationCornerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationCorner
        fields = ['id', 'x', 'y', 'order']


class LocationSerializer(serializers.ModelSerializer):
    floor = FloorSerializer(read_only=True)
    floor_id = serializers.PrimaryKeyRelatedField(
        queryset=Floor.objects.all(),
        source='floor',
        write_only=True
    )
    location_type = LocationTypeSerializer(read_only=True)
    location_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LocationType.objects.all(),
        source='location_type',
        write_only=True,
        allow_null=True
    )
    corners = LocationCornerSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'name',
            'floor', 'floor_id',
            'location_type', 'location_type_id',
            'corners',
        ]


class ConnectionSerializer(serializers.ModelSerializer):
    from_location = LocationSerializer(read_only=True)
    from_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='from_location',
        write_only=True
    )
    to_location = LocationSerializer(read_only=True)
    to_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='to_location',
        write_only=True
    )

    class Meta:
        model = Connection
        fields = [
            'id',
            'from_location', 'from_location_id',
            'to_location', 'to_location_id',
            'bidirectional', 'cost'
        ]


class RouteSerializer(serializers.ModelSerializer):
    start_location = LocationSerializer(read_only=True)
    start_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='start_location',
        write_only=True
    )
    end_location = LocationSerializer(read_only=True)
    end_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='end_location',
        write_only=True
    )

    class Meta:
        model = Route
        fields = [
            'id', 'name',
            'start_location', 'start_location_id',
            'end_location', 'end_location_id'
        ]
