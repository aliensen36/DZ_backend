from rest_framework import routers
from .views import LoyaltyCardViewSet, PointsTransactionViewSet

loyalty_app_router = routers.DefaultRouter()
loyalty_app_router.register(r'loyalty-cards', LoyaltyCardViewSet, basename='loyalty-card')
loyalty_app_router.register(r'points-transactions', PointsTransactionViewSet, basename='points-transactions')


urlpatterns = []
