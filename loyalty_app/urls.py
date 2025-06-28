from django.urls import path, include
from rest_framework import routers
from .views import PointsTransactionViewSet, LoyaltyCardViewSet

loyalty_app_router = routers.DefaultRouter()
# loyalty_app_router.register(r'loyalty-cards', LoyaltyCardViewSet, basename='loyaltycard')
loyalty_app_router.register(r'points-transactions', PointsTransactionViewSet, basename='points-transactions')


urlpatterns = [
    path('loyalty-cards/<int:user__tg_id>/card-image/', LoyaltyCardViewSet.as_view({'get': 'loyalty_card_image'}),
         name='loyalty-card-image'),
    path('', include(loyalty_app_router.urls))
]
