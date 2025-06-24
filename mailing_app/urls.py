from django.urls import path
from rest_framework import routers
from . import views

mailing_app_router = routers.DefaultRouter()
mailing_app_router.register(r'mailings', views.MailingViewSet, basename='mailing')
mailing_app_router.register(r'admin/subscriptions', views.AdminSubscriptionViewSet, basename='admin-subscriptions')
mailing_app_router.register(r'subscriptions', views.UserSubscriptionViewSet, basename='user-subscriptions')

urlpatterns = []