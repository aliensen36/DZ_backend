from django.urls import path
from rest_framework import routers
from . import views

mailing_app_router = routers.DefaultRouter()
mailing_app_router.register(r'mailings', views.MailingViewSet, basename='mailing')

urlpatterns = []