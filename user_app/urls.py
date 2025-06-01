from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import UserViewSet

user_app_router = DefaultRouter()
user_app_router.register(r'auth', views.AuthViewSet, basename='auth')
user_app_router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', views.home, name='home'),  # Временная стартовая страница
]
