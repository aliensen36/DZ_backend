from rest_framework import routers

from .views import (
    QuestionTypeAdminViewSet,
    QuestionTypeUserViewSet,
    FAQAdminViewSet,
    FAQUserViewSet,
)

faq_app_router = routers.DefaultRouter()

# Админские эндпоинты
faq_app_router.register(r'admin/question-types', QuestionTypeAdminViewSet, basename='admin-question-type')
faq_app_router.register(r'admin/faqs', FAQAdminViewSet, basename='admin-faq')

# Пользовательские эндпоинты
faq_app_router.register(r'user/question-types', QuestionTypeUserViewSet, basename='user-question-type')
faq_app_router.register(r'user/faqs', FAQUserViewSet, basename='user-faq')