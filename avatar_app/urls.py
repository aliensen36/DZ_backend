from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import AvatarViewSet, UserAvatarProgressViewSet

avatar_app_router = routers.DefaultRouter()
avatar_app_router.register(r'avatars', AvatarViewSet, basename='avatar')
avatar_app_router.register(r'avatars', UserAvatarProgressViewSet, basename='avatar-activate')

urlpatterns = [
    path('', include(avatar_app_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 