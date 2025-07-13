from django.urls import path
from rest_framework import routers
from .views import CategoryViewSet, ResidentViewSet, PinCodeVerifyView

resident_app_router = routers.DefaultRouter()
resident_app_router.register(r'categories', CategoryViewSet, basename='category')
resident_app_router.register(r'residents', ResidentViewSet, basename='resident')


urlpatterns = [
    path('verify-pin/', PinCodeVerifyView.as_view(), name='verify_pin'),
]