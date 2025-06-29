from django.urls import path, include

from rest_framework.routers import DefaultRouter

from user_app.auth.views import *
from user_app.views import UserViewSet

user_app_router = DefaultRouter()
user_app_router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('design_admin/', AdminView.as_view(), name='admin'),
    path('resident/', ResidentView.as_view(), name='resident'),
]
