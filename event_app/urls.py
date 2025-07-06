from rest_framework import routers
from .views import EventViewSet

event_app_router = routers.DefaultRouter()
event_app_router.register(r'events', EventViewSet, basename='event')

urlpatterns = []