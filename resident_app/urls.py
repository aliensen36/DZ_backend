from rest_framework import routers
from .views import ResidentViewSet

resident_app_router = routers.DefaultRouter()
resident_app_router.register(r'residents', ResidentViewSet, basename='resident')

urlpatterns = []