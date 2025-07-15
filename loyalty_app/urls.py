from django.urls import path, include
from rest_framework import routers
from .views import PointsTransactionViewSet, LoyaltyCardViewSet, PromotionViewSet
from django.conf import settings
from django.conf.urls.static import static

loyalty_app_router = routers.DefaultRouter()
# loyalty_app_router.register(r'loyalty-cards', LoyaltyCardViewSet, basename='loyaltycard')
loyalty_app_router.register(r'points-transactions', PointsTransactionViewSet, basename='points-transactions')
loyalty_app_router.register(r'promotions', PromotionViewSet, basename='promotions')


urlpatterns = [
    path('loyalty-cards/<int:user__tg_id>/card-image/', LoyaltyCardViewSet.as_view({'get': 'loyalty_card_image'}),
         name='loyalty-card-image'),
    path('loyalty-cards/<int:user__tg_id>/card-number/', LoyaltyCardViewSet.as_view({'get': 'card_number'}),
         name='loyalty-card-number'),
    path('loyalty-cards/card-number/<str:card_number>/', LoyaltyCardViewSet.as_view({'get': 'get_by_card_number'}),
         name='loyalty-card-by-number'),
    path('loyalty-cards/<int:user__tg_id>/card-id/', LoyaltyCardViewSet.as_view({'get': 'card_id'}),
         name='loyalty-card-id'),
    path('loyalty-cards/card-number/<str:card_number>/', LoyaltyCardViewSet.as_view({'get': 'get_by_card_number'}),
         name='loyalty-card-by-number'),
    path('', include(loyalty_app_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
