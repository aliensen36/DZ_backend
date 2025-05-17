from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from user_app.urls import router as user_app_router

router = routers.DefaultRouter()
router.registry.extend(user_app_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
