from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import EventViewSet

event_app_router = routers.DefaultRouter()
event_app_router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(event_app_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)