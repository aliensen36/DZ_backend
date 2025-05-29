from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from user_app.urls import router as user_app_router
from mailing_app.urls import router as mailing_app_router
from loyalty_app.urls import router as loyalty_app_router


router = routers.DefaultRouter()
router.registry.extend(user_app_router.registry)
router.registry.extend(mailing_app_router.registry)
router.registry.extend(loyalty_app_router.registry)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('user_app.urls')), # Временная стартовая страница
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
