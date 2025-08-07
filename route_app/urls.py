from django.urls import path
from rest_framework import routers

from .floor_plan_preview import floor_plan_preview
from .views import *

route_app_router = routers.DefaultRouter()
route_app_router.register(r'buildings', BuildingViewSet, basename='building')
route_app_router.register(r'floors', FloorViewSet, basename='floor')
route_app_router.register(r'locations', LocationViewSet, basename='location')
route_app_router.register(r'location-types', LocationTypeViewSet, basename='location-type')
route_app_router.register(r'location-corners', LocationCornerViewSet, basename='location-corner')
route_app_router.register(r'connections', ConnectionViewSet, basename='connection')
route_app_router.register(r'routes', RouteViewSet, basename='route')
route_app_router.register(r'tours', TourViewSet, basename='tour')


urlpatterns = [
    path('floors/<int:pk>/plan/', floor_plan_preview, name='floor_plan_preview'),
]