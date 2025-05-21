from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'mailings', views.MailingViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # path('api/mailings/<int:pk>/send/', send_mailing, name='mailing-send'),
]
