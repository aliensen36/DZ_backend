from django.urls import include, path
from rest_framework import routers
from .views import LoyaltyCardViewSet

router = routers.DefaultRouter()
router.register(r'loyalty-cards', LoyaltyCardViewSet, basename='loyalty-card')


urlpatterns = [
    path('', include(router.urls)),
]
