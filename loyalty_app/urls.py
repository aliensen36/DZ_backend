from django.urls import path
from rest_framework import routers
from .views import LoyaltyCardViewSet

loyalty_app_router = routers.DefaultRouter()
loyalty_app_router.register(r'loyalty-cards', LoyaltyCardViewSet, basename='loyalty-card')

urlpatterns = []
