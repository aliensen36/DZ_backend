
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from user_app.urls import user_app_router
from mailing_app.urls import mailing_app_router
from loyalty_app.urls import loyalty_app_router
from resident_app.urls import resident_app_router
from event_app.urls import event_app_router
from faq_app.urls import faq_app_router
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.registry.extend(user_app_router.registry)
router.registry.extend(mailing_app_router.registry)
router.registry.extend(loyalty_app_router.registry)
router.registry.extend(resident_app_router.registry)
router.registry.extend(event_app_router.registry)
router.registry.extend(faq_app_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('', include('user_app.urls')),
    # path('api/', include('user_app.urls')),
    path('api/', include('loyalty_app.urls')),
    path('api/', include('resident_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
